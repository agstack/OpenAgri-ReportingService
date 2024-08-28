from typing import List

from fpdf import FPDF

from schemas import FarmProfile, MachineryAssetsOfFarm, PlotParcelDetail, GenericCultivationInformationForParcel, \
    Harvest, Irrigation, PestManagement


def create_pdf_report(
        farm: FarmProfile,
        mach: List[MachineryAssetsOfFarm],
        plot: PlotParcelDetail,
        # cult: GenericCultivationInformationForParcel,
        # harv: Harvest,
        # irri: Irrigation,
        # pemg: PestManagement
):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(40, 10, "1. Farm profile")
    pdf.set_font("helvetica", "", 8)
    FPDF.set_y(pdf, y=20)

    # 1.
    keys = ["First name or surname:", "Father's name:", "VAT:", "Head office details:", "Phone:", "District:", "County:", "Municipality:", "Community:", "Place name:", "Farm area:", "Plot IDs:"]

    with pdf.table() as table:
        for key, value in zip(keys, list(farm.model_dump().values())):
            row = table.row()
            row.cell(key)
            if value is not None:
                row.cell(str(value))
            else:
                row.cell(value)

    FPDF.set_y(pdf, y=100)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(40, 10, "2. Machinery / Assets of Farm")
    pdf.set_font("helvetica", "", 8)
    FPDF.set_y(pdf, y=110)

    # 2.
    keys = ["Index", "Description", "Serial Number", "Date of manufacturing"]
    with pdf.table() as table:
        row = table.row()
        for key in keys:
            row.cell(key)
        for value in mach:
            row = table.row()
            row.cell(str(value.index))
            row.cell(value.description)
            row.cell(value.serial_number)
            row.cell(str(value.date_of_manufacturing))

    # 3.

    FPDF.set_y(pdf, y=140)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(40, 10, "3. Plot/parcel details")
    pdf.set_font("helvetica", "", 8)
    FPDF.set_y(pdf, y=150)

    keys = ["Plot ID:", "Reporting Year:", "Cartographic:", "Region:", "Toponym:", "Area:", "Nitro area:", "Natura2000 area:", "PDO/PGI area:", "Irrigated:", "Cultivation in Levels:", "Ground slope:"]
    with pdf.table() as table:
        for key, value in zip(keys, list(plot.model_dump().values())):
            row = table.row()
            row.cell(key)
            if value is not None:
                row.cell(str(value))
            else:
                row.cell(value)

    # 4.

    return pdf
