from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class HostCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    url: HttpUrl
    check_interval_seconds: int = Field(default=300, ge=60, le=900)


class HostResponse(BaseModel):
    id: str
    name: str
    url: str
    is_active: bool
    check_interval_seconds: int
    last_status: str | None
    summary: str | None
    created_at: datetime
    updated_at: datetime


def host_document_to_response(host: dict) -> HostResponse:
    return HostResponse(
        id=str(host["_id"]),
        name=host["name"],
        url=host["url"],
        is_active=host["is_active"],
        check_interval_seconds=host["check_interval_seconds"],
        last_status=host["last_status"],
        summary=host["summary"],
        created_at=host["created_at"],
        updated_at=host["updated_at"],
    )
