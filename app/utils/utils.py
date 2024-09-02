from typing import List

from fastapi import HTTPException
from fpdf import FPDF

from schemas import FarmProfile, MachineryAssetsOfFarm, PlotParcelDetail, GenericCultivationInformationForParcel, \
    Harvest, Irrigation, PestManagement, Fertilization

import datetime


def parse_plant_protection(json: dict) -> List[PestManagement]:
    try:
        graph = json["@graph"]

        ppp = []

        for node in graph:
            date = datetime.datetime.strptime(node["hasTimestamp"], "%Y-%m-%d") if node["hasTimestamp"] is not None else None

            enemy_target = node["isTargetedTowards"] if node["isTargetedTowards"] is not None else ""

            active_substance = node["usesPesticide"]["hasActiveSubstance"] if node["usesPesticide"]["hasActiveSubstance"] is not None else ""

            product = node["usesPesticide"]["hasCommercialName"] if node["usesPesticide"]["hasCommercialName"] is not None else ""

            dose = node["hasAppliedAmount"]["numericValue"] if node["hasAppliedAmount"]["numericValue"] is not None else ""

            unit = node["hasAppliedAmount"]["unit"].split("/")[-1] if node["hasAppliedAmount"]["unit"] is not None else ""

            area = node["hasTreatedArea"] if node["hasTreatedArea"] is not None else ""

            treatment_description = node["description"] if node["description"] is not None else ""

            ppp.append(
                PestManagement(
                    date=date,
                    enemy_target=enemy_target,
                    active_substance=active_substance,
                    product=product,
                    dose=dose,
                    unit=unit,
                    area=area,
                    treatment_description=treatment_description
                )
            )

        return ppp

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400,
            detail="Received json does not comply to expected format."
        )


def parse_irrigation(json: dict) -> List[Irrigation]:
    try:
        graph = json["@graph"]

        irgs = []

        for node in graph:
            started_date = datetime.datetime.strptime(node["startedAt"], "%Y-%m-%dT%H:%M:%S") if node["startedAt"] is not None else None

            ended_date = datetime.datetime.strptime(node["endedAt"], "%Y-%m-%dT%H:%M:%S") if node["endedAt"] is not None else None

            dose = node["hasAppliedAmount"]["numericValue"] if node["hasAppliedAmount"]["numericValue"] is not None else ""

            unit = node["hasAppliedAmount"]["unit"].split("/")[-1] if node["hasAppliedAmount"]["unit"] is not None else ""

            watering_system = node["usesIrrigationSystem"]["hasIrrigationType"] if node["usesIrrigationSystem"]["hasIrrigationType"] is not None else ""

            irgs.append(
                Irrigation(
                    started_date=started_date,
                    ended_date=ended_date,
                    dose=dose,
                    unit=unit,
                    watering_system=watering_system
                )
            )

        return irgs

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400,
            detail="Received json does not comply to expected format."
        )


def parse_fertilization(json: dict) -> List[Fertilization]:
    try:
        graph = json["@graph"]

        ferts = []

        for node in graph:
            date = datetime.datetime.strptime(node["hasTimestamp"], "%Y-%m-%dT%H:%M").date() if node["hasTimestamp"] is not None else None

            product = node["usesFertilizer"]["hasCommercialName"] if node["usesFertilizer"]["hasCommercialName"] is not None else ""

            quantity = node["hasAppliedAmount"]["numericValue"] if node["hasAppliedAmount"]["numericValue"] is not None else ""

            unit = node["hasAppliedAmount"]["unit"].split("/")[-1] if node["hasAppliedAmount"]["unit"] is not None else ""

            #TODO ask nikos
            treatment_plan = ""

            #TODO check with nikos if description is right info for this
            form_of_treatment = node["plan"]["description"] if node["plan"]["description"] is not None else ""

            operation_type = node["operationType"] if node["operationType"] is not None else ""

            treatment_description = node["hasApplicationMethod"] if node["hasApplicationMethod"] is not None else ""

            ferts.append(
                Fertilization(
                    date=date,
                    product=product,
                    quantity=quantity,
                    unit=unit,
                    treatment_plan=treatment_plan,
                    form_of_treatment=form_of_treatment,
                    operation_type=operation_type,
                    treatment_description=treatment_description
                )
            )

        return ferts

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400,
            detail="Received json does not comply to expected format."
        )


def parse_plot_detail(json: dict) -> List[PlotParcelDetail]:
    try:
        graph = json["@graph"]

        details = []

        index = 0

        for node in graph:
            plot_id = node["hasAgriParcel"][index]["identifier"] if node["hasAgriParcel"][index]["identifier"] is not None else ""

            reporting_year = int(node["hasAgriParcel"][index]["validFrom"].split("-")[0]) if node["hasAgriParcel"][index]["validFrom"] is not None else None

            # TODO ask nikos
            cartographic = ""

            region = node["hasAgriParcel"][index]["inRegion"] if node["hasAgriParcel"][index]["inRegion"] is not None else ""

            toponym = node["hasAgriParcel"][index]["hasToponym"] if node["hasAgriParcel"][index]["hasToponym"] is not None else ""

            area = str(node["hasAgriParcel"][index]["area"]) if node["hasAgriParcel"][index]["area"] is not None else ""

            nitro_area = bool(node["hasAgriParcel"][index]["isNitroAarea"]) if node["hasAgriParcel"][index]["isNitroAarea"] is not None else None

            natura_area = bool(node["hasAgriParcel"][index]["isNatura2000Area"]) if node["hasAgriParcel"][index]["isNatura2000Area"] is not None else None

            pdo_pgi_area = bool(node["hasAgriParcel"][index]["isPDOPGIArea"]) if node["hasAgriParcel"][index]["isPDOPGIArea"] is not None else None

            irrigated = bool(node["hasAgriParcel"][index]["isIrrigated"]) if node["hasAgriParcel"][index]["isIrrigated"] is not None else None

            cultivation_in_levels = bool(node["hasAgriParcel"][index]["isCultivatedInLevels"]) if node["hasAgriParcel"][index]["isCultivatedInLevels"] is not None else None

            ground_slope = bool(node["hasAgriParcel"][index]["isGroundSlope"]) if node["hasAgriParcel"][index]["isGroundSlope"] is not None else None

            index += 1

            details.append(
                PlotParcelDetail(
                    plot_id=plot_id,
                    reporting_year=reporting_year,
                    cartographic=cartographic,
                    region=region,
                    toponym=toponym,
                    area=area,
                    nitro_area=nitro_area,
                    natura_area=natura_area,
                    pdo_pgi_area=pdo_pgi_area,
                    irrigated=irrigated,
                    cultivation_in_levels=cultivation_in_levels,
                    ground_slope=ground_slope
                )
            )

        return details

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400,
            detail="Received json does not comply to expected format."
        )


def parse_generic_cultivation_info(json: dict) -> List[GenericCultivationInformationForParcel]:
    try:
        graph = json["@graph"]

        gen = []

        index = 0

        for node in graph:
            cultivation_type = node["hasAgriParcel"][index]["hasAgriCrop"]["name"] if node["hasAgriParcel"][index]["hasAgriCrop"]["name"] is not None else ""

            variety = node["hasAgriParcel"][index]["hasAgriCrop"]["cropSpecies"]["name"] if node["hasAgriParcel"][index]["hasAgriCrop"]["cropSpecies"]["name"] is not None else ""

            irrigated = bool(node["hasAgriParcel"][index]["isIrrigated"]) if node["hasAgriParcel"][index]["isIrrigated"] is not None else None

            # TODO ask nikos
            greenhouse = None

            production_direction = node["hasAgriParcel"][index]["hasAgriCrop"]["isMeantFor"] if node["hasAgriParcel"][index]["hasAgriCrop"]["isMeantFor"] is not None else ""

            # TODO ask nikos, these seem to not be present in the LD provided.
            planting_system = ""

            planting_distances_of_lines = None

            planting_distance_between_lines = None

            number_of_productive_trees = None

            index += 1

            gen.append(
                GenericCultivationInformationForParcel(
                    cultivation_type=cultivation_type,
                    variety=variety,
                    irrigated=irrigated,
                    greenhouse=greenhouse,
                    production_direction=production_direction,
                    planting_system=planting_system,
                    planting_distances_of_lines=planting_distances_of_lines,
                    planting_distance_between_lines=planting_distance_between_lines,
                    number_of_productive_trees=number_of_productive_trees
                )
            )

        return gen

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400,
            detail="Received json does not comply to expected format."
        )


def parse_farm_profile(json: dict) -> FarmProfile:
    try:
        graph = json["@graph"]

        for node in graph:
            name = ""
            if node["contactPerson"]["firstname"] is not None:
                name += node["contactPerson"]["firstname"]

            if name == "":
                name = node["contactPerson"]["lastname"]
            else:
                name += " " + node["contactPerson"]["lastname"]

            # TODO: ask nikos
            father_name = ""

            vat = ""
            if node["vatID"] is not None:
                vat = node["vatID"]

            # TODO: ask nikos
            head_office_details = ""

            # phone = ""
            # if node["telephone"] is not None:
            #     phone = node["telephone"]

            phone = node["telephone"] if node["telephone"] is not None else ""

            # district = ""
            # if node["address"]["addressArea"] is not None:
            #     district = node["address"]["addressArea"]

            district = node["address"]["addressArea"] if node["address"]["addressArea"] is not None else ""

            # county = ""
            # if node["address"]["adminUnitL2"] is not None:
            #     county = node["address"]["adminUnitL2"]

            county = node["address"]["adminUnitL2"] if node["address"]["adminUnitL2"] is not None else ""

            # municipality = ""
            # if node["address"]["municipality"] is not None:
            #     municipality = node["address"]["municipality"]

            municipality = node["address"]["municipality"] if node["address"]["municipality"] is not None else ""

            community = node["address"]["community"] if node["address"]["community"] is not None else ""

            place_name = node["address"]["locatorName"] if node["address"]["locatorName"] is not None else ""

            farm_area = str(node["area"]) if node["area"] is not None else ""

            plot_ids = []
            if node["hasAgriParcel"] is not None:
                for parcel in node["hasAgriParcel"]:
                    plot_ids.append(parcel["identifier"])

            return FarmProfile(
                name=name,
                father_name=father_name,
                vat=vat,
                head_office_details=head_office_details,
                phone=phone,
                district=district,
                county=county,
                municipality=municipality,
                community=community,
                place_name=place_name,
                farm_area=farm_area,
                plot_ids=plot_ids
            )

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400,
            detail="Received json does not comply to expected format."
        )


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


def fertilisation(ferts: List[Fertilization]):
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
        for fert in ferts:
            row = table.row()

            row.cell(str(fert.date))
            row.cell(fert.product)
            row.cell(str(fert.quantity))
            row.cell(fert.unit)
            row.cell(fert.treatment_plan)
            row.cell(fert.form_of_treatment)
            row.cell(fert.operation_type)
            row.cell(fert.treatment_description)

    return pdf


def irrigations(irgs: List[Irrigation]):
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
        for ir in irgs:
            row = table.row()

            row.cell(str(ir.started_date))
            row.cell(str(ir.ended_date))
            row.cell(str(ir.dose))
            row.cell(ir.unit)
            row.cell(ir.watering_system)

    return pdf


def plant_protection(ppp: List[PestManagement]):
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
        for p in ppp:
            row = table.row()

            row.cell(str(p.date))
            row.cell(p.enemy_target)
            row.cell(p.active_substance)
            row.cell(p.product)
            row.cell(str(p.dose))
            row.cell(p.unit)
            row.cell(p.area)
            row.cell(p.treatment_description)

    return pdf


def work_book(
        farm: FarmProfile,
        plot: List[PlotParcelDetail],
        cult: List[GenericCultivationInformationForParcel]
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
        for i in range(5):
            row = table.row()
            for j in range(4):
                row.cell(None)

    # 3.

    c = 1
    base_height = 150
    table_height = 40

    FPDF.set_y(pdf, y=145)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(40, 10, "3. Plot/parcel details")
    pdf.set_font("helvetica", "", 8)
    FPDF.set_y(pdf, y=155)

    for pt in plot:

        keys = ["Plot ID:", "Reporting Year:", "Cartographic:", "Region:", "Toponym:", "Area:", "Nitro area:", "Natura2000 area:", "PDO/PGI area:", "Irrigated:", "Cultivation in Levels:", "Ground slope:"]
        with pdf.table() as table:
            for key, value in zip(keys, list(pt.model_dump().values())):
                row = table.row()
                row.cell(key)
                if value is not None:
                    row.cell(str(value))
                else:
                    row.cell(value)

        pdf.set_y(base_height + (c * table_height))
        c += 1

    # 4.

    c = 1
    base_height = 60
    table_height = 40

    pdf.add_page()
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(40, 10, "4. Generic cultivation information for parcel")
    pdf.set_font("helvetica", "", 8)
    FPDF.set_y(pdf, y=20)

    for cl in cult:

        keys = ["Cultivation type", "Variety", "Irrigated", "Greenhouse", "Production direction", "Planting System:", "Planting distances of lines (m):", "Planting distances between lines (m):", "Number of productive trees:"]
        with pdf.table() as table:
            for key, value in zip(keys, list(cl.model_dump().values())):
                row = table.row()
                row.cell(key)
                if value is not None:
                    row.cell(str(value))
                else:
                    row.cell(value)

        pdf.set_y(base_height + (c * table_height))
        c += 1

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
