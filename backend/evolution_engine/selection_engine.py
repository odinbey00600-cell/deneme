def select_best(generations: list[dict]) -> dict | None:
    if not generations:
        return None
    return sorted(generations, key=lambda g: g.get('ending_balance', 0), reverse=True)[0]
