from fastapi import APIRouter, File, Depends, HTTPException, Response, UploadFile
from sqlalchemy.orm import Session

from api import deps
from models import User

import crud

from schemas import DataCreate, DataID, DataDB

router = APIRouter()


@router.get("/{data_id}", response_model=DataDB)
def get_by_id(
        data_id: int,
        current_user: User = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    """
    Returns the data, as a formatted json string.
    """

    data_db = crud.data.get(db=db, id=data_id)

    if not data_db:
        raise HTTPException(
            status_code=400,
            detail="Data file with ID:{} does not exist.".format(data_id)
        )

    return DataDB(**data_db.__dict__)


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


@router.get("/download/{data_id}")
def download_json(
        data_id: int,
        current_user: User = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    """
    Returns the previously uploaded/queried json for download.
    """

    data_db = crud.data.get(db=db, id=data_id)

    if not data_db:
        raise HTTPException(
            status_code=400,
            detail="Data file with ID:{} does not exist.".format(data_id)
        )

    headers = {
        "Content-Disposition": "attachment; filename={}".format(data_db.filename)
    }

    return Response(content=data_db.data, media_type="application/octet-stream", headers=headers)

