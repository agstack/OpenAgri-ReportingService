from fastapi import HTTPException

from core import settings
import requests
from typing import Dict, Optional, Union


def make_get_request(
    url: str,
    params: Optional[Dict[str, Union[str, int, float]]] = None,
    token: Optional[Dict[str, str]] = None,
) -> Union[dict, str]:
    """
    Makes a GET request with custom parameters and headers.

    Args:
        url (str): The base URL for the request
        params (Dict[str, Union[str, int, float]], optional): Query parameters to append to URL
        token (Dict[str, str], optional): Token to be sent to request

    Returns:
        requests.Response: JSON response from the request

    Raises:
        ValueError: For invalid input parameters
    """

    base_url = f"{settings.REPORTING_GATEKEEPER_BASE_URL}{url}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token),
    }

    try:
        response = requests.get(
            base_url,
            params=params,
            headers=headers,
        )

        response.raise_for_status()

        return response.json()

    except Exception as ee:
        raise HTTPException(status_code=400, detail="Gatekeeper API returned an error.")
