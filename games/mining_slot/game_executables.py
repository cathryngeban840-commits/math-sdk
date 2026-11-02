"""SDK event/evaluation adapter for Mining Slot."""
from game_calculations import GameCalculations
from src.calculations.ways import Ways

class GameExecutables(GameCalculations):
    def expand_wild_reels(self):
        """Expand every reel containing a Wild to five Wild symbols."""
        if not hasattr(self, "sticky_wild_reels"):
            self.sticky_wild_reels = set()
        current = {r for r, reel in enumerate(self.board) if any(s.name == "W" for s in reel)}
        current |= set(self.sticky_wild_reels) if self.gametype == self.config.freegame_type else set()
        for reel in current:
            for row in range(self.config.num_rows[reel]):
                self.board[reel][row] = self.create_symbol("W")
        # Capture triggering-spin expansions for the first free spin.
        self.sticky_wild_reels |= current
        return current

    def evaluate_ways_board(self):
        self.expand_wild_reels()
        feature_mult = self.mining_feature_multiplier if self.gametype == self.config.freegame_type else 1.0
        self.win_data = Ways.get_ways_data(
            self.config, self.board,
            global_multiplier=feature_mult,
            multiplier_strategy="global",
        )
        if self.win_data["totalWin"] > 0:
            Ways.record_ways_wins(self)
            self.win_manager.update_spinwin(self.win_data["totalWin"])
        Ways.emit_wayswin_events(self)

    def count_scatters(self):
        return sum(1 for reel in self.board for symbol in reel if symbol.name == "S")
