from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import gymnasium as gym
import numpy as np


class BTCGymEnv(gym.Env):
    def __init__(self):
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(10,), dtype=np.float32)
        self.action_space = gym.spaces.Discrete(4)
        self.state = np.zeros(10, dtype=np.float32)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.state = np.zeros(10, dtype=np.float32)
        return self.state, {}

    def step(self, action):
        reward = float(np.random.normal(0, 0.01))
        terminated = False
        truncated = False
        return self.state, reward, terminated, truncated, {}


class PPOAgent:
    def __init__(self, seed: int):
        env = DummyVecEnv([BTCGymEnv])
        self.model = PPO(
            'MlpPolicy', env, verbose=0, seed=seed,
            learning_rate=3e-4, ent_coef=0.01, max_grad_norm=0.5
        )

    def train(self, timesteps: int = 2048):
        self.model.learn(total_timesteps=timesteps)

    def act(self, state):
        action, _ = self.model.predict(state, deterministic=True)
        return int(action)
