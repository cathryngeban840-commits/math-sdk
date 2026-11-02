"""Deterministic rules core for Mining Slot.

Board convention: board[reel][row], zero-based indices. Payouts are total-bet
multipliers. This module is deliberately independent of SDK internals so its
feature rules can be unit-tested before wiring to SDK events/outcome books.
"""
from dataclasses import dataclass, field
from itertools import product
from typing import Iterable

REELS, ROWS = 6, 5
WILD, SCATTER = "W", "S"
ROUND_CAP = 15000.0

PAYTABLE = {
    "MINER": {3: 5, 4: 15, 5: 50, 6: 200},
    "CART": {3: 4, 4: 12, 5: 40, 6: 150},
    "GOLD": {3: 3, 4: 10, 5: 30, 6: 100},
    "PURPLE": {3: 2, 4: 7, 5: 20, 6: 75},
    "BLUE": {3: 2, 4: 6, 5: 18, 6: 60},
    "RED": {3: 1.5, 4: 5, 5: 15, 6: 50},
    "GREEN": {3: 1, 4: 4, 5: 12, 6: 40},
    "PICKAXE": {3: .8, 4: 3, 5: 9, 6: 30},
    "LANTERN": {3: .6, 4: 2, 5: 6, 6: 20},
    "A": {3: .4, 4: 1.5, 5: 5, 6: 15},
    "K": {3: .4, 4: 1.4, 5: 4.5, 6: 13},
    "Q": {3: .35, 4: 1.2, 5: 4, 6: 12},
    "J": {3: .3, 4: 1, 5: 3.5, 6: 10},
    "10": {3: .25, 4: .9, 5: 3, 6: 9},
    "9": {3: .2, 4: .8, 5: 2.5, 6: 8},
}
BONUS_TIERS = {
    3: ("Gold Rush", 10, 0.0),
    4: ("Crystal Cavern", 12, 0.25),
    5: ("Deep Mine Jackpot", 15, 0.50),
    6: ("Deep Mine Jackpot", 15, 0.50),
}

def validate_board(board):
    if len(board) != REELS or any(len(reel) != ROWS for reel in board):
        raise ValueError("Board must be 6 reels by 5 rows (board[reel][row]).")
    allowed = set(PAYTABLE) | {WILD, SCATTER}
    bad = {s for reel in board for s in reel if s not in allowed}
    if bad:
        raise ValueError(f"Unknown symbols: {sorted(bad)}")

def expand_wild_reels(board, sticky_reels: Iterable[int] = ()):
    """Return copied board and sorted reels expanded by natural or sticky Wild."""
    validate_board(board)
    expanded = {i for i, reel in enumerate(board) if WILD in reel}
    expanded.update(sticky_reels)
    if any(i < 0 or i >= REELS for i in expanded):
        raise ValueError("Sticky reel index outside 0..5.")
    out = [list(reel) for reel in board]
    for i in expanded:
        out[i] = [WILD] * ROWS
    return out, tuple(sorted(expanded))

def evaluate_ways(board, bet=1.0, multiplier=1.0, cap=ROUND_CAP):
    """Evaluate left-to-right all-ways wins; one payout per symbol and length."""
    validate_board(board)
    if bet < 0 or multiplier < 0 or cap < 0:
        raise ValueError("bet, multiplier and cap must be non-negative.")
    wins, total = [], 0.0
    for symbol, pays in PAYTABLE.items():
        ways, length = 1, 0
        for reel in board:
            count = sum(s == symbol or s == WILD for s in reel)
            if count == 0:
                break
            ways *= count
            length += 1
        if length >= 3:
            # Match the SDK adapter: configured awards are total-bet payouts
            # at five positions per reel, so normalize ways by 5**reels.
            # Each individual award is rounded to the RGS tenth-bet precision.
            amount = round((pays[length] * ways / (5 ** length)) * bet * multiplier, 1)
            if amount:
                wins.append({"symbol": symbol, "reels": length, "ways": ways, "payout": amount})
                total += amount
    # The SDK clamps the final paid round to its configured win cap.
    return {"totalWin": round(min(total, cap * bet), 1), "wins": wins}

def scatter_count(board):
    validate_board(board)
    return sum(s == SCATTER for reel in board for s in reel)

def bonus_for_scatter(count):
    """Three and four Scatters select their tiers; every 5+ result selects top tier."""
    if count >= 5:
        return BONUS_TIERS[5]
    return BONUS_TIERS.get(count)

@dataclass
class FeatureState:
    name: str
    spins_remaining: int
    multiplier: float
    multiplier_increment: float
    sticky_reels: set[int] = field(default_factory=set)
    total_feature_win: float = 0.0

    def add_retrigger(self, count: int):
        tier = bonus_for_scatter(count)
        if tier:
            self.spins_remaining += tier[1]

@dataclass
class RoundState:
    bet: float
    total_win: float = 0.0
    feature: FeatureState | None = None
    capped: bool = False

    def remaining_cap(self):
        return max(0.0, ROUND_CAP * self.bet - self.total_win)

    def record(self, amount):
        amount = min(max(0.0, amount), self.remaining_cap())
        self.total_win += amount
        if self.remaining_cap() <= 1e-12:
            self.capped = True
        return amount

def start_feature(board, scatter_total):
    tier = bonus_for_scatter(scatter_total)
    if not tier:
        return None
    expanded, reels = expand_wild_reels(board)
    name, spins, inc = tier
    return FeatureState(name, spins, 1.0, inc, set(reels)), expanded

def play_feature_spin(state: FeatureState, board, round_state: RoundState):
    """Apply sticky reels, expand new Wild reels, evaluate, then progress state."""
    if state.spins_remaining <= 0 or round_state.capped:
        return {"totalWin": 0.0, "wins": [], "expanded_reels": []}
    state.spins_remaining -= 1
    expanded, reels = expand_wild_reels(board, state.sticky_reels)
    state.sticky_reels.update(reels)
    result = evaluate_ways(expanded, round_state.bet, state.multiplier, round_state.remaining_cap() / round_state.bet if round_state.bet else 0.0)
    awarded = round_state.record(result["totalWin"])
    state.total_feature_win += awarded
    result["totalWin"] = awarded
    result["expanded_reels"] = list(reels)
    count = scatter_count(board)
    if count >= 3:
        state.add_retrigger(count)
    state.multiplier += state.multiplier_increment
    return result
