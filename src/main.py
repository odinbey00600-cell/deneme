from src.config.settings import get_settings
from src.core.bot import TradingBot
from src.utils.logger import configure_logger


if __name__ == "__main__":
    configure_logger()
    bot = TradingBot(get_settings())
    bot.run()
