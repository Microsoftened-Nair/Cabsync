"""Core aggregation logic that orchestrates provider integrations."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
import logging
from typing import Dict, List

from fastapi import HTTPException

from models.ride import CompareResponse, ResponseMeta, RideRequest, RideResult
from services.registry import PlatformProvider


logger = logging.getLogger(__name__)


class RideAggregator:
    """Combine quotes across modular provider integrations."""

    def __init__(self, registry: Dict[str, PlatformProvider]):
        self._registry = registry

    def list_platforms(self) -> List[str]:
        return sorted(self._registry.keys())

    def get_timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def compare(self, request: RideRequest) -> CompareResponse:
        results: List[RideResult] = []
        failed: List[str] = []

        for key, provider in self._registry.items():
            try:
                quotes = provider.fetch_quotes(request)
                results.extend(quotes)
            except HTTPException as exc:
                logger.warning("Provider %s returned error: %s", key, exc.detail)
                failed.append(key)
            except Exception as exc:  # pragma: no cover - provider safeguard
                logger.exception("Provider %s raised unexpected error", key)
                failed.append(key)

        results.sort(key=lambda quote: (quote.price.value, quote.eta.seconds, quote.provider))

        if not results and failed:
            raise HTTPException(status_code=503, detail="All providers failed to respond")

        meta = ResponseMeta(
            queried_at=datetime.now(timezone.utc).isoformat(),
            cache_key=self._build_cache_key(request),
            total_providers=len(self._registry),
            failed_providers=failed,
        )

        return CompareResponse(results=results, meta=meta)

    def _build_cache_key(self, request: RideRequest) -> str:
        base = (
            f"{request.pickup.lat:.3f}:{request.pickup.lng:.3f}:"
            f"{request.dropoff.lat:.3f}:{request.dropoff.lng:.3f}:"
            f"{(request.vehicle_type or 'any').lower()}"
        )
        digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]
        return f"cabsync_{digest}"
