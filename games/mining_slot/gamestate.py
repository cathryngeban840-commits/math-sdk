"""Mining Slot game-state integration."""
from game_override import GameStateOverride

class GameState(GameStateOverride):
    def run_spin(self, sim: int, simulation_seed=None) -> None:
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board(emit_event=True)
            self.evaluate_ways_board()
            scatter_total = self.count_scatters()
            if scatter_total >= 3 and self.check_freespin_entry():
                # Select tier from actual scatter count. The SDK's trigger map supplies
                # awarded spins; the multiplier progression is managed below.
                if scatter_total == 3:
                    self.mining_feature_name, self.mining_feature_increment = "Gold Rush", 0.0
                elif scatter_total == 4:
                    self.mining_feature_name, self.mining_feature_increment = "Crystal Cavern", 0.25
                else:
                    self.mining_feature_name, self.mining_feature_increment = "Deep Mine Jackpot", 0.50
                self.mining_feature_multiplier = 1.0
                self.run_freespin_from_base()
            self.evaluate_finalwin()
            self.check_repeat()
        self.imprint_wins()

    def run_freespin(self) -> None:
        self.reset_fs_spin()
        while self.fs < self.tot_fs:
            self.update_freespin()
            self.draw_board(emit_event=True)
            # evaluate_ways_board applies the sticky expanded reels before scoring.
            self.evaluate_ways_board()
            scatter_total = self.count_scatters()
            if scatter_total >= 3:
                self.update_fs_retrigger_amt()
            self.win_manager.update_gametype_wins(self.gametype)
            self.mining_feature_multiplier += self.mining_feature_increment
        self.end_freespin()
