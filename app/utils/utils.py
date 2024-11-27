import os
from typing import List

from fastapi import HTTPException
from fpdf import FPDF

from schemas import (
    FarmProfile,
    PlotParcelDetail,
    GenericCultivationInformationForParcel,
    Irrigation,
    PestManagement,
    Fertilization,
    Livestock,
)

import datetime


def parse_plant_protection(json: dict) -> List[PestManagement]:
    if "@graph" not in json:
        raise HTTPException(
            status_code=400, detail="Received json does not comply to expected format."
        )

    graph = json["@graph"]

    ppp = []

    for node in graph:
        if "@type" in node:
            if not node["@type"] == "ChemicalControlOperation":
                continue
        else:
            continue

        active_substance, product = "", ""
        if "usesPesticide" in node:
            active_substance = (
                node["usesPesticide"]["hasActiveSubstance"]
                if "hasActiveSubstance" in node["usesPesticide"]
                else ""
            )
            product = (
                node["usesPesticide"]["hasCommercialName"]
                if "hasCommercialName" in node["usesPesticide"]
                else ""
            )

        dose, unit = "", ""
        if "hasAppliedAmount" in node:
            dose = (
                node["hasAppliedAmount"]["numericValue"]
                if "numericValue" in node["hasAppliedAmount"]
                else ""
            )
            unit = (
                node["hasAppliedAmount"]["unit"].split("/")[-1]
                if "unit" in node["hasAppliedAmount"]
                and node["hasAppliedAmount"]["unit"] is not None
                else ""
            )

        date = None
        try:
            date = (
                datetime.datetime.strptime(node["hasTimestamp"], "%Y-%m-%d")
                if node["hasTimestamp"] is not None
                else None
            )
        except ValueError:
            print("Does this date exist: " + node["hasTimestamp"])

        enemy_target = (
            node["isTargetedTowards"] if node["isTargetedTowards"] is not None else ""
        )

        area = node["hasTreatedArea"] if node["hasTreatedArea"] is not None else ""

        treatment_description = (
            node["description"] if node["description"] is not None else ""
        )

        ppp.append(
            PestManagement(
                date=date,
                enemy_target=enemy_target,
                active_substance=active_substance,
                product=product,
                dose=dose,
                unit=unit,
                area=area,
                treatment_description=treatment_description,
            )
        )

    return ppp


def parse_irrigation(json: dict) -> List[Irrigation]:
    if "@graph" not in json:
        raise HTTPException(
            status_code=400, detail="Received json does not comply to expected format."
        )

    graph = json["@graph"]

    irri = []

    for node in graph:
        if "@type" in node:
            if not node["@type"] == "IrrigationOperation":
                continue
        else:
            continue

        started_date, ended_date = None, None
        try:
            started_date = (
                datetime.datetime.strptime(node["startedAt"], "%Y-%m-%d %H:%M:%S")
                if "startedAt" in node
                else None
            )
        except ValueError:
            print("Does this date exist: " + node["startedAt"])
        try:
            ended_date = (
                datetime.datetime.strptime(node["endedAt"], "%Y-%m-%d %H:%M:%S")
                if "endedAt" in node
                else None
            )
        except ValueError:
            print("Does this date exist: " + node["endedAt"])

        dose = ""
        unit = ""
        if "hasAppliedAmount" in node:
            dose = (
                node["hasAppliedAmount"]["numericValue"]
                if "numericValue" in node["hasAppliedAmount"]
                else ""
            )
            unit = (
                node["hasAppliedAmount"]["unit"].split("/")[-1]
                if "unit" in node["hasAppliedAmount"]
                and node["hasAppliedAmount"]["unit"] is not None
                else ""
            )

        watering_system = ""
        if "usesIrrigationSystem" in node:
            watering_system = (
                node["usesIrrigationSystem"]["hasIrrigationType"]
                if "hasIrrigationType" in node["usesIrrigationSystem"]
                else ""
            )

        irri.append(
            Irrigation(
                started_date=started_date,
                ended_date=ended_date,
                dose=dose,
                unit=unit,
                watering_system=watering_system,
            )
        )

    return irri


def parse_fertilization(json: dict) -> List[Fertilization]:

    if "@graph" not in json:
        raise HTTPException(
            status_code=400, detail="Received json does not comply to expected format."
        )

    graph = json["@graph"]

    ferts = []

    for node in graph:
        if "@type" in node:
            if not node["@type"] == "FertilizationOperation":
                continue
        else:
            continue

        product = ""
        if "usesFertilizer" in node:
            product = (
                node["usesFertilizer"]["hasCommercialName"]
                if "hasCommercialName" in node["usesFertilizer"]
                else ""
            )

        quantity, unit = "", ""
        if "hasAppliedAmount" in node:
            quantity = (
                node["hasAppliedAmount"]["numericValue"]
                if "numericValue" in node["hasAppliedAmount"]
                else ""
            )
            unit = (
                node["hasAppliedAmount"]["unit"].split("/")[-1]
                if "unit" in node["hasAppliedAmount"]
                and node["hasAppliedAmount"]["unit"] is not None
                else ""
            )

        form_of_treatment = None
        if "plan" in node:
            # TODO check with nikos if description is right info for this
            form_of_treatment = (
                node["plan"]["description"] if "description" in node["plan"] else ""
            )

        date = None
        try:
            date = (
                datetime.datetime.strptime(node["hasTimestamp"], "%Y-%m-%d").date()
                if "hasTimestamp" in node
                else None
            )
        except ValueError:
            print("Does this date exist: " + node["hasTimestamp"])

        # TODO ask nikos
        treatment_plan = ""

        operation_type = (
            node["operationType"] if node["operationType"] is not None else ""
        )

        treatment_description = (
            node["hasApplicationMethod"]
            if node["hasApplicationMethod"] is not None
            else ""
        )

        ferts.append(
            Fertilization(
                date=date,
                product=product,
                quantity=quantity,
                unit=unit,
                treatment_plan=treatment_plan,
                form_of_treatment=form_of_treatment,
                operation_type=operation_type,
                treatment_description=treatment_description,
            )
        )

    return ferts


def parse_plot_detail(json: dict) -> List[PlotParcelDetail]:
    if "@graph" not in json:
        raise HTTPException(
            status_code=400, detail="Received json does not comply to expected format."
        )

    graph = json["@graph"]

    details = []

    for node in graph:
        if "@type" in node:
            if not node["@type"] == "Farm":
                continue
        else:
            continue

        if "hasAgriParcel" not in node:
            continue

        for parcel in node["hasAgriParcel"]:

            plot_id = parcel["identifier"] if "identifier" in parcel else ""

            reporting_year = (
                int(parcel["validFrom"].split("-")[0])
                if "validFrom" in parcel and parcel["validFrom"] is not None
                else None
            )

            # TODO ask nikos
            cartographic = ""

            region = parcel["inRegion"] if "inRegion" in parcel else ""

            toponym = parcel["hasToponym"] if "hasToponym" in parcel else ""

            area = str(parcel["area"]) if "area" in parcel else ""

            nitro_area = (
                bool(parcel["isNitroAarea"])
                if "isNitroAarea" in parcel and parcel["isNitroAarea"] is not None
                else None
            )

            natura_area = (
                bool(parcel["isNatura2000Area"])
                if "isNatura2000Area" in parcel
                and parcel["isNatura2000Area"] is not None
                else None
            )

            pdo_pgi_area = (
                bool(parcel["isPDOPGIArea"])
                if "isPDOPGIArea" in parcel and parcel["isPDOPGIArea"] is not None
                else None
            )

            irrigated = (
                bool(parcel["isIrrigated"])
                if "isIrrigated" in parcel and parcel["isIrrigated"] is not None
                else None
            )

            cultivation_in_levels = (
                bool(parcel["isCultivatedInLevels"])
                if "isCultivatedInLevels" in parcel
                and parcel["isCultivatedInLevels"] is not None
                else None
            )

            ground_slope = (
                bool(parcel["isGroundSlope"])
                if "isGroundSlope" in parcel and parcel["isGroundSlope"] is not None
                else None
            )

            depiction = parcel["depiction"] if "depiction" in parcel else None

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
                    ground_slope=ground_slope,
                    depiction=depiction,
                )
            )

    return details


def parse_generic_cultivation_info(
    json: dict,
) -> List[GenericCultivationInformationForParcel]:
    if "@graph" not in json:
        raise HTTPException(
            status_code=400, detail="Received json does not comply to expected format."
        )

    graph = json["@graph"]

    gen = []

    for node in graph:
        if "@type" in node:
            if not node["@type"] == "Farm":
                continue
        else:
            continue

        if "hasAgriParcel" not in node:
            continue

        for parcel in node["hasAgriParcel"]:

            variety, production_direction, cultivation_type = "", "", ""
            if "hasAgriCrop" in parcel:
                cultivation_type = (
                    parcel["hasAgriCrop"]["name"]
                    if "name" in parcel["hasAgriCrop"]
                    else ""
                )

                if "cropSpecies" in parcel["hasAgriCrop"]:
                    variety = (
                        parcel["hasAgriCrop"]["cropSpecies"]["name"]
                        if "name" in parcel["hasAgriCrop"]["cropSpecies"]
                        else ""
                    )
                    production_direction = (
                        parcel["hasAgriCrop"]["isMeantFor"]
                        if "isMeantFor" in parcel["hasAgriCrop"]
                        else ""
                    )

            irrigated = (
                bool(parcel["isIrrigated"])
                if "isIrrigated" in parcel and parcel["isIrrigated"] is not None
                else None
            )

            # TODO ask nikos
            greenhouse = None

            # TODO ask nikos, these seem to not be present.
            planting_system = ""

            planting_distances_of_lines = None

            planting_distance_between_lines = None

            number_of_productive_trees = None

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
                    number_of_productive_trees=number_of_productive_trees,
                )
            )

    return gen


def parse_farm_profile(json: dict) -> FarmProfile:
    if "@graph" not in json:
        raise HTTPException(
            status_code=400, detail="Received json does not comply to expected format."
        )

    graph = json["@graph"]

    for node in graph:
        if "@type" in node:
            if not node["@type"] == "Farm":
                continue
        else:
            continue

        name = ""
        if "contactPerson" in node:
            name = (
                node["contactPerson"]["firstname"]
                if "firstname" in node["contactPerson"]
                else ""
            )
            name += (
                node["contactPerson"]["lastname"]
                if "lastname" in node["contactPerson"]
                and node["contactPerson"]["lastname"] is not None
                else ""
            )

        # TODO: ask nikos
        father_name = ""

        vat = node["vatID"] if "vatID" in node else ""

        # TODO: ask nikos
        head_office_details = ""

        phone = node["telephone"] if "telephone" in node else ""

        district, county, municipality, community, place_name = "", "", "", "", ""
        if "address" in node:
            district = (
                node["address"]["addressArea"]
                if "addressArea" in node["address"]
                else ""
            )
            county = (
                node["address"]["adminUnitL2"]
                if "adminUnitL2" in node["address"]
                else ""
            )
            municipality = (
                node["address"]["municipality"]
                if "municipality" in node["address"]
                else ""
            )
            community = (
                node["address"]["community"] if "community" in node["address"] else ""
            )
            place_name = (
                node["address"]["locatorName"]
                if "locatorName" in node["address"]
                else ""
            )

        farm_area = (
            str(node["area"]) if "area" in node and node["area"] is not None else ""
        )

        plot_ids = []
        if "hasAgriParcel" in node:

            for parcel in node["hasAgriParcel"]:

                if "identifier" in parcel:

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
            plot_ids=plot_ids,
        )


def parse_livestock(json: dict) -> List[Livestock]:
    # TODO to be updated when we know correct json-ld format
    if "@graph" not in json:
        raise HTTPException(
            status_code=400, detail="Received json does not comply to expected format."
        )

    graph = json["@graph"]
    livestock_list = []

    for node in graph:
        if "@type" in node:
            if node["@type"] != "Livestock":
                continue
        else:
            continue

        id = node.get("@id", None)
        name = node.get("name", None)
        type = node.get("type", None)
        category = node.get("category", None)
        breed = node.get("breed", None)
        color = node.get("color", None)
        gender = node.get("gender", None)

        birth_date = None
        if "birthDate" in node:
            try:
                birth_date = datetime.datetime.strptime(
                    node["birthDate"], "%Y-%m-%d"
                ).date()
            except ValueError:
                print("Invalid birth date format:", node["birthDate"])

        is_dam_owned = node.get("isDamOwned", None)
        sire_id = node.get("sireID", None)
        is_sire_owned = node.get("isSireOwned", None)
        loss_cause = node.get("lossCause", None)

        loss_date = None
        if "lossDate" in node:
            try:
                loss_date = datetime.datetime.strptime(
                    node["lossDate"], "%Y-%m-%d"
                ).date()
            except ValueError:
                print("Invalid loss date format:", node["lossDate"])

        sold_through = node.get("soldThrough", None)
        sale_amount = node.get("saleAmount", None)
        sale_weight = node.get("saleWeight", None)
        is_owned = node.get("isOwned", None)

        livestock_list.append(
            Livestock(
                id=id,
                name=name,
                type=type,
                category=category,
                breed=breed,
                color=color,
                gender=gender,
                birth_date=birth_date,
                is_dam_owned=is_dam_owned,
                sire_id=sire_id,
                is_sire_owned=is_sire_owned,
                loss_cause=loss_cause,
                loss_date=loss_date,
                sold_through=sold_through,
                sale_amount=sale_amount,
                sale_weight=sale_weight,
                is_owned=is_owned,
            )
        )

    return livestock_list


def harvests():
    pdf = EX()

    pdf.set_title("OpenAgri Reporting Template")

    pdf.add_page()

    add_fonts(pdf)

    pdf.set_font("FreeSerif", "B", 10)
    pdf.cell(40, 10, "Harvests")
    pdf.set_font("FreeSerif", "", 8)

    EX.ln(pdf)

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
    pdf = EX()

    pdf.set_title("OpenAgri Reporting Template")

    pdf.add_page()

    add_fonts(pdf)

    pdf.set_font("FreeSerif", "B", 10)
    pdf.cell(40, 10, "Fertilization")
    pdf.set_font("FreeSerif", "", 8)

    EX.ln(pdf)

    keys = [
        "Date",
        "Product",
        "Quantity",
        "Unit",
        "Treatment Plan",
        "Form of Treatment",
        "Operation Type",
        "Treatment Description",
    ]
    with pdf.table() as table:
        if len(ferts) != 0:
            row = table.row()
            for key in keys:
                row.cell(key)
            for fert in ferts:
                row = table.row()

                if fert.date is None:
                    row.cell(None)
                else:
                    row.cell(str(fert.date))

                row.cell(fert.product)
                row.cell(str(fert.quantity))
                row.cell(fert.unit)
                row.cell(fert.treatment_plan)
                row.cell(fert.form_of_treatment)
                row.cell(fert.operation_type)
                row.cell(fert.treatment_description)
        else:
            row = table.row()
            for key in keys:
                row.cell(key)
            row = table.row()
            for i in range(len(keys)):
                row.cell(None)

    return pdf


def irrigations(irgs: List[Irrigation]):
    pdf = EX()

    pdf.set_title("OpenAgri Reporting Template")

    pdf.add_page()

    add_fonts(pdf)

    pdf.set_font("FreeSerif", "B", 10)
    pdf.cell(40, 10, "Irrigation")
    pdf.set_font("FreeSerif", "", 8)

    EX.ln(pdf)

    keys = ["Started Date", "Ended Date", "Dose", "Unit", "Watering System"]
    with pdf.table() as table:
        if len(irgs) != 0:
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
        else:
            row = table.row()
            for key in keys:
                row.cell(key)
            row = table.row()
            for i in range(len(keys)):
                row.cell(None)

    return pdf


def plant_protection(ppp: List[PestManagement]):
    pdf = EX()

    pdf.set_title("OpenAgri Reporting Template")

    pdf.add_page()

    add_fonts(pdf)

    pdf.set_font("FreeSerif", "B", 10)
    pdf.cell(40, 10, "Plant Protection")
    pdf.set_font("FreeSerif", "", 8)

    EX.ln(pdf)

    keys = [
        "Date",
        "Enemy/Target",
        "Active Substance",
        "Product",
        "Dose",
        "Unit",
        "Area",
        "Treatment Description",
    ]
    with pdf.table() as table:
        if len(ppp) != 0:
            row = table.row()
            for key in keys:
                row.cell(key)
            for p in ppp:
                row = table.row()

                if p.date is None:
                    row.cell(p.date)
                else:
                    row.cell(str(p.date))

                row.cell(p.enemy_target)
                row.cell(p.active_substance)
                row.cell(p.product)
                row.cell(str(p.dose))
                row.cell(p.unit)
                row.cell(p.area)
                row.cell(p.treatment_description)
        else:
            row = table.row()
            for key in keys:
                row.cell(key)
            row = table.row()
            for i in range(len(keys)):
                row.cell(None)

    return pdf


def work_book(
    farm: FarmProfile,
    plot: List[PlotParcelDetail],
    cult: List[GenericCultivationInformationForParcel],
    irri: List[Irrigation],
    fert: List[Fertilization],
    pdmd: List[PestManagement],
):

    pdf = EX()

    pdf.set_title("OpenAgri Reporting Template")

    # 1

    pdf.add_page()
    add_fonts(pdf)

    pdf.set_font("FreeSerif", "B", 10)
    pdf.cell(40, 10, "1. Farm profile")
    pdf.set_font("FreeSerif", "", 8)

    EX.ln(pdf)

    keys = [
        "First name or surname",
        "Father's name",
        "VAT",
        "Head office details",
        "Phone",
        "District",
        "County",
        "Municipality",
        "Community",
        "Place name",
        "Farm area",
        "Plot IDs",
    ]

    with pdf.table() as table:
        if farm is not None:
            for key, value in zip(keys, list(farm.model_dump().values())):
                row = table.row()
                row.cell(key)
                if value is not None:
                    row.cell(str(value))
                else:
                    row.cell(value)
        else:
            for key in keys:
                row = table.row()
                row.cell(key)
                row.cell(None)

    EX.ln(pdf)

    # 2

    pdf.add_page()

    pdf.set_font("FreeSerif", "B", 10)
    pdf.cell(40, 10, "2. Machinery / Assets of Farm")
    pdf.set_font("FreeSerif", "", 8)

    EX.ln(pdf)

    keys = ["Index", "Description", "Serial Number", "Date of manufacturing"]
    with pdf.table() as table:
        row = table.row()
        for key in keys:
            row.cell(key)
        for i in range(1):
            row = table.row()
            for j in range(4):
                row.cell(None)

    # 3

    first = 1
    first_page = True

    if len(plot) == 0:
        pdf.add_page()

        pdf.set_font("FreeSerif", "B", 10)
        pdf.cell(40, 10, "3. Plot/parcel details")
        pdf.set_font("FreeSerif", "", 8)

        EX.ln(pdf)

        keys = [
            "Plot ID:",
            "Reporting Year:",
            "Cartographic:",
            "Region:",
            "Toponym:",
            "Area:",
            "Nitro area:",
            "Natura2000 area:",
            "PDO/PGI area:",
            "Irrigated:",
            "Cultivation in Levels:",
            "Ground slope:",
        ]
        with pdf.table() as table:
            for key in keys:
                row = table.row()
                row.cell(key)
                row.cell(None)

    else:
        for pt in plot:
            if first_page:
                pdf.add_page()

                pdf.set_font("FreeSerif", "B", 10)
                pdf.cell(40, 10, "3. Plot/parcel details")
                pdf.set_font("FreeSerif", "", 8)

                EX.ln(pdf)

                first_page = False
            else:
                pdf.add_page()

                pdf.cell(40, 10, "")

                EX.ln(pdf)

            keys = [
                "Plot ID:",
                "Reporting Year:",
                "Cartographic:",
                "Region:",
                "Toponym:",
                "Area:",
                "Nitro area:",
                "Natura2000 area:",
                "PDO/PGI area:",
                "Irrigated:",
                "Cultivation in Levels:",
                "Ground slope:",
            ]
            with pdf.table() as table:
                for key, value in zip(keys, list(pt.model_dump().values())):
                    row = table.row()
                    row.cell(key)
                    if value is not None:
                        row.cell(str(value))
                    else:
                        row.cell(value)

            EX.ln(pdf)

            if pt.depiction is not None:
                if pt.depiction.find("example") == -1:
                    pdf.image(name=pt.depiction, w=80, keep_aspect_ratio=True)
                else:
                    if first == 1:
                        pdf.image(
                            name="https://raw.githubusercontent.com/openagri-eu/OCSM/main/examples/parcel123001.jpeg",
                            w=80,
                            keep_aspect_ratio=True,
                        )
                        first = 2
                    else:
                        pdf.image(
                            name="https://raw.githubusercontent.com/openagri-eu/OCSM/main/examples/parcel123002.jpeg",
                            w=80,
                            keep_aspect_ratio=True,
                        )
            else:
                if first == 1:
                    pdf.image(
                        name="https://raw.githubusercontent.com/openagri-eu/OCSM/main/examples/parcel123001.jpeg",
                        w=80,
                        keep_aspect_ratio=True,
                    )
                    first = 2
                else:
                    pdf.image(
                        name="https://raw.githubusercontent.com/openagri-eu/OCSM/main/examples/parcel123002.jpeg",
                        w=80,
                        keep_aspect_ratio=True,
                    )

    EX.ln(pdf)

    # 4.
    pdf.add_page()

    pdf.set_font("FreeSerif", "B", 10)
    pdf.cell(40, 10, "4. Generic cultivation information for parcel")
    pdf.set_font("FreeSerif", "", 8)

    EX.ln(pdf)

    keys = [
        "Cultivation type",
        "Variety",
        "Irrigated",
        "Greenhouse",
        "Production direction",
        "Planting System:",
        "Planting distances of lines (m):",
        "Planting distances between lines (m):",
        "Number of productive trees:",
    ]

    if len(cult) == 0:
        with pdf.table() as table:
            for key in keys:
                row = table.row()
                row.cell(key)
                row.cell(None)

        EX.ln(pdf)

    else:
        for cl in cult:
            with pdf.table() as table:
                for key, value in zip(keys, list(cl.model_dump().values())):
                    row = table.row()
                    row.cell(key)
                    if value is not None:
                        row.cell(str(value))
                    else:
                        row.cell(value)

            EX.ln(pdf)

    # 5.
    pdf.add_page()

    pdf.set_font("FreeSerif", "B", 10)
    pdf.cell(40, 10, "5. Harvests")
    pdf.set_font("FreeSerif", "", 8)

    EX.ln(pdf)

    keys = ["Date", "Production Amount", "Unit"]
    with pdf.table() as table:
        row = table.row()
        for key in keys:
            row.cell(key)
        row = table.row()
        for i in range(3):
            row.cell(None)

    EX.ln(pdf)

    # 6.
    pdf.add_page()

    pdf.set_font("FreeSerif", "B", 10)
    pdf.cell(40, 10, "6. Irrigations")
    pdf.set_font("FreeSerif", "", 8)

    EX.ln(pdf)

    keys = ["Started Date", "Ended Date", "Dose", "Unit", "Watering System"]
    with pdf.table() as table:
        row = table.row()
        for key in keys:
            row.cell(key)

        if len(irri) == 0:
            row = table.row()
            row.cell(None)
            row.cell(None)
            row.cell(None)
            row.cell(None)
            row.cell(None)
        else:
            for ir in irri:
                row = table.row()
                row.cell(str(ir.started_date))
                row.cell(str(ir.ended_date))
                row.cell(str(ir.dose))
                row.cell(ir.unit)
                row.cell(ir.watering_system)

    # 7.
    pdf.add_page()

    pdf.set_font("FreeSerif", "B", 10)
    pdf.cell(40, 10, "7. Pest management")
    pdf.set_font("FreeSerif", "", 8)

    EX.ln(pdf)

    keys = [
        "Date",
        "Enemy/Target",
        "Active Substance",
        "Product",
        "Dose",
        "Unit",
        "Area",
        "Treatment Description",
    ]
    with pdf.table() as table:
        if len(pdmd) != 0:
            row = table.row()
            for key in keys:
                row.cell(key)
            for p in pdmd:
                row = table.row()
                if p.date is None:
                    row.cell(p.date)
                else:
                    row.cell(str(p.date))
                row.cell(p.enemy_target)
                row.cell(p.active_substance)
                row.cell(p.product)
                row.cell(str(p.dose))
                row.cell(p.unit)
                row.cell(p.area)
                row.cell(p.treatment_description)
        else:
            row = table.row()
            for key in keys:
                row.cell(key)
            row = table.row()
            for i in range(len(keys)):
                row.cell(None)

    EX.ln(pdf)

    # 8.
    pdf.add_page()

    pdf.set_font("FreeSerif", "B", 10)
    pdf.cell(40, 10, "8. Fertilisation")
    pdf.set_font("FreeSerif", "", 8)

    EX.ln(pdf)

    keys = [
        "Date",
        "Product",
        "Quantity",
        "Unit",
        "Treatment Plan",
        "Form of Treatment",
        "Operation Type",
        "Treatment Description",
    ]
    with pdf.table() as table:
        if len(fert) != 0:
            row = table.row()
            for key in keys:
                row.cell(key)

            for fe in fert:
                row = table.row()
                if fe.date is None:
                    row.cell(None)
                else:
                    row.cell(str(fe.date))

                row.cell(fe.product)
                row.cell(str(fe.quantity))
                row.cell(fe.unit)
                row.cell(fe.treatment_plan)
                row.cell(fe.form_of_treatment)
                row.cell(fe.operation_type)
                row.cell(fe.treatment_description)
        else:
            row = table.row()
            for key in keys:
                row.cell(key)
            row = table.row()
            for i in range(len(keys)):
                row.cell(None)

    return pdf


def livestock(lst: List[Livestock]):
    pdf = EX()

    pdf.set_title("OpenAgri Reporting Template")

    pdf.add_page()

    add_fonts(pdf)

    pdf.set_font("FreeSerif", "B", 10)
    pdf.cell(40, 10, "Livestock")

    EX.ln(pdf)

    keys_table_1 = [
        "ID",
        "Name",
        "Type",
        "Category",
        "Breed",
        "Color",
        "Gender",
    ]

    keys_table_2 = [
        "BirthDate",
        "Is Dam Owned?",
        "Sire ID",
        "Is Sire Owned?",
        "Loss Cause",
        "Loss Date",
        "Sold Through",
        "Sale Amount",
        "Sale Weight",
        "Is Owned?",
    ]

    pdf.set_font("FreeSerif", "B", 8)
    pdf.cell(40, 10, "Table 1: Basic Information")
    pdf.ln(10)

    with pdf.table() as table:
        row = table.row()
        for key in keys_table_1:
            row.cell(key, align="C")

        for lv in lst:
            pdf.set_font("FreeSerif", "", 8)
            row = table.row()
            row.cell(str(lv.id), align="C")
            row.cell(lv.name, align="C")
            row.cell(lv.type, align="C")
            row.cell(lv.category, align="C")
            row.cell(lv.breed, align="C")
            row.cell(lv.color, align="C")
            row.cell(lv.gender, align="C")

    EX.ln(pdf)

    pdf.set_font("FreeSerif", "B", 8)
    pdf.cell(40, 10, "Table 2: Additional Information")
    pdf.ln(10)

    with pdf.table() as table:
        row = table.row()
        for key in keys_table_2:
            row.cell(key, align="C")

        for lv in lst:
            pdf.set_font("FreeSerif", "", 8)
            row = table.row()
            row.cell(str(lv.birth_date) if lv.birth_date else "N/A", align="C")
            row.cell("Yes" if lv.is_dam_owned else "No", align="C")
            row.cell(str(lv.sire_id) if lv.sire_id else "N/A", align="C")
            row.cell("Yes" if lv.is_sire_owned else "No", align="C")
            row.cell(lv.loss_cause if lv.loss_cause else "N/A", align="C")
            row.cell(str(lv.loss_date) if lv.loss_date else "N/A", align="C")
            row.cell(lv.sold_through if lv.sold_through else "N/A", align="C")
            row.cell(str(lv.sale_amount) if lv.sale_amount else "N/A", align="C")
            row.cell(str(lv.sale_weight) if lv.sale_weight else "N/A", align="C")
            row.cell("Yes" if lv.is_owned else "No", align="C")

    return pdf


def add_fonts(pdf):
    fonts_folder_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "fonts"
    )

    pdf.add_font(
        "FreeSerif", "", os.path.join(fonts_folder_path, "FreeSerif.ttf"), uni=True
    )
    pdf.add_font(
        "FreeSerif", "B", os.path.join(fonts_folder_path, "FreeSerifBold.ttf"), uni=True
    )


class EX(FPDF):
    def header(self):
        self.image(
            "https://horizon-openagri.eu/wp-content/uploads/2023/12/Logo-Open-Agri-blue-1024x338.png",
            w=40.0,
            keep_aspect_ratio=True,
            x=160,
        )
