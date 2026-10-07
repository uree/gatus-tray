import httpx  # noqa: F401
import pytest  # noqa: F401

from gatus_tray.backends.gatus import GatusClient, GatusError  # noqa: F401
from gatus_tray.models import EndpointStatus, OverallState
from gatus_tray.monitor import overall_state


# This test file is more of a placeholder for future tests, if ever needed.
def test_overall_state():
    assert overall_state([]) is OverallState.UNKNOWN
    e = EndpointStatus("x", "g", "k", None, False, None, None, None, {})
    assert overall_state([e]) is OverallState.DOWN
