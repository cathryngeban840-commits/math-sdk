# Mining Slot — integration and validation status

**Status: SDK-connected development build validated; production integration is not complete.**

## Implemented
- 6 reels × 5 rows; 15,625 positional ways, left-to-right from reel 1.
- Native SDK game configuration, state, executable, override, and run modules.
- Expanding Wild: any landed Wild expands its full reel to five Wilds.
- Expanded Wild reels from the triggering base spin carry into the feature and remain sticky through free spins.
- Scatter is trigger-only, does not pay, and is not substituted by Wild.
- 3 Scatters: Gold Rush — 10 free spins, 1.00× starting multiplier, no increment.
- 4 Scatters: Crystal Cavern — 12 free spins, 1.00× starting multiplier, +0.25× after each spin.
- 5–30 Scatters: Deep Mine Jackpot — 15 free spins, 1.00× starting multiplier, +0.50× after each spin.
- Feature retriggers preserve multiplier progression; feature spin budget is capped at 30 and multiplier at 5×.
- A round-wide 15,000× initiating-bet cap is enforced across base and free-game wins.
- SDK event-driven browser demo, local HTTP adapter, and deterministic reference/API tests.
- Bonus Buy remains disabled until its separate price and feature math are designed and validated.

## Latest SDK validation (2026-11-02)
The GitHub Actions SDK validation generated 1,000,000 outcome books for the base mode and reported:
- Measured RTP: **96.24%** (target range: 96.00–96.70%).
- Standard deviation: **57.849**.
- CVaR: **683.51**.
- SDK risk checks: **6 of 6 passed**.
- Verification sidecar: SHA-256 and payout hash passed.
- Reference tests: **21 passed**.
- Browser/API smoke tests: **24 passed**.
- SDK round smoke and full SDK validation workflows: **passed**.

This is a reproducible development simulation result for the current configuration. It is not an independent laboratory certification, legal review, production security assessment, or Stake approval. Re-run the complete math workflow after any reel-strip, paytable, or feature-rule change.

## Local demo
From the repository root:

```bash
pip install -r requirements.txt
python games/mining_slot/server.py
```

Open http://127.0.0.1:8787/demo/. The browser requests outcomes from the Python SDK adapter; it does not generate symbols or calculate game payouts itself. The balance is simulated demo credit only.

## Remaining before real-money / Stake release
1. Complete formal game-math review and independent certification with the target jurisdiction / platform.
2. Port the outcome flow into the required production RGS / Stake Engine runtime and verify the exact integration contract.
3. Replace the local development HTTP adapter with an authenticated, hardened production service; connect approved wallet/session/account systems only through the platform's approved interfaces.
4. Complete client asset/audio integration, responsive-device QA, accessibility, and cross-browser testing.
5. Complete operational, security, monitoring, responsible-gaming, and legal/compliance reviews.
6. Design and validate Bonus Buy separately before enabling it.

The local adapter binds to 127.0.0.1 and is intentionally a development tool, not a production server.
