from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session

import crud
from api import deps
from models import User
from schemas import ReportCreate, Message, ReportDBID
from utils.json_handler import ReportHandler

router = APIRouter()


@router.get("/{report_id}")
def get_by_id(
    report_id: int,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """
    Returns a report via ID.
    """

    report_db = crud.report.get(db=db, id=report_id)

    if not report_db:
        raise HTTPException(
            status_code=400,
            detail="Report with ID:{} does not exist.".format(report_id),
        )

    report_pdf_handler = ReportHandler(report_db=report_db)
    pdf = report_pdf_handler.generate_pdf()

    if not pdf:
        raise HTTPException(
            status_code=400,
            detail=f"Reporting service failed during PDF generation. Error details: [Type: {report_db.type}, ID: {report_db.id}]",
        )

    headers = {"Content-Disposition": "attachment; filename={}".format(report_db.name)}

    return Response(
        content=bytes(pdf.output()), media_type="application/pdf", headers=headers
    )


@router.post("/{report_type}/dataset/{dataset_id}", response_model=ReportDBID)
def create_by_data_id(
    dataset_id: int,
    report_type: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> ReportDBID:
    """
    Generate a report based off of a previously uploaded/queried data file.
    Types: [work-book, plant-protection, irrigations, fertilisations, harvests, GlobalGAP]
    """

    # short term solution, should be in a separate model in the DB, or a part of an existing model.
    types = {
        "work_book": "work-book",
        "plant_protection": "plant-protection",
        "irrigation": "irrigations",
        "fertilisation": "fertilisations",
        "harvest": "harvests",
        "global_gap": "GlobalGAP",
        "livestock": "livestock",
    }

    dataset_db = crud.data.get(db=db, id=dataset_id)

    if not dataset_db:
        raise HTTPException(
            status_code=400,
            detail="Dataset with ID:{} does not exist.".format(dataset_id),
        )

    if report_type not in types.values():
        raise HTTPException(
            status_code=400,
            detail="Report type {} isn't part of the offered types.".format(
                report_type
            ),
        )

    # Create DB entry
    report_db = crud.report.create(
        db=db,
        obj_in=ReportCreate(
            name=dataset_db.filename + " report.pdf",
            file=dataset_db.data,
            type=report_type,
        ),
    )

    return ReportDBID(**report_db.__dict__)


@router.delete("/{report_id}", response_model=Message)
def delete_report(
    report_id: int,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> Message:
    """
    Delete a report by ID.
    """

    report_db = crud.report.get(db=db, id=report_id)

    if not report_db:
        raise HTTPException(
            status_code=400,
            detail="Report with ID:{} does not exist.".format(report_id),
        )

    crud.report.remove(db=db, id=report_id)

    return Message(message="Successfully deleted report with ID:{}.".format(report_id))
