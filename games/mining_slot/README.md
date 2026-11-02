# Mining Slot — SDK integration workspace

This folder is the dedicated integration workspace for the 6×5 Mining Slot project. It is separate from the SDK's upstream examples.

## Current design
- 6 reels × 5 rows; left-to-right all-ways wins, starting on reel 1.
- Expanding Wild: any Wild on a reel converts all five positions on that reel to Wild.
- Wilds may land on reel 1.
- Sticky expanded reels persist for the full free-spin feature.
- Expanded Wild reels from the triggering base-game spin carry into the feature.
- Scatter is trigger-only and is not a paying symbol.
- 3 Scatters: Gold Rush, 10 free spins, +0.00× feature multiplier per spin.
- 4 Scatters: Crystal Cavern, 12 free spins, +0.25× feature multiplier per spin.
- 5 or 6 Scatters: Deep Mine Jackpot, 15 free spins, +0.50× feature multiplier per spin.
- Retriggers are enabled; multiplier progression is retained through retriggers.
- Total round cap: 15,000× initiating bet across the base trigger and complete feature.
- Bonus Buy is deferred until base/feature math is calibrated and validated.

## Math status
Latest SDK simulation (2026-11-02): measured RTP 96.24%, within the 96.00–96.70% target; 6/6 SDK risk checks passed; configured round cap is 15,000×. Reference-rule tests and SDK validation workflow passed. This is a successful development validation run, not independent certification or Stake approval. Re-run the full simulation after any math, reel-strip, or feature-rule change.

## Porting approach
Use the SDK's 0_0_ways game as the all-ways foundation and 0_0_expwilds only as a behavioral reference. The latter is not a drop-in implementation: Mining Slot expands an entire reel and carries full expanded reels into free spins. That behavior needs a dedicated state representation and tests.

See PORTING_STATUS.md and game_spec.json.

## SDK-connected local browser demo

The browser client now requests each round from the Python SDK adapter; it does not generate its own symbols or calculate payouts locally.

From the repository root, install the project's dependencies and start the adapter:

```bash
pip install -r requirements.txt
python games/mining_slot/server.py
```

Then open [http://127.0.0.1:8787/demo/](http://127.0.0.1:8787/demo/). The local API exposes `GET /health`, `POST /api/spin`, and the two demo assets. The browser renders the SDK's `reveal`, feature trigger/retrigger, win, and final payout events. The displayed balance is simulated demo credit only.

This is a local development adapter, not a production Remote Gaming Server (RGS), wallet, account, or Stake deployment. Python's built-in HTTP server is intended for development and is not production-hardened. Re-run SDK tests and math validation after any outcome or feature changes.
