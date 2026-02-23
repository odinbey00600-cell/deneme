class SequenceValidator:
    def __init__(self):
        self.last_update_id = None
        self.gaps = 0

    def validate(self, update_id: int) -> bool:
        if self.last_update_id is None:
            self.last_update_id = update_id
            return True
        if update_id <= self.last_update_id:
            return False
        if update_id != self.last_update_id + 1:
            self.gaps += 1
        self.last_update_id = update_id
        return True
