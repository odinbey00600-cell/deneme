import asyncio


async def online_training(agent, interval_seconds: int = 60):
    while True:
        agent.train(512)
        await asyncio.sleep(interval_seconds)
