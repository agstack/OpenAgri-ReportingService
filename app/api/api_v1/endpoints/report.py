import uuid

from fastapi import APIRouter, File, Depends, HTTPException, UploadFile, Response
from api import deps
from schemas import ReportDBID
from utils.json_handler import ReportHandler

router = APIRouter()


@router.post("/{report_type}/", response_model=ReportDBID)
async def generate_pdf_report(
    report_type: str, token=Depends(deps.get_current_user), data: UploadFile = None
):
    """
    Generate a report based off of a previously uploaded/queried data file.
    Types: [work-book, plant-protection, irrigations, fertilisations, harvests, GlobalGAP, livestock, forecast]
    """

    types = {
        "work_book": "work-book",
        "plant_protection": "plant-protection",
        "irrigation": "irrigations",
        "fertilisation": "fertilisations",
        "harvest": "harvests",
        "global_gap": "GlobalGAP",
        "livestock": "livestock",
        "compost": "compost",
    }

    if report_type not in types.values():
        raise HTTPException(
            status_code=400,
            detail="Report type {} isn't part of the offered types.".format(
                report_type
            ),
        )

    file = None
    if report_type != "harvests":
        if not data:
            raise HTTPException(status_code=400, detail="JSON-LD file is missing!")

        file_data = await data.read()
        try:
            file = file_data.decode("utf-8")
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Error during file decoding, .json file may be corrupted.",
            )

    report_pdf_handler = ReportHandler(file=file, file_type=report_type)
    pdf = report_pdf_handler.generate_pdf(token=token)

    if not pdf:
        raise HTTPException(
            status_code=400,
            detail=f"Reporting service failed during PDF generation. Error details: [Type: {report_pdf_handler}]",
        )

    headers = {
        "Content-Disposition": "attachment; filename={}-report-{}.pdf".format(
            report_type, uuid.uuid4()
        )
    }

    return Response(
        content=bytes(pdf.output()), media_type="application/pdf", headers=headers
    )
