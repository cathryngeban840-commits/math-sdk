import unittest

from src.wins.win_manager import WinManager


class WinManagerRoundCapTests(unittest.TestCase):
    def test_base_and_free_wins_share_one_round_cap(self):
        manager = WinManager("basegame", "freegame", 15000.0)
        manager.basegame_wins = 12000.0
        manager.freegame_wins = 9000.0

        manager.update_end_round_wins()

        self.assertAlmostEqual(manager.total_cumulative_wins, 15000.0)
        self.assertAlmostEqual(manager.cumulative_base_wins, 15000.0 * 12000.0 / 21000.0)
        self.assertAlmostEqual(manager.cumulative_free_wins, 15000.0 * 9000.0 / 21000.0)
        self.assertAlmostEqual(
            manager.cumulative_base_wins + manager.cumulative_free_wins,
            15000.0,
        )

    def test_round_below_cap_is_not_scaled(self):
        manager = WinManager("basegame", "freegame", 15000.0)
        manager.basegame_wins = 100.0
        manager.freegame_wins = 250.0

        manager.update_end_round_wins()

        self.assertEqual(manager.total_cumulative_wins, 350.0)
        self.assertEqual(manager.cumulative_base_wins, 100.0)
        self.assertEqual(manager.cumulative_free_wins, 250.0)

    def test_base_only_round_is_capped(self):
        manager = WinManager("basegame", "freegame", 15000.0)
        manager.basegame_wins = 18000.0

        manager.update_end_round_wins()

        self.assertEqual(manager.total_cumulative_wins, 15000.0)
        self.assertEqual(manager.cumulative_base_wins, 15000.0)
        self.assertEqual(manager.cumulative_free_wins, 0.0)


if __name__ == "__main__":
    unittest.main()
