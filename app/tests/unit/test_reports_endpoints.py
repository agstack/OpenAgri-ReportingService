from unittest import TestCase
from unittest.mock import patch, MagicMock

from fastapi import HTTPException
import os

REQUIRED_ENV_VARS = {
    "REPORTING_GATEKEEPER_USERNAME": "mock_user",
    "REPORTING_GATEKEEPER_PASSWORD": "mock_pass",
    "REPORTING_BACKEND_CORS_ORIGINS": '["*"]',
    "REPORTING_POSTGRES_USER": "mock_pg_user",
    "REPORTING_POSTGRES_PASSWORD": "mock_pg_pass",
    "REPORTING_POSTGRES_DB": "mock_db",
    "REPORTING_POSTGRES_HOST": "mock_host",
    "REPORTING_POSTGRES_PORT": "5432",
    "REPORTING_SERVICE_NAME": "mock_service",
    "REPORTING_SERVICE_PORT": "8000",
    "REPORTING_GATEKEEPER_BASE_URL": "http://mock.gatekeeper",
    "JWT_ACCESS_TOKEN_EXPIRATION_TIME": "3600",
    "JWT_SIGNING_KEY": "mock_jwt_secret",
    "PDF_DIRECTORY": "/",
    "REPORTING_USING_GATEKEEPER": "True"
}

# TestReportAPI Class that will be used for unit test of report endpoints
class TestReportAPI(TestCase):

    CORRECT_TOKEN = 'eyJhbGciOiJIUzI1NiJ9.eyJJc3N1ZXIiOiJJc3N1ZXIifQ.HLkw6rgYSwcv0sE69OKiNQFvHoo-6VqlxC5nKuMmftg'
    WRONG_TOKEN = "ayJhbGciOiJIUzI1NiJ9.eyJJc3N1ZXIiOiJJc3N1ZXIifQ.HLkw6rgYSwcv0sE69OKiNQFvHoo-6VqlxC5nKuMmftg"
    BASE_URL = "/api/v1/openagri-report"

    @staticmethod
    def user_login(token):
        if token == TestReportAPI.CORRECT_TOKEN:
            return ""
        else:
            raise HTTPException(status_code=401, detail='Not Auth!')


    def patch(self, obj, attr, value = None):
        if value is None:
            value = MagicMock()
        patcher = patch.object(obj, attr, value)
        self.addCleanup(patcher.stop)
        return patcher.start()


    def setUp(self):
        for k, v in REQUIRED_ENV_VARS.items():
            os.environ[k] = v

        super().setUpClass()
        from main import app
        from api.api_v1.endpoints import report
        from fastapi.testclient import TestClient
        from api.deps import get_current_user

        app.dependency_overrides[get_current_user] = TestReportAPI.user_login
        self.patch(
            report,
            "decode_jwt_token",
            MagicMock(return_value={"user_id": "123"})
        )
        self.client=TestClient(app)


    def test_get_report_endpoint_not_auth(self):
        response = self.client.get(f"{TestReportAPI.BASE_URL}/123/", headers={"X-Token": "OK"},
                              params={"token": TestReportAPI.WRONG_TOKEN})
        assert response.status_code == 401

    def test_get_report_endpoint_auth_in_progress(self):
        response = self.client.get(f"{TestReportAPI.BASE_URL}/123/", headers={"X-Token": "OK"},
                          params={"token": TestReportAPI.CORRECT_TOKEN})
        assert response.status_code == 202

    def test_get_report_endpoint_success(self):
        from api.api_v1.endpoints import report
        from fastapi import Response
        self.patch(
            report,
            "FileResponse",
            MagicMock(return_value=Response(content=b"PDF", media_type="application/pdf"))
        )

        self.patch(
            report.os.path,
            "exists",
            MagicMock(return_value=True)
        )
        response =  self.client.get(f"{TestReportAPI.BASE_URL}/123/", headers={"X-Token": "OK"},
                          params={"token": TestReportAPI.CORRECT_TOKEN})
        assert response.status_code == 200
