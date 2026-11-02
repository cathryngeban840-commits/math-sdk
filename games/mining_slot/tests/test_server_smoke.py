"""Smoke-test one real SDK-generated Mining Slot round."""
from server import play_sdk_round


def test_sdk_round_has_reveal_and_final_payout():
    result = play_sdk_round(seed=20261102)
    assert result["engine"] == "stake-math-sdk"
    assert result["game"] == "mining_slot"
    assert isinstance(result["events"], list) and result["events"]
    reveals = [event for event in result["events"] if event.get("type") == "reveal"]
    assert reveals, "SDK round did not emit a reel reveal"
    assert len(reveals[0]["board"]) == 6
    assert all(len(reel) == 7 for reel in reveals[0]["board"]), "Expected 5 visible rows plus padding"
    finals = [event for event in result["events"] if event.get("type") == "finalWin"]
    assert len(finals) == 1, "SDK round must emit exactly one finalWin event"
    assert result["payoutMultiplier"] >= 0
    assert finals[0]["amount"] >= 0
