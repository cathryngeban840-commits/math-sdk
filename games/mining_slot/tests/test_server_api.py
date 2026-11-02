"""Exercise the local HTTP adapter used by the Mining Slot browser demo."""
import json
from threading import Thread
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer

import games.mining_slot.server as server_module


def run_server():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server_module.Handler)
    thread = Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, thread, f"http://127.0.0.1:{httpd.server_address[1]}"


def test_health_endpoint_reports_sdk_connection():
    httpd, thread, base = run_server()
    try:
        with urlopen(base + "/health") as response:
            payload = json.loads(response.read())
            assert response.status == 200
            assert payload == {
                "ok": True,
                "engine": "stake-math-sdk",
                "game": "mining_slot",
            }
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)


def test_spin_endpoint_validates_bet_and_returns_sdk_outcome(monkeypatch):
    expected = {
        "id": "test-round",
        "payoutMultiplier": 2.5,
        "baseGameWins": 2.5,
        "freeGameWins": 0,
        "events": [{"type": "reveal", "board": [[{"name": "9"}] * 7] * 6},
                   {"type": "finalWin", "amount": 250}],
        "game": "mining_slot",
        "engine": "stake-math-sdk",
    }
    monkeypatch.setattr(server_module, "play_sdk_round", lambda seed=None: dict(expected))
    httpd, thread, base = run_server()
    try:
        invalid = Request(
            base + "/api/spin",
            data=json.dumps({"bet": 0.01}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urlopen(invalid)
            assert False, "Invalid bet should be rejected"
        except HTTPError as error:
            assert error.code == 400
            assert "between 0.10 and 1,000" in json.loads(error.read())["error"]

        valid = Request(
            base + "/api/spin",
            data=json.dumps({"bet": 2, "seed": 123}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(valid) as response:
            payload = json.loads(response.read())
            assert response.status == 200
            assert payload["engine"] == "stake-math-sdk"
            assert payload["bet"] == 2
            assert payload["winAmount"] == 5
            assert payload["events"] == expected["events"]
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)
