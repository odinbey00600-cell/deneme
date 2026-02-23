import uvicorn

from api_server.app import app
from config_manager.settings import settings


if __name__ == '__main__':
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
