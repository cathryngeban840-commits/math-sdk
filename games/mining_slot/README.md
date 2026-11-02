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

## Browser prototype
Open [`demo/index.html`](demo/index.html) for the playable visual prototype. It includes a 6×5 reel display, adjustable demo bet, spin and auto-spin controls, rules/paytable panel, feature-tier presentation, expanding/sticky Wild visuals, and demo balance. The browser prototype uses local randomized outcomes for UI testing; it is **not connected to the calibrated SDK math engine** and must not be used to represent the measured RTP or real-money outcomes.
