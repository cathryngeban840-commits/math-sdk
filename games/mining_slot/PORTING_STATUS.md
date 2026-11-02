# Native SDK port status

**Status: integration workspace created; native game implementation and SDK validation are not yet complete.**

The fork and development branch are available. The SDK sample interfaces were inspected in:
- games/0_0_ways/game_config.py
- games/0_0_ways/gamestate.py
- games/0_0_ways/game_executables.py
- games/0_0_ways/run.py
- games/0_0_expwilds/game_executables.py

## Implementation work still required
1. Add Mining Slot reel CSVs and a config using the SDK's exact config/distribution interfaces.
2. Implement all-ways evaluation and win event emission.
3. Implement full-reel expansion as a single reel-level state (not the sample's per-position expanding Wild).
4. Carry triggering-spin expanded reels into free spins and keep them sticky through the feature.
5. Implement the three mutually exclusive Scatter tiers, retriggers, and multiplier progression.
6. Enforce the 15,000× cap over the entire round, including all free spins.
7. Add deterministic feature-state tests and SDK event/schema tests.
8. Run the SDK book generation, optimizer, analytics, and RGS verification workflow.

## Acceptance gates
- Python import and lint checks pass.
- Unit tests cover every feature transition and cap edge case.
- SDK book generation completes for base and feature modes.
- Optimization converges to a documented measured RTP; 96% is not assumed.
- Independent analytics and RGS verification pass.
- Generated configuration and lookup assets are reviewed before release.

## Important
No SDK build, optimizer run, RGS test, or RTP certification is claimed by this commit. SDK sample code is a reference, not proof that Mining Slot is already integrated.
