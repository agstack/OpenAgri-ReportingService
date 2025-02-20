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

    # Delete User
    response = requests.delete(
        url="http://localhost/api/v1/user/",
        headers={"authorization": "bearer {}".format(access_token)},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Successfully deleted user."
