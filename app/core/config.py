from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings
from password_validator import PasswordValidator
from typing import Optional, Any

from os import path, environ


class Settings(BaseSettings):
    PROJECT_ROOT: str = path.dirname(path.dirname(path.realpath(__file__)))

    REPORTING_GATEKEEPER_USERNAME: str
    REPORTING_GATEKEEPER_PASSWORD: str
    REPORTING_BACKEND_CORS_ORIGINS: Any

    REPORTING_POSTGRES_USER: str
    REPORTING_POSTGRES_PASSWORD: str
    REPORTING_POSTGRES_DB: str
    REPORTING_POSTGRES_HOST: str
    REPORTING_POSTGRES_PORT: int
    REPORTING_SERVICE_NAME: str
    REPORTING_SERVICE_PORT: int
    REPORTING_USING_GATEKEEPER: bool = True
    REPORTING_GATEKEEPER_BASE_URL: str
    REPORTING_FARMCALENDAR_BASE_URL: str = "api/proxy/farmcalendar/api/v1"
    REPORTING_FARMCALENDAR_URLS: dict = {
        "irrigations": "/IrrigationOperations/",
        "fertilization": "/FertilizationOperations/",
        "pesticides": "/CropProtectionOperations/",
        "pest": "/Pesticides/",
        "activity_types": "/FarmCalendarActivityTypes/",
        "observations": "/Observations/",
        "operations": "/CompostOperations/",
        "turning_operations": "/CompostTurningOperations/",
        "activities": "/FarmCalendarActivities/",
        "parcel": "/FarmParcels/",
        "animals": "/FarmAnimals/",
        "materials": "/AddRawMaterialOperations/",
        "machines": "/AgriculturalMachines/",
        "farm": "/Farm/"
    }

    PDF_DIRECTORY: str = "user_reports/"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values) -> Any:
        if isinstance(v, str):
            return v

        url = "postgresql://{}:{}@{}:{}/{}".format(
            environ.get("REPORTING_POSTGRES_USER"),
            environ.get("REPORTING_POSTGRES_PASSWORD"),
            environ.get("REPORTING_POSTGRES_HOST"),
            environ.get("REPORTING_POSTGRES_PORT", 5439),
            environ.get("REPORTING_POSTGRES_DB"),
        )

        return url

    PASSWORD_SCHEMA_OBJ: PasswordValidator = PasswordValidator()
    PASSWORD_SCHEMA_OBJ.min(8).max(
        100
    ).has().uppercase().has().lowercase().has().digits().has().no().spaces()
    JWT_ACCESS_TOKEN_EXPIRATION_TIME: int
    JWT_SIGNING_KEY: str


settings = Settings()
