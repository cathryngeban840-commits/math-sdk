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
    os.makedirs(os.path.join("games", config.game_id, "library"), exist_ok=True)
    # Runs lookup precision, book/LUT payout consistency, RTP, volatility,
    # and Studio submission-limit checks without the SDK's optional XLSX report.
    execute_all_tests(config)
    # Emit the exact aggregate values from the same RGS lookup-table analysis
    # so CI logs retain the measured RTP and risk metrics for every calibration.
    summary_path = os.path.join("games", config.game_id, "library", "stats_summary.json")
    with open(summary_path, "r", encoding="UTF-8") as summary_file:
        summary = json.load(summary_file)
    for mode_name, stats in summary.items():
        print(
            f"MINING_SLOT_FINAL_STATS mode={mode_name} "
            f"rtp={stats.get('rtp')} std={stats.get('std')} "
            f"cvar={stats.get('cvar')} cvar_abs={stats.get('cvar_abs')} "
            f"norm_etl40={stats.get('norm_etl40')} "
            f"norm_etl10k={stats.get('norm_etl10k')} "
            f"sum_etl={stats.get('sum_etl')} max_win={stats.get('max_win')}"
        )
