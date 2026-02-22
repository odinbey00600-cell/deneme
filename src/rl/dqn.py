from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim


class QNet(nn.Module):
    def __init__(self, state_dim: int, action_dim: int) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


@dataclass
class RLAction:
    action: int
    confidence: float


class DQNAgent:
    def __init__(self, state_dim: int, action_dim: int) -> None:
        self.action_dim = action_dim
        self.policy = QNet(state_dim, action_dim)
        self.target = QNet(state_dim, action_dim)
        self.target.load_state_dict(self.policy.state_dict())
        self.optim = optim.Adam(self.policy.parameters(), lr=1e-3)
        self.buffer = deque(maxlen=10000)
        self.gamma = 0.99

    def act(self, state: np.ndarray, epsilon: float = 0.05) -> RLAction:
        if random.random() < epsilon:
            action = random.randrange(self.action_dim)
            return RLAction(action=action, confidence=0.2)
        with torch.no_grad():
            qvals = self.policy(torch.tensor(state, dtype=torch.float32).unsqueeze(0)).squeeze(0)
            action = int(torch.argmax(qvals).item())
            conf = float(torch.softmax(qvals, dim=0).max().item())
            return RLAction(action=action, confidence=conf)

    def push(self, transition: tuple[np.ndarray, int, float, np.ndarray, bool]) -> None:
        self.buffer.append(transition)

    def train_step(self, batch_size: int = 64) -> None:
        if len(self.buffer) < batch_size:
            return
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = map(np.array, zip(*batch))

        states_t = torch.tensor(states, dtype=torch.float32)
        actions_t = torch.tensor(actions, dtype=torch.int64).unsqueeze(1)
        rewards_t = torch.tensor(rewards, dtype=torch.float32).unsqueeze(1)
        next_states_t = torch.tensor(next_states, dtype=torch.float32)
        dones_t = torch.tensor(dones, dtype=torch.float32).unsqueeze(1)

        q = self.policy(states_t).gather(1, actions_t)
        next_q = self.target(next_states_t).max(1, keepdim=True)[0].detach()
        target_q = rewards_t + self.gamma * (1 - dones_t) * next_q

        loss = nn.MSELoss()(q, target_q)
        self.optim.zero_grad()
        loss.backward()
        self.optim.step()

    def sync_target(self) -> None:
        self.target.load_state_dict(self.policy.state_dict())
