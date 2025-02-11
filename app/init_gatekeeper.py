import json

import requests
from fastapi import APIRouter
from core.config import settings
from api.api_v1.endpoints import report


def register_apis_to_gatekeeper():
    print("Adding APIs to gatekeeper")

    payload = json.dumps(
        {
            "username": settings.REPORTING_GATEKEEPER_USERNAME,
            "email": "reporting-backend@gmail.com",
            "password": settings.REPORTING_GATEKEEPER_PASSWORD,
            "first_name": "Reporting",
            "last_name": "Backend",
        }
    )
    headers = {"Content-Type": "application/json"}
    url = settings.REPORTING_GATEKEEPER_BASE_URL + "api/register/"

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
    except Exception as e:
        print("Failed to register REPORTING user", e)
        return
    # If already registered it will proceed

    at = requests.post(
        url=settings.REPORTING_GATEKEEPER_BASE_URL + "api/login/",
        headers={"Content-Type": "application/json"},
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
            print("Port registered", settings.REPORTING_SERVICE_PORT)
            api_response = requests.post(
                url=settings.REPORTING_GATEKEEPER_BASE_URL + "api/register_service/",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(access),
                },
                json=json_data,
            )

        except Exception as e:
            print("Failed to register API to gatekeeper.", e)
            return

        if str(api_response.status_code)[0] != "2":
            print(api_response.json())
            print(
                f"API api/v1/{api.path.strip('/')} failed with registration to gatekeeper"
            )

    requests.post(
        url=settings.REPORTING_GATEKEEPER_BASE_URL + "api/logout/",
        headers={"Content-Type": "application/json"},
        json={"refresh": refresh},
    )
    return
