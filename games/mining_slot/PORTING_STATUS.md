# Native SDK port status

**Status: initial native SDK game files and provisional reel strips have been committed. SDK execution and certification are still pending.**

## Implemented in this branch
- 6-reel × 5-row configuration and 15,625 maximum positional ways.
- Provisional base-game and free-game reel strips (BR0 / FR0).
- Provisional paytable mapped to the SDK's `(reel_count, symbol)` paytable convention.
- Dedicated SDK game configuration, game-state, calculation, override, executable, and run modules.
- Explicit left-to-right all-ways evaluator, including fully-Wild first-reel handling.
- Full-reel Wild expansion and sticky reel tracking, including triggering-spin carry-over.
- Three Scatter award tiers and retrigger trigger map.
- Feature multiplier progression applied to free-spin win evaluation.
- Independent standard-library reference rules module and unit tests.

## Not yet verified / remaining work
1. Run the game inside the exact SDK environment and fix any interface/import mismatches.
2. Confirm the SDK's scatter-entry and retrigger lifecycle against the implemented tier map.
3. Verify the feature multiplier and sticky reel state across SDK's reset / free-spin lifecycle.
4. Enforce and test the 15,000× cap across the *entire* bonus round, not just individual spin evaluation. The configured SDK win cap is not proof of round-wide cap semantics.
5. Add deterministic integration tests using SDK Symbol objects and emitted event payloads.
6. Generate outcome books, run optimizer, generate analytics, and pass RGS format verification.
7. Optimize reel strips and paytable to a measured RTP near 96%; the current strips and paytable are provisional and unbalanced.
8. Review volatility, bonus frequency, max-win frequency, and edge cases before considering Bonus Buy.

## Important
No SDK workflow, optimizer, RGS test, or RTP certification is claimed by this commit. The SDK's Python environment requires Python 3.12 or newer; the optimizer's Rust component requires Cargo. Run `python games/mining_slot/run.py` from the game directory after installing the repository's dependencies, or adapt the invocation to the SDK's launcher conventions.
