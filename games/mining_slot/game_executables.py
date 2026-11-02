"""SDK event/evaluation adapter for Mining Slot."""
from game_calculations import GameCalculations
from src.calculations.ways import Ways

class GameExecutables(GameCalculations):
    def expand_wild_reels(self):
        """Expand every reel containing a Wild; retain expanded reels in free spins."""
        if not hasattr(self, "sticky_wild_reels"):
            self.sticky_wild_reels = set()
        current = {r for r, reel in enumerate(self.board) if any(s.name == "W" for s in reel)}
        if self.gametype == self.config.freegame_type:
            current |= set(self.sticky_wild_reels)
        for reel in current:
            for row in range(self.config.num_rows[reel]):
                self.board[reel][row] = self.symbol_storage.create_symbol("W")
        self.sticky_wild_reels |= current
        return current

    def evaluate_ways_board(self):
        """Evaluate all left-to-right symbol ways; Scatter never substitutes."""
        self.expand_wild_reels()
        multiplier = self.mining_feature_multiplier if self.gametype == self.config.freegame_type else 1.0
        wins, total = [], 0.0
        for symbol in self.config.paying_symbol_names:
            ways, kind, positions = 1, 0, []
            for reel_index, reel in enumerate(self.board):
                matching = [{"reel": reel_index, "row": row}
                            for row, item in enumerate(reel)
                            if item.name == symbol or item.name == "W"]
                if not matching:
                    break
                kind += 1
                ways *= len(matching)
                positions.extend(matching)
            if kind >= 3 and (kind, symbol) in self.config.paytable:
                raw = self.config.paytable[(kind, symbol)] * ways
                paid = round(raw * multiplier, 2)
                if paid:
                    wins.append({"symbol": symbol, "kind": kind, "win": paid,
                                 "positions": positions,
                                 "meta": {"ways": ways, "globalMult": multiplier,
                                          "winWithoutMult": raw, "symbolMult": 0}})
                    total += paid
        self.win_data = {"totalWin": round(total, 2), "wins": wins}
        if self.win_data["totalWin"] > 0:
            Ways.record_ways_wins(self)
            self.win_manager.update_spinwin(self.win_data["totalWin"])
        Ways.emit_wayswin_events(self)

    def count_scatters(self):
        return sum(1 for reel in self.board for symbol in reel if symbol.name == "S")
