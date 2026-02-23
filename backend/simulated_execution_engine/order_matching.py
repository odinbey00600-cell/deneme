def fill_order(mark_price: float, qty: float, side: str, slipped_price: float) -> dict:
    return {'side': side, 'qty': qty, 'price': slipped_price, 'mark_price': mark_price}
