"""Native SDK unbiased RTP measurement and RGS verification for Mining Slot."""
from gamestate import GameState
from game_config import GameConfig
from src.state.run_sims import create_books
from utils.rgs_verification import execute_all_tests
import os

if __name__ == "__main__":
    # One million ordinary base rounds, sampled from the configured reel strips.
    # Natural scatter triggers are enabled in GameStateOverride.
    num_threads, batching_size = 8, 50000
    compression, profiling = True, False
    num_sim_args = {"base": 1_000_000}
    config = GameConfig()
    gamestate = GameState(config)

    create_books(
        gamestate, config, num_sim_args, batching_size,
        num_threads, compression, profiling
    )
    # The verifier writes its summary into this directory.
    os.makedirs(os.path.join(config.game_path, "library"), exist_ok=True)
    # Runs lookup precision, book/LUT payout consistency, RTP, volatility,
    # and Studio submission-limit checks without the SDK's optional XLSX report.
    execute_all_tests(config)
