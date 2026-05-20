import os
from datetime import UTC, datetime

from bson import ObjectId
from fastapi import FastAPI, HTTPException, Request, status

from .database import MONGODB_DATABASE, database_lifespan, get_database
from .schemas import HostCreate, HostResponse, host_document_to_response


SERVICE_NAME = os.environ.get("SERVICE_NAME", "api-service")

app = FastAPI(title="Host Checker API", version="0.1.0", lifespan=database_lifespan)


@app.get("/health")
async def health(request: Request):
    database = get_database(request)
    await database.command("ping")
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "database": {
            "status": "ok",
            "name": MONGODB_DATABASE,
        },
    }


@app.post("/hosts", response_model=HostResponse, status_code=status.HTTP_201_CREATED)
async def create_host(host: HostCreate, request: Request):
    database = get_database(request)
    now = datetime.now(UTC)
    host_document = {
        "_id": ObjectId(),
        "name": host.name,
        "url": str(host.url),
        "is_active": True,
        "check_interval_seconds": host.check_interval_seconds,
        "last_status": None,
        "summary": None,
        "created_at": now,
        "updated_at": now,
    }

    await database.hosts.insert_one(host_document)
    return host_document_to_response(host_document)


@app.get("/hosts", response_model=list[HostResponse])
async def get_hosts(request: Request):
    database = get_database(request)

    hosts = []
    cursor = database.hosts.find({})

    async for host_document in cursor:
        hosts.append(host_document_to_response(host_document))

    return hosts


@app.get("/hosts/{host_id}", response_model=HostResponse)
async def get_host(host_id: str, request: Request):
    if not ObjectId.is_valid(host_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid host id.",
        )

    database = get_database(request)
    host_document = await database.hosts.find_one({"_id": ObjectId(host_id)})
    if host_document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Host not found.",
        )

    return host_document_to_response(host_document)
