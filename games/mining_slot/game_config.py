"""Stake Math SDK configuration for Mining Slot."""
import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode

class GameConfig(Config):
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "mining_slot"
        self.provider_number = 0
        self.working_name = "Mining Slot"
        self.wincap = 15000
        self.mining_max_feature_spins = 30
        self.mining_max_feature_multiplier = 5.0
        self.win_type = "ways"
        self.rtp = 0.96  # target only; optimizer must establish measured RTP
        # First measured pass landed at 10.46% RTP; scale provisional awards
        # toward target while preserving symbol/reel frequency relationships.
        self.mining_paytable_scale = 9.18
        self.construct_paths()
        self.num_reels = 6
        self.num_rows = [5] * 6
        # Payouts are total-bet multipliers. SDK ways paytable uses (reel_count, symbol).
        raw = {
            "MINER": (5,15,50,200), "CART": (4,12,40,150),
            "GOLD": (3,10,30,100), "PURPLE": (2,7,20,75),
            "BLUE": (2,6,18,60), "RED": (1.5,5,15,50),
            "GREEN": (1,4,12,40), "PICKAXE": (.8,3,9,30),
            "LANTERN": (.6,2,6,20), "A": (.4,1.5,5,15),
            "K": (.4,1.4,4.5,13), "Q": (.35,1.2,4,12),
            "J": (.3,1,3.5,10), "10": (.25,.9,3,9),
            "9": (.2,.8,2.5,8)
        }
        self.paytable = {}
        for symbol, pays in raw.items():
            for reels, payout in zip((3,4,5,6), pays):
                self.paytable[(reels, symbol)] = payout
        self.include_padding = True
        self.special_symbols = {"wild": ["W"], "scatter": ["S"], "multiplier": []}
        self.freespin_triggers = {
            self.basegame_type: {3: 10, 4: 12, 5: 15, 6: 15},
            self.freegame_type: {3: 10, 4: 12, 5: 15, 6: 15},
        }
        self.anticipation_triggers = {self.basegame_type: 2, self.freegame_type: 2}
        self.reels = {
            "BR0": self.read_reels_csv(os.path.join(self.reels_path, "BR0.csv")),
            "FR0": self.read_reels_csv(os.path.join(self.reels_path, "FR0.csv")),
        }
        # Unbiased natural-spin sample: every round uses the ordinary reel strips.
        # Do not force scatters, free games, zero wins, or max-win outcomes during RTP measurement.
        self.bet_modes = [
            BetMode(
                name="base", cost=1.0, rtp=self.rtp, max_win=self.wincap,
                auto_close_disabled=False, is_feature=False, is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="basegame", quota=1.0,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            )
        ]
