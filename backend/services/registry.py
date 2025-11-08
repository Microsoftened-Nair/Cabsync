"""Registry for platform-specific integrations."""
from __future__ import annotations

from typing import Dict, Protocol

from models.ride import RideRequest, RideResult
from platforms.ola import OlaProvider
from platforms.rapido import RapidoProvider
from platforms.uber import UberProvider
from platforms.namma_yatri import NammaYatriProvider


class PlatformProvider(Protocol):
    def fetch_quotes(self, request: RideRequest) -> list[RideResult]:
        raise NotImplementedError


def build_platform_registry() -> Dict[str, PlatformProvider]:
    return {
        "ola": OlaProvider(),
        "uber": UberProvider(),
        "rapido": RapidoProvider(),
        "namma_yatri": NammaYatriProvider(),
    }
