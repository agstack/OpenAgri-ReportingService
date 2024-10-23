from fastapi import APIRouter
from .endpoints import report, user, login, data

api_router = APIRouter()
api_router.include_router(report.router, prefix="/openagri-report", tags=["openagri-report"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(data.router, prefix="/openagri-dataset", tags=["openagri-dataset"])
