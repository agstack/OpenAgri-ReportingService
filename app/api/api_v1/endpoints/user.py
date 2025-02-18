import json
import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any
import logging

from api import deps
from models import User
from schemas import Message, UserCreate, UserMe
from crud import user
from core import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register/", response_model=Message)
def register(
    user_information: UserCreate, db: Session = Depends(deps.get_db)
) -> Message:
    """
    Registration API for the service.
    """
    if settings.REPORTING_USING_GATEKEEPER:
        payload = json.dumps(
            {
                "username": user_information.email.split("@")[0],
                "email": user_information.email,
                "password": user_information.password,
                "first_name": "Reporting",
                "last_name": "Backend",
            }
        )
        headers = {"Content-Type": "application/json"}
        url = settings.REPORTING_GATEKEEPER_BASE_URL + "api/register/"
        gatekeeper_response_code = False
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            if str(response.status_code)[0] == 2:
                response = Message(
                    message="You have successfully registered to Gatekeeper!"
                )
                gatekeeper_response_code = True
                return response

        except Exception as e:
            logger.info(f"Failed to register REPORTING user, {e}")
            raise HTTPException(
                status_code=400,
                detail="Registration failed",
            )

        if not gatekeeper_response_code:
            raise HTTPException(
                status_code=400,
                detail=f"Gatekeeper failed to register user. Please make sure all fields are correct.",
            )
    # When Gatekeeper is not used

    pwd_check = settings.PASSWORD_SCHEMA_OBJ.validate(pwd=user_information.password)
    if not pwd_check:
        raise HTTPException(
            status_code=400,
            detail="Password needs to be at least 8 characters long,"
            "contain at least one uppercase and one lowercase letter, one digit and have no spaces.",
        )

    user_db = user.get_by_email(db=db, email=user_information.email)
    if user_db:
        raise HTTPException(
            status_code=400,
            detail="User with email:{} already exists.".format(user_information.email),
        )

    user.create(db=db, obj_in=user_information)

    response = Message(message="You have successfully registered to reporting system!")

    return response


@router.get("/me/", response_model=UserMe)
def get_me(current_user: User = Depends(deps.get_current_user)) -> Any:
    """
    Returns user email
    """
    if settings.REPORTING_USING_GATEKEEPER:
        raise HTTPException(
            status_code=400, detail="This API can't be called when gatekeeper is used."
        )
    return current_user


@router.delete("/", response_model=Message)
def delete_user(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> Message:
    """
    Delete self from system.
    """
    if settings.REPORTING_USING_GATEKEEPER:
        raise HTTPException(
            status_code=400, detail="This API can't be called when gatekeeper is used."
        )
    user.remove(db=db, id=current_user.id)

    return Message(message="Successfully deleted user.")
