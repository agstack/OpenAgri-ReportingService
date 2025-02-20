import json

import requests
import logging

from fastapi import APIRouter
from core.config import settings
from api.api_v1.endpoints import report


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def register_apis_to_gatekeeper():
    at = requests.post(
        url=settings.REPORTING_GATEKEEPER_BASE_URL + "api/login/",
        json={
            "username": "{}".format(settings.REPORTING_GATEKEEPER_USERNAME),
            "password": "{}".format(settings.REPORTING_GATEKEEPER_PASSWORD),
        },
    )
    temp = at.json()
    access = temp["access"]
    refresh = temp["refresh"]

    # Registration  of APIs
    apis_to_register = APIRouter()
    apis_to_register.include_router(report.router, prefix="/openagri-report")
    for api in apis_to_register.routes:
        api_response = None
        try:
            json_data = {
                "base_url": "http://{}:{}/".format(
                    settings.REPORTING_SERVICE_NAME, settings.REPORTING_SERVICE_PORT
                ),
                "service_name": settings.REPORTING_SERVICE_NAME,
                "endpoint": f"api/v1/{api.path.strip('/')}",
                "methods": list(api.methods),
            }
            logger.info("Port registered", settings.REPORTING_SERVICE_PORT)
            api_response = requests.post(
                url=settings.REPORTING_GATEKEEPER_BASE_URL + "api/register_service/",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(access),
                },
                json=json_data,
            )

        except Exception as e:
            logger.info(f"Failed to register API to gatekeeper. {e}")
            return

        if str(api_response.status_code)[0] != "2":
            logger.info(
                f"API api/v1/{api.path.strip('/')} failed with registration to gatekeeper"
            )

    requests.post(
        url=settings.REPORTING_GATEKEEPER_BASE_URL + "api/logout/",
        json={"refresh": refresh},
    )
    return
