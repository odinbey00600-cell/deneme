from collections import deque
import random


class ReplayBuffer:
    def __init__(self, capacity: int = 10000):
        self.buf = deque(maxlen=capacity)

    def add(self, item):
        self.buf.append(item)

    def sample(self, batch_size: int):
        return random.sample(self.buf, min(batch_size, len(self.buf)))

    def __len__(self):
        return len(self.buf)
