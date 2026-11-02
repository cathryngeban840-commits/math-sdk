"""Mining Slot optimization setup.

The values below are starting optimization constraints, not measured RTP.
The SDK optimizer must determine the final outcome distribution.
"""
from optimization_program.optimization_config import (
    ConstructScaling, ConstructParameters, ConstructConditions,
    ConstructFenceBias, verify_optimization_input,
)

class OptimizationSetup:
    def __init__(self, game_config):
        self.game_config = game_config
        cap = game_config.wincap
        game_config.opt_params = {
            "base": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.001, av_win=cap, search_conditions=cap
                    ).return_dict(),
                    "0": ConstructConditions(
                        rtp=0.0, av_win=0, search_conditions=0
                    ).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.359, hr=150, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "basegame": ConstructConditions(
                        rtp=0.60, hr=3.0
                    ).return_dict(),
                },
                "scaling": ConstructScaling([
                    {"criteria": "basegame", "scale_factor": 1.15,
                     "win_range": (1, 5), "probability": 1.0},
                    {"criteria": "basegame", "scale_factor": 1.25,
                     "win_range": (10, 30), "probability": 1.0},
                    {"criteria": "freegame", "scale_factor": 0.85,
                     "win_range": (100, 500), "probability": 1.0},
                    {"criteria": "freegame", "scale_factor": 1.1,
                     "win_range": (1000, 3000), "probability": 1.0},
                ]).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000, num_per_fence=10000,
                    min_m2m=4, max_m2m=8, pmb_rtp=1.0,
                    sim_trials=5000, test_spins=[50, 100, 200],
                    test_weights=[0.3, 0.4, 0.3], score_type="rtp",
                ).return_dict(),
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["basegame"],
                    bias_ranges=[(1.5, 3.5)], bias_weights=[0.4],
                ).return_dict(),
            }
        }
        verify_optimization_input(game_config, game_config.opt_params)
