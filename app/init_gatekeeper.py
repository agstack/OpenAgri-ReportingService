import requests
from fastapi import APIRouter
from core.config import settings
from api.api_v1.endpoints import report


def register_apis_to_gatekeeper():
    at = requests.post(
        url=settings.GATEKEEPER_BASE_URL.unicode_string() + "api/login/",
        headers={"Content-Type": "application/json"},
        json={
            "username": "{}".format(settings.GATEKEEPER_USERNAME),
            "password": "{}".format(settings.GATEKEEPER_PASSWORD),
        },
    )
    temp = at.json()
    access = temp["access"]
    refresh = temp["refresh"]
    # Registration
    apis_to_register = APIRouter()
    apis_to_register.include_router(report.router, prefix="/openagri-report")
    for api in apis_to_register.routes:
        requests.post(
            url=settings.GATEKEEPER_BASE_URL.unicode_string() + "api/register_service/",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(access),
            },
            json={
                "base_url": "{}:{}".format(
                    settings.SERVICE_NAME, settings.SERVICE_PORT
                ),
                "service_name": "reporting",
                "endpoint": "api/v1/" + api.path.strip("/"),
                "methods": list(api.methods),
            },
        )
    requests.post(
        url=settings.GATEKEEPER_BASE_URL.unicode_string() + "api/logout/",
        headers={"Content-Type": "application/json"},
        json={"refresh": refresh},
    )
    return
