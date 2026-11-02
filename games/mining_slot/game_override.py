"""Mining Slot-specific state overrides."""
from game_executables import GameExecutables
from src.events.events import reveal_event, fs_trigger_event


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

    def _scatter_tier_count(self):
        """Map every 5+ Scatter result to the Deep Mine Jackpot tier."""
        count = self.count_scatters()
        return min(count, max(self.config.freespin_triggers[self.gametype]))

    def check_fs_condition(self, scatter_key="scatter"):
        """Use the current board for feature and retrigger scatter checks."""
        return self.count_scatters() >= min(self.config.freespin_triggers[self.gametype]) and not self.repeat

    def check_freespin_entry(self, scatter_key="scatter"):
        """Allow naturally landed scatters to start paid-round features."""
        return self.count_scatters() >= min(self.config.freespin_triggers[self.gametype])

    def update_freespin_amount(self, scatter_key="scatter"):
        """Award initial feature spins from the actual scatter count."""
        count = self._scatter_tier_count()
        self.tot_fs = self.config.freespin_triggers[self.gametype][count]
        fs_trigger_event(self, basegame_trigger=(self.gametype == self.config.basegame_type),
                         freegame_trigger=(self.gametype != self.config.basegame_type))

    def update_fs_retrigger_amt(self, scatter_key="scatter"):
        """Award retriggers; 5 or more Scatters always use the top tier."""
        count = self._scatter_tier_count()
        self.tot_fs += self.config.freespin_triggers[self.gametype][count]
        fs_trigger_event(self, freegame_trigger=True, basegame_trigger=False)

    def assign_special_sym_function(self):
        self.special_symbol_functions = {}

    def check_game_repeat(self):
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
