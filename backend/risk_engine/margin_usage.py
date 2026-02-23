def margin_ratio(maint_margin: float, wallet_balance: float, unrealized_pnl: float) -> float:
    equity = wallet_balance + unrealized_pnl
    if equity <= 0:
        return 1e9
    return maint_margin / equity
