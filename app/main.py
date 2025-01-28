from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from core.config import settings
from api.api_v1.api import api_router
from init_gatekeeper import register_apis_to_gatekeeper


@asynccontextmanager
async def lifespan(fa: FastAPI):
    if settings.REPORTING_USING_GATEKEEPER:
        register_apis_to_gatekeeper()
    yield


app = FastAPI(
    title="Reporting service", openapi_url="/api/v1/openapi.json", lifespan=lifespan
)


# Set all CORS enabled origins
if settings.REPORTING_BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.REPORTING_BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix="/api/v1")
