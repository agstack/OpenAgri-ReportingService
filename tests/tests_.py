from pathlib import Path
import pytest
import requests


@pytest.fixture()
def user_payload():
    return {"email": "test.test@example.com", "password": "Test123321"}


@pytest.fixture()
def user_login():
    return {"username": "test.test@example.com", "password": "Test123321"}


@pytest.mark.order(1)
def test_data_flow(user_payload, user_login):
    # Register
    response = requests.post(
        url="http://localhost/api/v1/user/register/",
        json=user_payload,
    )

    # Login
    response = requests.post(
        url="http://localhost/api/v1/login/access-token/", data=user_login
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()

    access_token = response.json()["access_token"]

    # Upload Data
    file = open(Path("example", "datasets", "example_farm_calendar_AIM.jsonld"), "rb")

    response = requests.post(
        url="http://localhost/api/v1/openagri-dataset/",
        headers={"authorization": "bearer {}".format(access_token)},
        files={"data": file},
    )

    assert response.status_code == 200
    assert "id" in response.json()

    data_id = response.json()["id"]

    # Get Data
    response = requests.get(
        url="http://localhost/api/v1/openagri-dataset/{}".format(data_id),
        headers={"authorization": "bearer {}".format(access_token)},
    )

    assert response.status_code == 200

    # Remove Data
    response = requests.delete(
        url="http://localhost/api/v1/openagri-dataset/{}".format(data_id),
        headers={"authorization": "bearer {}".format(access_token)},
    )

    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()[
        "message"
    ] == "Successfully removed dataset with ID:{}.".format(data_id)

    # Delete User
    response = requests.delete(
        url="http://localhost/api/v1/user/",
        headers={"authorization": "bearer {}".format(access_token)},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Successfully deleted user."


@pytest.mark.order(2)
def test_report_flow(user_payload, user_login):
    # Register
    response = requests.post(
        url="http://localhost/api/v1/user/register/",
        json=user_payload,
    )

    # Login
    response = requests.post(
        url="http://localhost/api/v1/login/access-token/", data=user_login
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()

    access_token = response.json()["access_token"]

    # Upload Data
    file = open(Path("example", "datasets", "example_farm_calendar_AIM.jsonld"), "rb")

    response = requests.post(
        url="http://localhost/api/v1/openagri-dataset/",
        headers={"authorization": "bearer {}".format(access_token)},
        files={"data": file},
    )

    assert response.status_code == 200
    assert "id" in response.json()

    data_id = response.json()["id"]

    # Create Report
    report_types = [
        "work-book",
        "plant-protection",
        "irrigations",
        "fertilisations",
        "harvests",
        "GlobalGAP",
    ]
    report_ids = []
    for rt in report_types:
        response = requests.post(
            url="http://localhost/api/v1/openagri-report/{report_type}/dataset/{dataset_id}".format(
                report_type=rt, dataset_id=data_id
            ),
            headers={"authorization": "bearer {}".format(access_token)},
        )

        assert response.status_code == 200
        assert "id" in response.json()

        report_ids.append(response.json()["id"])

    # Get Report
    for ri in report_ids:
        response = requests.get(
            url="http://localhost/api/v1/openagri-report/{}".format(ri),
            headers={"authorization": "bearer {}".format(access_token)},
        )

        assert response.status_code == 200
        assert "content-type" in response.headers
        assert response.headers["content-type"] == "application/pdf"

    # Delete Report
    for ri in report_ids:
        response = requests.delete(
            url="http://localhost/api/v1/openagri-report/{}".format(ri),
            headers={"authorization": "bearer {}".format(access_token)},
        )

        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()[
            "message"
        ] == "Successfully deleted report with ID:{}.".format(ri)

    # Remove Data
    response = requests.delete(
        url="http://localhost/api/v1/openagri-dataset/{}".format(data_id),
        headers={"authorization": "bearer {}".format(access_token)},
    )

    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()[
        "message"
    ] == "Successfully removed dataset with ID:{}.".format(data_id)

    # Delete User
    response = requests.delete(
        url="http://localhost/api/v1/user/",
        headers={"authorization": "bearer {}".format(access_token)},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Successfully deleted user."
