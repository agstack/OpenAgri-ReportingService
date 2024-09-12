import pytest

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture()
def user_payload():
    return {
        "email": "test@example.com",
        "password": "TestPassword10"
    }


@pytest.fixture()
def user_login():
    return {
        "username": "test@example.com",
        "password": "TestPassword10"
    }


@pytest.mark.order(1)
def test_access_token():
    response = client.post(
        url="api/v1/login/access-token/",
        data={"username": "stefan.drobic@vizlore.com", "password": "Windows8"},
    )

    assert response.status_code == 200


@pytest.mark.order(2)
def test_delete_user_not_logged():
    response = client.delete(
        url="api/v1/user/"
    )

    assert response.status_code == 401


@pytest.mark.order(3)
def test_user_flow(user_payload, user_login):
    # Register
    response = client.post(
        url="api/v1/user/register/",
        json=user_payload,
    )

    assert response.status_code == 200
    assert response.json()["message"] == "You have successfully registered!"

    # Login
    response = client.post(
        url="api/v1/login/access-token/",
        data=user_login
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()

    access_token = response.json()["access_token"]

    # Remove
    response = client.delete(
        url="api/v1/user/",
        headers={
            "authorization": "bearer {}".format(access_token)
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Successfully deleted user."


@pytest.mark.order(4)
def test_data_flow(user_payload, user_login):
    # Register
    response = client.post(
        url="api/v1/user/register/",
        json=user_payload,
    )

    assert response.status_code == 200
    assert response.json()["message"] == "You have successfully registered!"

    # Login
    response = client.post(
        url="api/v1/login/access-token/",
        data=user_login
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()

    access_token = response.json()["access_token"]

    # Upload Data
    file = open("test.json", "rb")

    response = client.post(
        url="api/v1/openagri-dataset/",
        headers={
            "authorization": "bearer {}".format(access_token)
        },
        files={
            "data": file
        }

    )

    assert response.status_code == 200
    assert "id" in response.json()

    data_id = response.json()["id"]

    # Get Data
    response = client.get(
        url="api/v1/openagri-dataset/{}".format(data_id),
        headers={
            "authorization": "bearer {}".format(access_token)
        }
    )

    assert response.status_code == 200

    # Remove Data
    response = client.delete(
        url="api/v1/openagri-dataset/{}".format(data_id),
        headers={
            "authorization": "bearer {}".format(access_token)
        }
    )

    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Successfully removed dataset with ID:{}.".format(data_id)

    # Delete User
    response = client.delete(
        url="api/v1/user/",
        headers={
            "authorization": "bearer {}".format(access_token)
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Successfully deleted user."


@pytest.mark.order(5)
def test_report_flow(user_payload, user_login):
    # Register
    response = client.post(
        url="api/v1/user/register/",
        json=user_payload,
    )

    assert response.status_code == 200
    assert response.json()["message"] == "You have successfully registered!"

    # Login
    response = client.post(
        url="api/v1/login/access-token/",
        data=user_login
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()

    access_token = response.json()["access_token"]

    # Upload Data
    file = open("test.json", "rb")

    response = client.post(
        url="api/v1/openagri-dataset/",
        headers={
            "authorization": "bearer {}".format(access_token)
        },
        files={
            "data": file
        }

    )

    assert response.status_code == 200
    assert "id" in response.json()

    data_id = response.json()["id"]

    # Create Report
    report_types = ["work-book", "plant-protection", "irrigations", "fertilisations", "harvests", "GlobalGAP"]
    report_ids = []
    for rt in report_types:
        response = client.post(
            url="api/v1/openagri-report/{report_type}/dataset/{dataset_id}".format(report_type=rt, dataset_id=data_id),
            headers={
                "authorization": "bearer {}".format(access_token)
            }
        )

        assert response.status_code == 200
        assert "id" in response.json()

        report_ids.append(response.json()["id"])

    # Get Report
    for ri in report_ids:
        response = client.get(
            url="api/v1/openagri-report/{}".format(ri),
            headers={
                "authorization": "bearer {}".format(access_token)
            }
        )

        assert response.status_code == 200
        assert "content-type" in response.headers
        assert response.headers["content-type"] == "application/pdf"

    # Delete Report
    for ri in report_ids:
        response = client.delete(
            url="api/v1/openagri-report/{}".format(ri),
            headers={
                "authorization": "bearer {}".format(access_token)
            }
        )

        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()["message"] == "Successfully deleted report with ID:{}.".format(ri)

    # Remove Data
    response = client.delete(
        url="api/v1/openagri-dataset/{}".format(data_id),
        headers={
            "authorization": "bearer {}".format(access_token)
        }
    )

    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Successfully removed dataset with ID:{}.".format(data_id)

    # Delete User
    response = client.delete(
        url="api/v1/user/",
        headers={
            "authorization": "bearer {}".format(access_token)
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Successfully deleted user."






