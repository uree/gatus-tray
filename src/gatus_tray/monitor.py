import logging
import threading
from collections.abc import Callable

from gatus_tray.backends.gatus import GatusClient, GatusError
from gatus_tray.models import EndpointStatus, OverallState

log = logging.getLogger(__name__)

def overall_state(endpoints: list[EndpointStatus]) -> OverallState:
    if not endpoints: return OverallState.UNKNOWN
    return OverallState.DOWN if any(not e.success for e in endpoints) else OverallState.UP

class Monitor:
    def __init__(
        self,
        client: GatusClient,
        interval: float,
        callback: Callable[[OverallState, list[EndpointStatus], str | None], None],
    ):
        self.client, self.interval, self.callback = client, interval, callback
        self.previous: dict[str, bool] = {}
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self):
        self._thread = threading.Thread(
            target=self._run, name="gatus-monitor", daemon=True
        )
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _run(self):
        while not self._stop.is_set():
            try:
                endpoints = self.client.fetch_statuses()
                state = overall_state(endpoints)
                self.callback(state, endpoints, None)
                self.previous = {e.key: e.success for e in endpoints}
            except GatusError as exc:
                log.warning("%s", exc)
                self.callback(OverallState.UNKNOWN, [], str(exc))
            self._stop.wait(self.interval)

