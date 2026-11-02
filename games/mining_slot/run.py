"""Run the native Stake Math SDK workflow for Mining Slot.

Run from the SDK repository root with its environment installed.
"""
from gamestate import GameState
from game_config import GameConfig
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":
    config = GameConfig()
    gamestate = GameState(config)
    num_threads, rust_threads, batching_size = 8, 8, 50000
    compression, profiling = True, False
    num_sim_args = {"base": int(1e5)}
    run_sims = True
    run_optimization = True
    run_analysis = True
    run_format_checks = True
    target_modes = ["base"]

    if run_sims:
        create_books(gamestate, config, num_sim_args, batching_size,
                     num_threads, compression, profiling)
    generate_configs(gamestate)
    if run_optimization:
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        generate_configs(gamestate)
    if run_analysis:
        create_stat_sheet(gamestate, custom_keys=[{"symbol": "scatter"}])
    if run_format_checks:
        execute_all_tests(config)
