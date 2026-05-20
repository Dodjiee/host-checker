import os
from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI, Request
from pymongo import AsyncMongoClient


logger = getLogger(__name__)

MONGODB_URL = os.environ.get("MONGODB_URL", "mongodb://localhost:27017/host_checker")
MONGODB_DATABASE = os.environ.get("MONGODB_DATABASE", "host_checker")


@asynccontextmanager
async def database_lifespan(app: FastAPI):
    app.state.mongodb_client = AsyncMongoClient(MONGODB_URL)
    app.state.database = app.state.mongodb_client[MONGODB_DATABASE]

    ping_response = await app.state.database.command("ping")
    if int(ping_response["ok"]) != 1:
        raise RuntimeError("Problem connecting to MongoDB.")

    logger.info("Connected to MongoDB database '%s'.", MONGODB_DATABASE)
    yield
    await app.state.mongodb_client.close()


def get_database(request: Request):
    return request.app.state.database
