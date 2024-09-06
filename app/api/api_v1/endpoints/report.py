import datetime
import json

from fastapi import APIRouter, Depends, Response, HTTPException
from fpdf import FPDF
from sqlalchemy.orm import Session

import crud
import utils
from api import deps
from models import User
from schemas import FarmProfile, MachineryAssetsOfFarm, PlotParcelDetail, ReportDB, ReportCreate, Message, ReportDBID

from utils import plant_protection, irrigations, fertilisation, harvests, work_book

router = APIRouter()


@router.get("/{report_id}")
def get_by_id(
        report_id: int,
        current_user: User = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    """
    Returns a report via ID.
    """

    report_db = crud.report.get(db=db, id=report_id)

    if not report_db:
        raise HTTPException(
            status_code=400,
            detail="Report with ID:{} does not exist.".format(report_id)
        )

    types = {"work_book": "work-book", "plant_protection": "plant-protection", "irrigation": "irrigations", "fertilisations": "fertilisations", "harvest": "harvests", "global_gap": "GlobalGAP"}

    if report_db.type == "work-book":
        json_file = json.loads(report_db.file)

        pdf = utils.work_book(
            farm=utils.parse_farm_profile(json_file),
            plot=utils.parse_plot_detail(json_file),
            cult=utils.parse_generic_cultivation_info(json_file),
            irri=utils.parse_irrigation(json_file),
            fert=utils.parse_fertilization(json_file),
            pdmd=utils.parse_plant_protection(json_file)
        )

    elif report_db.type == "plant-protection":

        pdf = plant_protection(utils.parse_plant_protection(json.loads(report_db.file)))

    elif report_db.type == "irrigations":

        pdf = irrigations(utils.parse_irrigation(json.loads(report_db.file)))

    elif report_db.type == "fertilisations":

        pdf = fertilisation(utils.parse_fertilization(json.loads(report_db.file)))

    elif report_db.type == "harvests":
        # This will pass always, because it generates an empty .pdf every time
        pdf = harvests()
    else:
        # Same as work-book for now
        json_file = json.loads(report_db.file)

        pdf = utils.work_book(
            farm=utils.parse_farm_profile(json_file),
            plot=utils.parse_plot_detail(json_file),
            cult=utils.parse_generic_cultivation_info(json_file),
            irri=utils.parse_irrigation(json_file),
            fert=utils.parse_fertilization(json_file),
            pdmd=utils.parse_plant_protection(json_file)
        )

    # Return the report as a response (binary)
    headers = {
        "Content-Disposition": "attachment; filename={}".format(report_db.name)
    }

    return Response(content=bytes(pdf.output()), media_type="application/pdf", headers=headers)


@router.post("/{report_type}/dataset/{dataset_id}", response_model=ReportDBID)
def create_by_data_id(
        dataset_id: int,
        report_type: str,
        current_user: User = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
) -> ReportDBID:
    """
    Generate a report based off of a previously uploaded/queried data file.
    [Currently returns an example PDF file regardless of input json]
    Types: [work-book, plant-protection, irrigations, fertilisations, harvests, GlobalGAP]
    """

    # short term solution, should be in a separate model in the DB, or a part of an existing model.
    types = {"work_book": "work-book", "plant_protection": "plant-protection", "irrigation": "irrigations", "fertilisation": "fertilisations", "harvest": "harvests", "global_gap": "GlobalGAP"}

    dataset_db = crud.data.get(db=db, id=dataset_id)

    if not dataset_db:
        raise HTTPException(
            status_code=400,
            detail="Dataset with ID:{} does not exist.".format(dataset_id)
        )

    if report_type not in types.values():
        raise HTTPException(
            status_code=400,
            detail="Report type {} isn't part of the offered types.".format(report_type)
        )

    # Create DB entry
    report_db = crud.report.create(db=db, obj_in=ReportCreate(name=dataset_db.filename + " report.pdf", file=dataset_db.data, type=report_type))

    return ReportDBID(**report_db.__dict__)


@router.delete("/{report_id}", response_model=Message)
def delete_report(
        report_id: int,
        current_user: User = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
) -> Message:
    """
    Delete a report by ID.
    """

    report_db = crud.report.get(db=db, id=report_id)

    if not report_db:
        raise HTTPException(
            status_code=400,
            detail="Report with ID:{} does not exist.".format(report_id)
        )

    crud.report.remove(db=db, id=report_id)

    return Message(message="Successfully deleted report with ID:{}.".format(report_id))
