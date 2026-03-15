from pydantic import BaseModel


class ServiceStatus(BaseModel):
    database: str
    redis: str
    storage: str


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    services: ServiceStatus
