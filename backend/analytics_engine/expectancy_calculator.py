def expectancy(wins: list[float], losses: list[float]) -> float:
    total = len(wins) + len(losses)
    if total == 0:
        return 0.0
    win_rate = len(wins) / total
    avg_win = sum(wins) / len(wins) if wins else 0.0
    avg_loss = abs(sum(losses) / len(losses)) if losses else 0.0
    return win_rate * avg_win - (1 - win_rate) * avg_loss
