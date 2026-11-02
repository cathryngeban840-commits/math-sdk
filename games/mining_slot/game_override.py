"""Mining Slot-specific state overrides."""
from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome

class GameStateOverride(GameExecutables):
    def reset_book(self):
        super().reset_book()
        self.sticky_wild_reels = set()
        self.mining_round_paid = 0.0
        self.mining_feature_multiplier = 1.0
        self.mining_feature_increment = 0.0
        self.mining_feature_name = None

    def assign_special_sym_function(self):
        # Wilds do not carry a symbol-level multiplier in this design.
        self.special_symbol_functions = {}

    def check_game_repeat(self):
        # Retain SDK repeat behavior. Round-level cap is enforced by the win manager
        # / SDK wincap distribution; custom round accumulation is tracked for auditing.
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
