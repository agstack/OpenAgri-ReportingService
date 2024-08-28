from typing import List

from fpdf import FPDF

from schemas import FarmProfile, MachineryAssetsOfFarm, PlotParcelDetail, GenericCultivationInformationForParcel, \
    Harvest, Irrigation, PestManagement


def harvests():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(40, 10, "Harvests")
    pdf.set_font("helvetica", "", 8)
    FPDF.set_y(pdf, y=20)

    pdf.set_title("OpenAgri Reporting Template")

    keys = ["Date", "Production Amount", "Unit"]
    with pdf.table() as table:
        row = table.row()
        for key in keys:
            row.cell(key)
        row = table.row()
        for i in range(3):
            row.cell(None)

    return pdf


def fertilisation():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(40, 10, "Fertilization")
    pdf.set_font("helvetica", "", 8)
    FPDF.set_y(pdf, y=20)

    pdf.set_title("OpenAgri Reporting Template")

    keys = ["Date", "Product", "Quantity", "Unit", "Treatment Plan", "Form of Treatment", "Operation Type",
            "Treatment Description"]
    with pdf.table() as table:
        row = table.row()
        for key in keys:
            row.cell(key)
        for i in range(3):
            row = table.row()
            for j in range(8):
                row.cell(None)

    return pdf


def irrigations():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(40, 10, "Irrigation")
    pdf.set_font("helvetica", "", 8)
    FPDF.set_y(pdf, y=20)

    pdf.set_title("OpenAgri Reporting Template")

    keys = ["Started Date", "Ended Date", "Dose", "Unit", "Watering System"]
    with pdf.table() as table:
        row = table.row()
        for key in keys:
            row.cell(key)
        for i in range(3):
            row = table.row()
            for j in range(5):
                row.cell(None)

    return pdf


def plant_protection():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(40, 10, "Plant Protection")
    pdf.set_font("helvetica", "", 8)
    FPDF.set_y(pdf, y=20)

    pdf.set_title("OpenAgri Reporting Template")

    keys = ["Date", "Enemy/Target", "Active Substance", "Product", "Dose", "Unit", "Area", "Treatment Description"]
    with pdf.table() as table:
        row = table.row()
        for key in keys:
            row.cell(key)
        for i in range(3):
            row = table.row()
            for j in range(8):
                row.cell(None)

    return pdf


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

    pdf.set_title("OpenAgri Reporting Template")

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
    pdf.add_page()
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(40, 10, "4. Generic cultivation information for parcel")
    pdf.set_font("helvetica", "", 8)
    FPDF.set_y(pdf, y=20)

    keys = ["Cultivation type", "Variety", "Irrigated", "Greenhouse", "Production direction", "Planting System:", "Planting distances of lines (m):", "Planting distances between lines (m):", "Number of productive trees:"]
    with pdf.table() as table:
        for key in keys:
            row = table.row()
            row.cell(key)
            row.cell(None)

    # 5.
    FPDF.set_y(pdf, y=85)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(40, 10, "5. Harvests")
    pdf.set_font("helvetica", "", 8)
    FPDF.set_y(pdf, y=95)

    keys = ["Date", "Production Amount", "Unit"]
    with pdf.table() as table:
        row = table.row()
        for key in keys:
            row.cell(key)
        row = table.row()
        for i in range(3):
            row.cell(None)

    # 6.

    FPDF.set_y(pdf, y=110)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(40, 10, "6. Irrigations")
    pdf.set_font("helvetica", "", 8)
    FPDF.set_y(pdf, y=120)

    keys = ["Started Date", "Ended Date", "Dose", "Unit", "Watering System"]
    with pdf.table() as table:
        row = table.row()
        for key in keys:
            row.cell(key)
        for i in range(3):
            row = table.row()
            for j in range(5):
                row.cell(None)

    # 7.
    FPDF.set_y(pdf, y=150)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(40, 10, "7. Pest management")
    pdf.set_font("helvetica", "", 8)
    FPDF.set_y(pdf, y=159)

    keys = ["Date", "Enemy/Target", "Active Substance", "Product", "Dose", "Unit", "Area", "Treatment Description"]
    with pdf.table() as table:
        row = table.row()
        for key in keys:
            row.cell(key)
        for i in range(3):
            row = table.row()
            for j in range(8):
                row.cell(None)

    # 8.
    FPDF.set_y(pdf, y=195)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(40, 10, "8. Fertilisation")
    pdf.set_font("helvetica", "", 8)
    FPDF.set_y(pdf, y=204)

    keys = ["Date", "Product", "Quantity", "Unit", "Treatment Plan", "Form of Treatment", "Operation Type", "Treatment Description"]
    with pdf.table() as table:
        row = table.row()
        for key in keys:
            row.cell(key)
        for i in range(3):
            row = table.row()
            for j in range(8):
                row.cell(None)

    return pdf
