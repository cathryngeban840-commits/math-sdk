"""Local HTTP adapter exposing real Mining Slot SDK outcomes to the browser demo.

Run from the repository root:
    python games/mining_slot/server.py
The endpoint is for local development only. It has no wallet, account, payment,
or production RGS integration.
"""
from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
GAME_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(GAME_DIR))
os.chdir(ROOT)

from game_config import GameConfig
from gamestate import GameState

HOST, PORT = "127.0.0.1", 8787
_config = GameConfig()


def play_sdk_round(seed: int | None = None) -> dict:
    """Generate one complete round using the configured Stake SDK game state."""
    state = GameState(_config)
    state.betmode = "base"
    state.criteria = "basegame"
    state.run_spin(sim=0 if seed is None else int(seed), simulation_seed=seed)
    book = state.book.to_json()
    return {
        "id": book.get("id"),
        "payoutMultiplier": book.get("payoutMultiplier", 0),
        "baseGameWins": book.get("baseGameWins", 0),
        "freeGameWins": book.get("freeGameWins", 0),
        "events": book.get("events", []),
        "game": "mining_slot",
        "engine": "stake-math-sdk",
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "MiningSlotSDK/0.1"

    def _send(self, status: int, payload: dict):
        body = json.dumps(payload, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:8787")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            return self._send(200, {"ok": True, "engine": "stake-math-sdk", "game": "mining_slot"})
        # Serve demo UI and explicitly allowlisted art files only; never expose repository paths.
        assets = {
            "/demo/": (GAME_DIR / "demo" / "index.html", "text/html; charset=utf-8"),
            "/demo/index.html": (GAME_DIR / "demo" / "index.html", "text/html; charset=utf-8"),
            "/demo/app.js": (GAME_DIR / "demo" / "app.js", "text/javascript; charset=utf-8"),
        }
        # Symbol and bonus art are served from fixed subdirectories with a strict filename allowlist.
        art_names = {
            "miner.png", "cart.png", "gold.png", "purple.png", "blue.png",
            "red.png", "green.png", "pickaxe.png", "lantern.png", "a.png",
            "k.png", "q.png", "j.png", "10.png", "9.png", "w.png", "scatter.png",
        }
        bonus_names = {"gold_rush.png", "crystal_cavern.png", "deep_mine_jackpot.png"}
        if path.startswith("/demo/assets/symbols/"):
            name = path.rsplit("/", 1)[-1]
            if name in art_names:
                assets[path] = (GAME_DIR / "demo" / "assets" / "symbols" / name, "image/png")
        elif path.startswith("/demo/assets/bonus/"):
            name = path.rsplit("/", 1)[-1]
            if name in bonus_names:
                assets[path] = (GAME_DIR / "demo" / "assets" / "bonus" / name, "image/png")
        asset = assets.get(path)
        if asset is None:
            return self._send(404, {"error": "Not found"})
        file_path, content_type = asset
        try:
            body = file_path.read_bytes()
        except OSError:
            return self._send(404, {"error": "Demo asset not found"})
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if urlparse(self.path).path != "/api/spin":
            return self._send(404, {"error": "Not found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 2048:
                return self._send(413, {"error": "Request too large"})
            request = json.loads(self.rfile.read(length) or b"{}")
            bet = float(request.get("bet", 1))
            if not (0.1 <= bet <= 1000):
                return self._send(400, {"error": "Bet must be between 0.10 and 1,000."})
            seed = request.get("seed")
            outcome = play_sdk_round(seed)
            outcome["bet"] = bet
            outcome["winAmount"] = round(float(outcome["payoutMultiplier"]) * bet, 2)
            return self._send(200, outcome)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            return self._send(400, {"error": str(exc)})
        except Exception as exc:
            return self._send(500, {"error": "SDK round failed", "detail": str(exc)})

    def log_message(self, fmt, *args):
        print("[mining-slot-api] " + fmt % args)


if __name__ == "__main__":
    print(f"Mining Slot SDK API listening at http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
