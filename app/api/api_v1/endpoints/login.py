from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core import security
from core.security import *
from core.config import settings
from api import deps
from crud import user
from schemas import Token
import requests

router = APIRouter()


@router.post("/access-token/", response_model=Token)
def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(deps.get_db),
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    if settings.REPORTING_USING_GATEKEEPER:
        login = requests.post(
            url=settings.REPORTING_GATEKEEPER_BASE_URL + "api/login/",
            headers={"Content-Type": "application/json"},
            json={
                "username": "{}".format(form_data.username),
                "password": "{}".format(form_data.password),
            },
        )

        if login.status_code == 400:
            raise HTTPException(status_code=400, detail="Login failed.")
        return Token(
            access_token=login.json()["access"],
            token_type="bearer",
        )
    else:
        user_db = user.authenticate(
            db, email=form_data.username, password=form_data.password
        )

        if not user_db:
            raise HTTPException(status_code=400, detail="Incorrect email or password")

        access_token_expires = timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRATION_TIME
        )

        at = Token(
            access_token=security.create_access_token(
                user_db.id, expires_delta=access_token_expires
            ),
            token_type="bearer",
        )

    return at
