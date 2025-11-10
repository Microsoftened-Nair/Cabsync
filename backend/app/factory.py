"""Application factory for the Cabsync backend."""
from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Dict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models.ride import (
    CompareResponse,
    RideRequest,
    BecknCallback,
    transaction_store,
    TransactionStatus,
    RideResult,
    Price,
    Eta,
    cabsync,
)
from services.aggregator import RideAggregator
from services.registry import build_platform_registry

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    load_dotenv()

    app = FastAPI(
        title="Cabsync API",
        description="Aggregate ride options from modular provider integrations",
        version=os.getenv("CABSYNC_API_VERSION", "2.0.0"),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    aggregator = RideAggregator(build_platform_registry())

    @app.get("/")
    async def root() -> Dict[str, object]:
        registry = aggregator.list_platforms()
        return {
            "message": "Cabsync API",
            "version": app.version,
            "providers": registry,
        }

    @app.get("/api/health")
    async def health_check() -> Dict[str, object]:
        return {
            "status": "healthy",
            "timestamp": aggregator.get_timestamp(),
            "providers": aggregator.list_platforms(),
        }

    @app.post("/api/compare", response_model=CompareResponse, response_model_by_alias=True)
    async def compare_rides(request: RideRequest) -> CompareResponse:
        try:
            return aggregator.compare(request)
        except HTTPException:
            raise
        except Exception as exc:  # pragma: no cover - defensive catch-all
            logger.exception("Unexpected error while comparing rides")
            raise HTTPException(status_code=500, detail="Failed to compare rides") from exc

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.status_code, "message": exc.detail}},
        )

    @app.post("/api/beckn/on_search")
    async def beckn_on_search(callback: BecknCallback) -> Dict[str, Dict[str, Dict[str, str]]]:
        """
        Beckn protocol callback endpoint for search responses.
        Called asynchronously by the Beckn Gateway after search request.
        """
        try:
            transaction_id = callback.context.get("transaction_id")
            
            if not transaction_id:
                logger.error("Received callback without transaction_id")
                return {"message": {"ack": {"status": "NACK"}}}
            
            # Check if we have this transaction
            if transaction_id not in transaction_store:
                logger.warning(f"Unknown transaction_id: {transaction_id}")
                return {"message": {"ack": {"status": "NACK"}}}
            
            state = transaction_store[transaction_id]
            
            # Handle error responses
            if callback.error:
                state.status = TransactionStatus.FAILED
                state.error = callback.error.get("message", "Unknown error")
                logger.error(f"Beckn error for {transaction_id}: {state.error}")
                return {"message": {"ack": {"status": "ACK"}}}
            
            # Parse catalog and convert to RideResult objects
            catalog = callback.message.get("catalog", {})
            providers = catalog.get("providers", [])
            
            results = []
            for provider in providers:
                items = provider.get("items", [])
                for item in items:
                    try:
                        # Extract price
                        price_data = item.get("price", {})
                        price_value = float(price_data.get("value", 0))
                        
                        # Extract ETA from fulfillment
                        fulfillment = item.get("fulfillment", {})
                        eta_state = fulfillment.get("state", {})
                        eta_descriptor = eta_state.get("descriptor", {})
                        eta_text = eta_descriptor.get("name", "Unknown")
                        
                        # Parse ETA seconds (e.g., "ETA 5 mins" -> 300 seconds)
                        eta_seconds = 300  # Default
                        if "min" in eta_text.lower():
                            try:
                                minutes = int(''.join(filter(str.isdigit, eta_text)))
                                eta_seconds = minutes * 60
                            except ValueError:
                                pass
                        
                        # Extract vehicle type
                        descriptor = item.get("descriptor", {})
                        service_name = descriptor.get("name", "Auto Rickshaw")
                        
                        # Create RideResult
                        result = RideResult(
                            provider="namma_yatri",
                            service_type=service_name,
                            price=Price(value=price_value, currency="₹", confidence=1.0),
                            eta=Eta(seconds=eta_seconds, text=eta_text),
                            distance=0,  # Not provided in callback
                            deep_link=f"nammayatri://ride/{item.get('id', '')}",
                            meta=cabsync(
                                vehicle_capacity=3 if "auto" in service_name.lower() else 4,
                                rating=4.5,  # Default rating
                                co2_estimate=0.12,
                            )
                        )
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Error parsing Beckn item: {e}")
                        continue
            
            # Update transaction state
            state.results = results
            state.status = TransactionStatus.COMPLETED
            state.callback_received_at = datetime.now()
            
            logger.info(f"Processed {len(results)} results for transaction {transaction_id}")
            
            return {"message": {"ack": {"status": "ACK"}}}
            
        except Exception as e:
            logger.exception(f"Error processing Beckn callback: {e}")
            return {"message": {"ack": {"status": "NACK"}}}

    return app
