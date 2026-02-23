import time


class HeartbeatMonitor:
    def __init__(self, timeout_seconds: int):
        self.timeout_seconds = timeout_seconds
        self.last = time.time()

    def beat(self):
        self.last = time.time()

    def healthy(self) -> bool:
        return (time.time() - self.last) < self.timeout_seconds
