"""Mining Slot base-game and free-spin state machine."""
from game_override import GameStateOverride

class GameState(GameStateOverride):
    def run_spin(self, sim: int, simulation_seed=None) -> None:
        self.reset_seed(sim, simulation_seed)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board(emit_event=True)
            self.evaluate_ways_board()
            self.win_manager.update_gametype_wins(self.gametype)
            if self.check_fs_condition() and self.check_freespin_entry():
                scatter_total = self.count_scatters()
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
        while self.fs < self.tot_fs and not self.wincap_triggered:
            self.update_freespin()
            self.draw_board(emit_event=True)
            self.evaluate_ways_board()
            if self.check_fs_condition():
                self.update_fs_retrigger_amt()
            self.win_manager.update_gametype_wins(self.gametype)
            self.mining_feature_multiplier += self.mining_feature_increment
            # evaluate_ways_board calls evaluate_wincap; the loop exits on the
            # next condition check once the round-wide SDK win manager reaches cap.
        self.end_freespin()
