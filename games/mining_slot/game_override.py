"""Mining Slot-specific state overrides."""
from game_executables import GameExecutables
from src.events.events import reveal_event

class GameStateOverride(GameExecutables):
    def reset_book(self):
        super().reset_book()
        # Clear only between independent outcome attempts; this method is not called
        # between free spins, so the feature's expanded reels remain sticky.
        self.sticky_wild_reels = set()
        self.mining_feature_multiplier = 1.0
        self.mining_feature_increment = 0.0
        self.mining_feature_name = None

    def draw_board(self, emit_event=True, trigger_symbol="scatter"):
        """Draw natural boards without the SDK anti-scatter reroll."""
        self.create_board_reelstrips()
        if emit_event:
            reveal_event(self)

    def check_freespin_entry(self, scatter_key="scatter"):
        """Allow naturally landed scatters to start paid-round features."""
        return self.count_scatters() >= min(self.config.freespin_triggers[self.gametype].keys())

    def assign_special_sym_function(self):
        self.special_symbol_functions = {}

    def check_game_repeat(self):
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
