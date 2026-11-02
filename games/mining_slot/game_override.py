"""Mining Slot-specific state overrides."""
from game_executables import GameExecutables

class GameStateOverride(GameExecutables):
    def reset_book(self):
        super().reset_book()
        # Clear only between independent outcome attempts; this method is not called
        # between free spins, so the feature's expanded reels remain sticky.
        self.sticky_wild_reels = set()
        self.mining_feature_multiplier = 1.0
        self.mining_feature_increment = 0.0
        self.mining_feature_name = None

    def check_freespin_entry(self, scatter_key="scatter"):
        """Natural scatters trigger features in ordinary paid rounds."""
        return len(self.special_syms_on_board.get(scatter_key, [])) >= min(
            self.config.freespin_triggers[self.gametype].keys()
        )

    def assign_special_sym_function(self):
        self.special_symbol_functions = {}

    def check_game_repeat(self):
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
