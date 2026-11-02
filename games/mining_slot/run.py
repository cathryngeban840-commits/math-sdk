"""Native Stake Math SDK workflow for Mining Slot. Run from repository root."""
from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":
    num_threads, rust_threads, batching_size = 8, 8, 50000
    compression, profiling = True, False
    num_sim_args = {"base": int(1e4)}
    target_modes = ["base"]
    config = GameConfig()
    gamestate = GameState(config)
    OptimizationSetup(config)
    create_books(gamestate, config, num_sim_args, batching_size,
                 num_threads, compression, profiling)
    generate_configs(gamestate)
    OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
    generate_configs(gamestate)
    create_stat_sheet(gamestate, custom_keys=[{"symbol": "scatter"}])
    execute_all_tests(config)
