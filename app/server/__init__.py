from fastapi import FastAPI

from app.adapters import logger
from app.config import config
from .routes import router


async def start_server(server: FastAPI) -> FastAPI:
    """Run server and attach all the endpoints."""
    server.include_router(router=router, prefix=f"/{config.URL_PREFIX}" if config.URL_PREFIX else "")

    logger.info("Server is starting...")
    return server
