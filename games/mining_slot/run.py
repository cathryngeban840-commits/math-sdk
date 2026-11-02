"""Native SDK unbiased RTP measurement and RGS verification for Mining Slot."""
from gamestate import GameState
from game_config import GameConfig
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":
    # One million ordinary base rounds, sampled from the configured reel strips.
    # No optimizer/forced criteria are used in this measurement pass.
    num_threads, rust_threads, batching_size = 8, 8, 50000
    compression, profiling = True, False
    num_sim_args = {"base": 1_000_000}
    config = GameConfig()
    gamestate = GameState(config)

    create_books(
        gamestate, config, num_sim_args, batching_size,
        num_threads, compression, profiling
    )
    generate_configs(gamestate)
    create_stat_sheet(gamestate, custom_keys=[{"symbol": "scatter"}])
    execute_all_tests(config)
