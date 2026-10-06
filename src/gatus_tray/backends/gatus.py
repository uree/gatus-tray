from typing import Any
import httpx
from gatus_tray.models import GatusCheckResult, GatusEndpoint, EndpointStatus

class GatusError(RuntimeError): pass

class GatusClient:
    def __init__(self, base_url: str, timeout: float = 10): self.base_url, self.timeout = base_url.rstrip("/"), timeout
    def fetch_statuses(self) -> list[EndpointStatus]:
        try:
            response = httpx.get(f"{self.base_url}/api/v1/endpoints/statuses", timeout=self.timeout)
            response.raise_for_status(); payload = response.json()
        except (httpx.HTTPError, ValueError) as exc: raise GatusError(f"Gatus request failed: {exc}") from exc
        if not isinstance(payload, list): raise GatusError("Gatus returned a non-list status payload")
        statuses = []
        for item in payload:
            if not isinstance(item, dict): continue
            results = [self._result(x) for x in item.get("results", []) if isinstance(x, dict)]
            if not results: continue
            latest = results[-1]
            statuses.append(EndpointStatus(str(item.get("name", "")), str(item.get("group", "")), str(item.get("key", "")), latest.hostname, latest.success, latest.status, latest.response_time_ms, latest.timestamp, item))
        return statuses
    @staticmethod
    def _result(raw: dict[str, Any]) -> GatusCheckResult:
        duration = raw.get("duration")
        return GatusCheckResult(raw.get("status"), raw.get("hostname"), int(duration) if isinstance(duration, (int, float)) else None, bool(raw.get("success", False)), raw.get("timestamp"), raw)

