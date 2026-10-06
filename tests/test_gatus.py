import httpx
import pytest
from gatus_tray.backends.gatus import GatusClient, GatusError
from gatus_tray.monitor import overall_state
from gatus_tray.models import EndpointStatus, OverallState

def test_latest_result_and_nanoseconds(monkeypatch):
    def request(*a, **kw): return httpx.Response(200, json=[{"name":"x","group":"g","key":"k","results":[{"success":False},{"success":True,"status":200,"hostname":"h","duration":66260548,"timestamp":"t"}]}])
    monkeypatch.setattr(httpx, "get", request)
    result = GatusClient("http://x").fetch_statuses()[0]
    assert result.success and result.response_time_ms == pytest.approx(66.260548)

def test_empty_results_are_ignored(monkeypatch):
    monkeypatch.setattr(httpx, "get", lambda *a, **k: httpx.Response(200, json=[{"name":"x","results":[]}]))
    assert GatusClient("http://x").fetch_statuses() == []

def test_http_errors_are_wrapped(monkeypatch):
    monkeypatch.setattr(httpx, "get", lambda *a, **k: (_ for _ in ()).throw(httpx.ConnectError("no")))
    with pytest.raises(GatusError): GatusClient("http://x").fetch_statuses()

def test_overall_state():
    assert overall_state([]) is OverallState.UNKNOWN
    e = EndpointStatus("x","g","k",None,False,None,None,None,{})
    assert overall_state([e]) is OverallState.DOWN

