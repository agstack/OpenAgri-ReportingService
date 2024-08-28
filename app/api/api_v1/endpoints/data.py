import json

from fastapi import APIRouter, File, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from api import deps
from models import User

import crud

from schemas import DataCreate, DataID, Message

router = APIRouter()


@router.get("/{dataset_id}")
def get_by_id(
        dataset_id: int,
        current_user: User = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    """
    Returns the data, as a formatted json string.
    """

    data_db = crud.data.get(db=db, id=dataset_id)

    if not data_db:
        raise HTTPException(
            status_code=400,
            detail="Data file with ID:{} does not exist.".format(dataset_id)
        )

    dat = json.loads(data_db.data)

    return dat


@router.post("/", response_model=DataID)
async def upload_data(
        data: UploadFile = File(...),
        current_user: User = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    """
    Upload a JSON-LD compliant file to be used as a data source when creating a report.
    """

    a = await data.read()
    try:
        decoded_data = a.decode("utf-8")
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Error during file decoding, .json file may be corrupted."
        )

    data_db = crud.data.create(db=db, obj_in=DataCreate(data=decoded_data, filename=data.filename))

    return DataID(**data_db.__dict__)


@router.delete("/{dataset_id}", response_model=Message)
def delete_dataset(
        dataset_id: int,
        current_user: User = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
) -> Message:
    """
    Delete a dataset by ID.
    """

    dataset_db = crud.data.get(db=db, id=dataset_id)

    if not dataset_db:
        raise HTTPException(
            status_code=400,
            detail="Dataaset with ID:{} does not exist.".format(dataset_id)
        )

    crud.data.remove(db=db, id=dataset_id)

    return Message(message="Successfully removed dataset with ID:{}.".format(dataset_id))

