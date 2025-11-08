"""Namma Yatri provider using Beckn protocol for real-time fare estimation."""
from __future__ import annotations

import asyncio
import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
import threading

import httpx
from fastapi import HTTPException

from models.ride import (
    Eta,
    Price,
    RideRequest,
    RideResult,
    RideMeta,
    TransactionState,
    TransactionStatus,
    transaction_store,
)

logger = logging.getLogger(__name__)


@dataclass
class BecknContext:
    """Beckn protocol context for request routing and identification."""
    
    domain: str = "mobility"
    country: str = "IND"
    city: str = "std:080"  # Bangalore
    action: str = "search"
    version: str = "1.1.0"
    bap_id: str = "cabsync.app"
    bap_uri: str = "https://cabsync.app/beckn"
    transaction_id: str = ""
    message_id: str = ""
    timestamp: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "domain": self.domain,
            "country": self.country,
            "city": self.city,
            "action": self.action,
            "version": self.version,
            "bap_id": self.bap_id,
            "bap_uri": self.bap_uri,
            "transaction_id": self.transaction_id,
            "message_id": self.message_id,
            "timestamp": self.timestamp,
        }


class BecknClient:
    """
    Beckn protocol client for Namma Yatri integration.
    
    Implements the Beckn mobility API for ride discovery and fare estimation.
    Note: This is a simplified implementation focusing on the search flow.
    """
    
    def __init__(self, gateway_url: str, timeout: float = 10.0):
        self.gateway_url = gateway_url
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
    
    def _create_context(self, action: str, bap_uri: Optional[str] = None) -> BecknContext:
        """Create a Beckn context with unique identifiers."""
        context = BecknContext(
            action=action,
            transaction_id=str(uuid.uuid4()),
            message_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        
        # Override BAP URI if provided (for callback endpoint)
        if bap_uri:
            context.bap_uri = bap_uri
        
        return context
    
    async def search(
        self,
        pickup_lat: float,
        pickup_lng: float,
        dropoff_lat: float,
        dropoff_lng: float,
        bap_uri: Optional[str] = None,
    ) -> str:
        """
        Send a Beckn search request to discover available rides.
        
        Args:
            pickup_lat: Pickup latitude
            pickup_lng: Pickup longitude
            dropoff_lat: Dropoff latitude
            dropoff_lng: Dropoff longitude
            bap_uri: BAP callback URI for receiving on_search responses
            
        Returns:
            Transaction ID for correlating async callbacks
        """
        context = self._create_context("search", bap_uri)
        
        # Beckn search request payload
        payload = {
            "context": context.to_dict(),
            "message": {
                "intent": {
                    "fulfillment": {
                        "start": {
                            "location": {
                                "gps": f"{pickup_lat},{pickup_lng}"
                            }
                        },
                        "end": {
                            "location": {
                                "gps": f"{dropoff_lat},{dropoff_lng}"
                            }
                        }
                    }
                }
            }
        }
        
        try:
            # Send search request to Beckn gateway
            response = await self._client.post(
                f"{self.gateway_url}/search",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                logger.warning(
                    f"Beckn search request failed: {response.status_code} - {response.text}"
                )
                return ""
            
            # Beckn gateway returns ACK immediately, actual results come via callback
            ack_data = response.json()
            logger.info(f"Beckn search ACK received for transaction {context.transaction_id}")
            
            return context.transaction_id
            
        except httpx.RequestError as exc:
            logger.error(f"Beckn gateway request failed: {exc}")
            return ""
        except Exception as exc:
            logger.exception("Unexpected error in Beckn search")
            return ""


class NammaYatriProvider:
    """
    Namma Yatri provider using Beckn protocol.
    
    Currently configured for discovery mode. Full integration requires:
    1. Beckn gateway endpoint
    2. Callback URL implementation for on_search, on_select, etc.
    3. Provider registration in Beckn registry
    """
    
    provider_id = "namma_yatri"
    provider_name = "Namma Yatri"
    
    def __init__(self, beckn_gateway_url: Optional[str] = None):
        # Use environment variable or default to a sandbox gateway
        self.gateway_url = beckn_gateway_url or os.getenv(
            "BECKN_GATEWAY_URL",
            "https://gateway.beckn.nsdl.co.in"  # Example gateway
        )
        self.enabled = os.getenv("NAMMA_YATRI_ENABLED", "false").lower() == "true"
        self.bap_uri = os.getenv("BAP_URI", "http://localhost:8000/api/beckn")
        self._client: Optional[BecknClient] = None
    
    async def _get_client(self) -> BecknClient:
        """Get or create Beckn client."""
        if not self._client:
            self._client = BecknClient(self.gateway_url)
        return self._client
    
    def fetch_quotes(self, request: RideRequest) -> List[RideResult]:
        """
        Fetch ride quotes from Namma Yatri via Beckn protocol.
        
        This initiates an async Beckn search and returns immediately.
        Actual results arrive later via the /api/beckn/on_search callback.
        """
        if not self.enabled:
            raise HTTPException(
                status_code=501,
                detail="Namma Yatri integration is disabled. Set NAMMA_YATRI_ENABLED=true to enable."
            )
        
        try:
            # Run async code in a separate thread to avoid event loop conflicts
            def run_beckn_search():
                # Create new event loop in this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Get Beckn client
                    if not self._client:
                        self._client = BecknClient(self.gateway_url)
                    
                    # Send Beckn search request
                    transaction_id = loop.run_until_complete(
                        self._client.search(
                            pickup_lat=request.pickup.lat,
                            pickup_lng=request.pickup.lng,
                            dropoff_lat=request.dropoff.lat,
                            dropoff_lng=request.dropoff.lng,
                            bap_uri=self.bap_uri,
                        )
                    )
                    
                    return transaction_id
                finally:
                    loop.close()
            
            # Execute in thread pool
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_beckn_search)
                transaction_id = future.result(timeout=10)
            
            if not transaction_id:
                logger.error("Failed to initiate Beckn search")
                raise HTTPException(
                    status_code=503,
                    detail="Failed to connect to Namma Yatri via Beckn gateway"
                )
            
            # Store transaction state for callback correlation
            state = TransactionState(
                transaction_id=transaction_id,
                request=request,
                status=TransactionStatus.PENDING,
            )
            transaction_store[transaction_id] = state
            
            logger.info(f"Beckn search initiated with transaction_id: {transaction_id}")
            
            # Wait briefly for callback (with timeout)
            import time
            max_wait = 5.0  # seconds
            wait_interval = 0.2
            elapsed = 0.0
            
            while elapsed < max_wait:
                time.sleep(wait_interval)
                elapsed += wait_interval
                
                # Check if callback received
                if state.status == TransactionStatus.COMPLETED:
                    logger.info(f"Received {len(state.results)} results from Namma Yatri")
                    return state.results
                elif state.status == TransactionStatus.FAILED:
                    logger.error(f"Beckn search failed: {state.error}")
                    raise HTTPException(status_code=503, detail=state.error or "Beckn search failed")
            
            # Timeout - no callback received
            state.status = TransactionStatus.TIMEOUT
            logger.warning(f"Beckn search timeout for transaction {transaction_id}")
            
            # Return empty results on timeout (callback may still arrive later)
            return []
            
        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("Unexpected error in Namma Yatri fetch_quotes")
            raise HTTPException(
                status_code=500,
                detail=f"Namma Yatri integration error: {str(exc)}"
            )
