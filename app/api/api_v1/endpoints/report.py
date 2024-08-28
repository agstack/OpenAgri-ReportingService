import datetime

from fastapi import APIRouter, Depends, Response, HTTPException
from fpdf import FPDF
from sqlalchemy.orm import Session

import crud
from api import deps
from models import User
from schemas import FarmProfile, MachineryAssetsOfFarm, PlotParcelDetail, ReportDB, ReportCreate, ReportDBByID

from utils import create_pdf_report

router = APIRouter()


@router.get("/{report_id}", response_model=ReportDBByID)
def get_by_id(
        report_id: int,
        current_user: User = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
) -> ReportDBByID:
    """
    Returns a report via ID.
    """

    report_db = crud.report.get(db=db, id=report_id)

    if not report_db:
        raise HTTPException(
            status_code=400,
            detail="Report with ID:{} does not exist.".format(report_id)
        )

    return ReportDBByID(**report_db.__dict__)


@router.post("/{data_id}", response_model=ReportDB)
def create_by_data_id(
        data_id: int,
        current_user: User = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
) -> ReportDB:
    """
    Generate a report based off of a previously uploaded/queried data file.
    [Currently returns an example PDF file regardless of input json]
    """

    data_db = crud.data.get(db=db, id=data_id)

    if not data_db:
        raise HTTPException(
            status_code=400,
            detail="Data file with ID:{} does not exist.".format(data_id)
        )

    # Create DB entry
    report_db = crud.report.create(db=db, obj_in=ReportCreate(name=data_db.filename + " report.pdf", file="Temporary Example"))

    return ReportDB(**report_db.__dict__)


@router.get("/download/{report_id}")
def download_report(
        report_id: int,
        current_user: User = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db)
):
    """
    Download a generated report via ID.
    """

    report_db = crud.report.get(db=db, id=report_id)

    if not report_db:
        raise HTTPException(
            status_code=400,
            detail="Report with ID:{} does not exist.".format(report_id)
        )

    # Create the report (Example code, leftover after initial, albeit wrongly presumed, implementation)
    pdf = create_pdf_report(farm=FarmProfile(name="A", father_name="b", vat="c", head_office_details="d", phone=None,
                                             district="f", county="g", municipality="h", community="i", place_name="j",
                                             farm_area="k", plot_ids=[1, 2]),
                            mach=[MachineryAssetsOfFarm(index=1, description="a", serial_number="b",
                                                        date_of_manufacturing=datetime.date.today()),
                                  MachineryAssetsOfFarm(index=2, description="c", serial_number="d",
                                                        date_of_manufacturing=datetime.date.today())],
                            plot=PlotParcelDetail(plot_id=1, reporting_year=2024, cartographic="a", region="b",
                                                  toponym="c", area="200", nitro_area=True, natura_area=None,
                                                  pdo_pgi_area=True, irrigated=True, cultivation_in_levels=False,
                                                  ground_slope=False),
                            )

    # Return the report as a response (binary)
    headers = {
        "Content-Disposition": "attachment; filename={}".format(report_db.name)
    }

    return Response(content=bytes(pdf.output()), media_type="application/pdf", headers=headers)
