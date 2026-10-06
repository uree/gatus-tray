from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

class OverallState(str, Enum):
    UP = "up"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class GatusCheckResult:
    status: int | None
    hostname: str | None
    duration_ns: int | None
    success: bool
    timestamp: str | None
    raw: dict[str, Any]

    @property
    def response_time_ms(self) -> float | None:
        return self.duration_ns / 1_000_000 if self.duration_ns is not None else None

@dataclass(frozen=True)
class GatusEndpoint:
    name: str
    group: str
    key: str
    results: tuple[GatusCheckResult, ...]
    raw: dict[str, Any]

@dataclass(frozen=True)
class EndpointStatus:
    name: str
    group: str
    key: str
    hostname: str | None
    success: bool
    http_status: int | None
    response_time_ms: float | None
    timestamp: str | None
    raw: dict[str, Any]

