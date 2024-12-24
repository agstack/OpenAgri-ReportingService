from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from core.config import settings
from api.api_v1.api import api_router
from init_gatekeeper import register_apis_to_gatekeeper

app = FastAPI(title="Reporting service", openapi_url="/api/v1/openapi.json")


@asynccontextmanager
async def lifespan(fa: FastAPI):
    if settings.USING_GATEKEEPER:
        register_apis_to_gatekeeper()
    yield


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix="/api/v1")
