from src.config.settings import get_settings
from src.data.binance_client import BinanceFuturesGateway
from src.features.indicators import add_indicators
from src.rl.dqn import DQNAgent
from src.rl.environment import FuturesTimingEnv


def main() -> None:
    settings = get_settings()
    gateway = BinanceFuturesGateway(settings.binance_api_key, settings.binance_api_secret, settings.use_testnet)
    frame = add_indicators(gateway.fetch_klines(settings.symbols[0], "1m", settings.history_limit))

    env = FuturesTimingEnv(frame)
    agent = DQNAgent(state_dim=8, action_dim=4)

    for episode in range(20):
        state, _ = env.reset()
        done = False
        while not done:
            action = agent.act(state, epsilon=max(0.1, 1 - episode / 20)).action
            next_state, reward, done, _, _ = env.step(action)
            agent.push((state, action, reward, next_state, done))
            agent.train_step()
            state = next_state
        agent.sync_target()
        print(f"episode={episode} complete")


if __name__ == "__main__":
    main()
