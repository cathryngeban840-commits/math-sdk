import unittest
from game_logic import (
    WILD, SCATTER, PAYTABLE, evaluate_ways, expand_wild_reels,
    scatter_count, bonus_for_scatter, start_feature, RoundState,
    play_feature_spin, ROUND_CAP,
)

def board(symbol="9"):
    return [[symbol for _ in range(5)] for _ in range(6)]

class MiningRulesTests(unittest.TestCase):
    def test_dimensions_checked(self):
        with self.assertRaises(ValueError):
            evaluate_ways([["9"]])

    def test_all_ways_multiplicity(self):
        b = board("MINER")
        result = evaluate_ways(b)
        self.assertEqual(result["totalWin"], PAYTABLE["MINER"][6] * (5 ** 6))

    def test_left_to_right_stops_at_first_empty_reel(self):
        b = board("MINER")
        b[2] = ["9"] * 5
        self.assertEqual(evaluate_ways(b)["totalWin"], 0)

    def test_wild_substitution_and_expansion(self):
        b = board("MINER")
        b[0][0] = WILD
        expanded, reels = expand_wild_reels(b)
        self.assertEqual(reels, (0,))
        self.assertEqual(expanded[0], [WILD] * 5)
        result = evaluate_ways(expanded)
        self.assertEqual(result["totalWin"], PAYTABLE["MINER"][6] * (5 ** 6))

    def test_scatter_not_substitute_or_pay(self):
        b = board("MINER")
        b[0] = [SCATTER] * 5
        result = evaluate_ways(b)
        self.assertEqual(result["totalWin"], 0)
        self.assertEqual(scatter_count(b), 5)

    def test_bonus_tiers(self):
        self.assertEqual(bonus_for_scatter(3), ("Gold Rush", 10, 0.0))
        self.assertEqual(bonus_for_scatter(4), ("Crystal Cavern", 12, 0.25))
        self.assertEqual(bonus_for_scatter(5), ("Deep Mine Jackpot", 15, 0.5))
        self.assertIsNone(bonus_for_scatter(2))

    def test_triggering_wild_reels_carry_into_feature(self):
        b = board("9")
        b[1][0] = WILD
        state, expanded = start_feature(b, 3)
        self.assertIn(1, state.sticky_reels)
        self.assertEqual(expanded[1], [WILD] * 5)

    def test_retrigger_keeps_multiplier_progress(self):
        b = board("9")
        fs = start_feature(b, 4)[0]
        fs.multiplier = 2.25
        fs.add_retrigger(5)
        self.assertEqual(fs.multiplier, 2.25)
        self.assertEqual(fs.spins_remaining, 27)

    def test_round_cap_is_shared_across_feature(self):
        rs = RoundState(bet=1)
        rs.record(ROUND_CAP - 2)
        paid = rs.record(10)
        self.assertEqual(paid, 2)
        self.assertTrue(rs.capped)

    def test_sticky_reels_remain_expanded(self):
        fs = start_feature(board("9"), 3)[0]
        fs.sticky_reels.add(4)
        rs = RoundState(bet=1)
        b = board("9")
        result = play_feature_spin(fs, b, rs)
        self.assertEqual(b[4], ["9"] * 5)
        self.assertIn(4, fs.sticky_reels)
        self.assertEqual(result["expanded_reels"], [4])

if __name__ == "__main__":
    unittest.main()
