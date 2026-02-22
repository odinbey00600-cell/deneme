from __future__ import annotations

import asyncio

from loguru import logger
from telegram import Bot


class Notifier:
    def __init__(self, token: str | None, chat_id: str | None) -> None:
        self.token = token
        self.chat_id = chat_id
        self.bot = Bot(token=token) if token else None

    async def send(self, text: str) -> None:
        logger.info(text)
        if self.bot and self.chat_id:
            try:
                await self.bot.send_message(chat_id=self.chat_id, text=text)
            except Exception as exc:  # noqa: BLE001
                logger.error("Notifier failed: {}", exc)

    def send_sync(self, text: str) -> None:
        asyncio.run(self.send(text))
