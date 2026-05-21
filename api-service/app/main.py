import os
from datetime import UTC, datetime

from bson import ObjectId
from fastapi import FastAPI, HTTPException, Request, status
from pymongo import ReturnDocument

from .database import MONGODB_DATABASE, database_lifespan, get_database
from .queue import send_host_check_message
from .schemas import HostCreate, HostResponse, host_document_to_response


SERVICE_NAME = os.environ.get("SERVICE_NAME", "api-service")

app = FastAPI(title="Host Checker API", version="0.1.0", lifespan=database_lifespan)


def get_object_id(host_id: str) -> ObjectId:
    if not ObjectId.is_valid(host_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid host id.",
        )

    return ObjectId(host_id)


async def update_host_active_status(
    request: Request,
    host_id: str,
    is_active: bool,
) -> HostResponse:
    database = get_database(request)
    host_document = await database.hosts.find_one_and_update(
        {"_id": get_object_id(host_id)},
        {"$set": {"is_active": is_active, "updated_at": datetime.now(UTC)}},
        return_document=ReturnDocument.AFTER,
    )

    if host_document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Host not found.",
        )

    return host_document_to_response(host_document)


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
    send_host_check_message(str(host_document["_id"]), reason="created",host_name = host.name)
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
    database = get_database(request)
    host_document = await database.hosts.find_one({"_id": get_object_id(host_id)})
    if host_document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Host not found.",
        )

    return host_document_to_response(host_document)


@app.post("/hosts/{host_id}/deactivate", response_model=HostResponse)
async def deactivate_host(host_id: str, request: Request):
    return await update_host_active_status(request, host_id, is_active=False)


@app.post("/hosts/{host_id}/activate", response_model=HostResponse)
async def activate_host(host_id: str, request: Request):
    return await update_host_active_status(request, host_id, is_active=True)
