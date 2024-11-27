import json
from pathlib import Path
import uuid
import sys

import report_service_utils as report_srv


# Function to generate a UUID with a specific prefix
def generate_uuid(prefix):
    return f"urn:openagri:{prefix}:{uuid.uuid4()}"


# Function to create the filename for the extracted AIM model in JSON-LD
def generate_aim_filename(generic_filename: str) -> str:
    return f'{Path("example", "datasets", generic_filename).stem}_AIM.jsonld'


# Function to map unit to vocabulary term
def get_unit_uri(unit):
    unit_mapping = {
        "gr/ha": "http://qudt.org/vocab/unit/GM",
        "ml/ha": "http://qudt.org/vocab/unit/ML",
    }
    return unit_mapping.get(unit, "")


# Function to convert parcel data to JSON-LD format and create a mapping from parcelUniqueIdentifier to parcelId
def convert_parcel_data(parcel_data_list):
    parcel_mapping = {}
    json_ld_parcels = []

    for parcel in parcel_data_list:
        parcel_id = generate_uuid("parcel")
        parcel_mapping[parcel.get("parcelUniqueIdentifier")] = parcel_id

        gis_data = parcel.get("gis", [{}])[0]

        parcel_entry = {
            "@id": parcel_id,
            "@type": "Vineyard",
            "identifier": parcel.get("parcelUniqueIdentifier", None),
            "description": parcel.get("description", None),
            "category": parcel.get("category", None),
            "validFrom": parcel.get("validFrom", None),
            "validTo": parcel.get("validTo", None),
            "inRegion": parcel.get("inRegion", None),
            "hasToponym": parcel.get("hasToponym", None),
            "area": (
                parcel.get("parcel_area") * 10000 if parcel.get("parcel_area") else None
            ),  # Convert Ha to m²
            "isNitroAarea": parcel.get("isNitroAarea", None),
            "isNatura2000Area": parcel.get("isNatura2000Area", None),
            "isPDOPGIArea": parcel.get("isPDOPGIArea", None),
            "isIrrigated": parcel.get("isIrrigated", None),
            "isCultivatedInLevels": parcel.get("isCultivatedInLevels", None),
            "isGroundSlope": parcel.get("isGroundSlope", None),
            "depiction": parcel.get("depiction", None),
            "hasGeometry": {
                "@id": generate_uuid("parcel:geo"),
                "@type": "Polygon",
                "asWKT": gis_data.get("wkt", None),
            },
            "location": {
                "@id": generate_uuid("parcel:point"),
                "@type": "Point",
                "lat": gis_data.get("latitude", None),
                "long": gis_data.get("longitude", None),
            },
            "usesIrrigationSystem": {
                "@id": generate_uuid("parcel:irrigation"),
                "@type": "IrrigationSystem",
                "name": parcel.get("irrigation_system", None),
            },
            "hasIrrigationFlow": parcel.get("irrigation_supply_rate", None),
        }

        json_ld_parcels.append(parcel_entry)

    return json_ld_parcels, parcel_mapping


# Function to convert farm data to JSON-LD format
def convert_farm_data(farm_data_list, json_ld_parcels):
    json_ld_farms = []

    for farm in farm_data_list:
        farm_id = generate_uuid("farm")

        # Link parcels associated with the farm
        farm_parcel_ids = farm.get("farm_parcel_ids", [])
        linked_parcels = [
            parcel
            for parcel in json_ld_parcels
            if parcel.get("identifier") in farm_parcel_ids
        ]

        farm_entry = {
            "@id": farm_id,
            "@type": "Farm",
            "name": farm.get("farmName", None),
            "description": farm.get("description", None),
            "hasAdministrator": farm.get("farmAdministratorName", None),
            "contactPerson": {
                "@id": generate_uuid("contact"),
                "@type": "Person",
                "firstname": farm.get("farmContactPerson", None),
                "lastname": farm.get("farmContactPerson", None),
            },
            "telephone": farm.get("telephone", None),
            "vatID": farm.get("vatID", None),
            "address": {
                "@id": generate_uuid("address"),
                "@type": "Address",
                "adminUnitL1": farm.get("adminUnitL1", None),
                "adminUnitL2": farm.get("adminUnitL2", None),
                "addressArea": farm.get("addressArea", None),
                "municipality": farm.get("municipality", None),
                "community": farm.get("community", None),
                "locatorName": farm.get("locatorName", None),
            },
            "area": (
                farm.get("totalFarmArea") * 10000 if farm.get("totalFarmArea") else None
            ),  # Convert Ha to m²
            "hasAgriParcel": linked_parcels,  # Link the parcels related to this farm
        }

        json_ld_farms.append(farm_entry)

    return json_ld_farms


# Function to convert pesticides data to JSON-LD format and associate it with the corresponding parcelId
def convert_pesticides_to_jsonld(pesticides_data, parcel_mapping):
    json_ld_pesticides = []

    for entry in pesticides_data:
        base_id = generate_uuid("pestMgmt")
        amount_id = generate_uuid("pestMgmt:amount")
        system_id = generate_uuid("pestMgmt:system")

        parcel_unique_identifier = entry.get("parcelUniqueIdentifier")
        parcel_id = parcel_mapping.get(parcel_unique_identifier)

        pesticides_entry = {
            "@id": base_id,
            "@type": "ChemicalControlOperation",
            "description": entry.get("remarks", "treatment description"),
            "hasAppliedAmount": {
                "@id": amount_id,
                "@type": "QuantityValue",
                "numericValue": entry.get("dose"),
                "unit": get_unit_uri(entry.get("unit")),
            },
            "hasTimestamp": entry.get("date"),
            "hasTreatedArea": "null",  # Assuming no treated area info provided
            "isOperatedOn": parcel_id,
            "isTargetedTowards": entry.get("target"),
            "usesPesticide": {
                "@id": system_id,
                "@type": "Pesticide",
                "hasActiveSubstance": entry.get("activeSubstance"),
                "hasCommercialName": entry.get("comercialDrugName"),
            },
        }

        json_ld_pesticides.append(pesticides_entry)

    return json_ld_pesticides


# Function to convert irrigation data to JSON-LD format and associate it with the corresponding parcelId
def convert_irrigation_to_jsonld(irrigation_data, parcel_mapping):
    json_ld_irrigation = []

    for entry in irrigation_data:
        base_id = generate_uuid("irrigation")
        amount_id = generate_uuid("irrigation:amount")
        system_id = generate_uuid("irrigation:system")

        parcel_unique_identifier = entry.get("parcelUniqueIdentifier")
        parcel_id = parcel_mapping.get(parcel_unique_identifier)

        irrigation_entry = {
            "@id": base_id,
            "@type": "IrrigationOperation",
            "description": "irrigation description",
            "startedAt": entry.get("startDateTime", None),
            "endedAt": entry.get("endDateTime", None),
            "hasAppliedAmount": {
                "@id": amount_id,
                "@type": "QuantityValue",
                "numericValue": entry.get("waterQuantity", None),
                "unit": (
                    "http://qudt.org/vocab/unit/M3"
                    if entry.get("unit") == "m3/Ha"
                    else None
                ),
            },
            "usesIrrigationSystem": {
                "@id": system_id,
                "@type": "IrrigationSystem",
                "name": entry.get("irrigationSystem", None),
                "hasIrrigationType": entry.get("irrigationSystem", None),
            },
            "isOperatedOn": parcel_id,
        }

        json_ld_irrigation.append(irrigation_entry)

    return json_ld_irrigation


# Function to convert fertilization data to JSON-LD format and associate it with the corresponding parcelId
def convert_fertilization_to_jsonld(fertilizations_data, parcel_mapping):
    json_ld_fertilization = []

    for entry in fertilizations_data:
        base_id = generate_uuid("fertilization")
        product_id = generate_uuid("fertilization:product")
        amount_id = generate_uuid("fertilization:amount")
        plan_id = generate_uuid("fertilization:plan")

        # Determine the correct unit vocabulary term
        if entry.get("unit") == "kg" and entry.get("referenceDose") == "per plant":
            unit_vocab = "https://w3id.org/ocsm/KiloGM-PER-PLANT"
        elif (
            entry.get("unit") == "liters"
            and entry.get("referenceDose") == "per hectare"
        ):
            unit_vocab = "https://w3id.org/ocsm/Litres-PER-Hectar"
        else:
            unit_vocab = None

        parcel_unique_identifier = entry.get("parcelUniqueIdentifier")
        parcel_id = parcel_mapping.get(parcel_unique_identifier)

        fertilization_entry = {
            "@id": base_id,
            "@type": "FertilizationOperation",
            "description": entry.get(
                "fertilization_description", "No description provided"
            ),
            "hasTimestamp": entry.get("date", None),
            "usesFertilizer": {
                "@id": product_id,
                "@type": "Fertilizer",
                "hasCommercialName": entry.get("product_name", None),
            },
            "hasAppliedAmount": {
                "@id": amount_id,
                "@type": "QuantityValue",
                "numericValue": entry.get("dose", None),
                "unit": unit_vocab,
            },
            "plan": {
                "@id": plan_id,
                "@type": "TreatmentPlan",
                "description": entry.get("remarks", "No plan description provided"),
            },
            "hasApplicationMethod": entry.get("fertilization_application_method", None),
            "operationType": entry.get("fertilization_application_method", None),
            "isOperatedOn": parcel_id,
        }

        json_ld_fertilization.append(fertilization_entry)

    return json_ld_fertilization


# Function to create a single combined JSON-LD file with all data under one "@graph" array
def create_combined_jsonld(
    irrigation_data, fertilizations_data, pesticides_data, parcel_data
):
    combined_json_ld = {
        "@context": ["https://w3id.org/ocsm/main-context.jsonld"],
        "@graph": [],
    }

    combined_json_ld["@graph"].extend(parcel_data)
    combined_json_ld["@graph"].extend(irrigation_data)
    combined_json_ld["@graph"].extend(fertilizations_data)
    combined_json_ld["@graph"].extend(pesticides_data)

    return combined_json_ld


def main():
    # Read the input JSON file from argv[1]
    input_file = sys.argv[1]

    with open(input_file, "r", encoding="utf-8") as file:
        input_data = json.load(file)

    irrigation_data = input_data.get("irrigation_data", [])
    fertilizations_data = input_data.get("fertilizations_data", [])
    pesticides_data = input_data.get("pesticides_data", [])
    farm_data_list = input_data.get("farm_related_data", [])
    parcel_data_list = input_data.get("parcel_related_data", [])

    # Convert parcel data and create a parcel mapping
    json_ld_parcels, parcel_mapping = convert_parcel_data(parcel_data_list)

    if irrigation_data or fertilizations_data or farm_data_list:
        choice = input(
            "Data found. Choose output option:\n"
            "1. Dump irrigation data to console\n"
            "2. Dump fertilization data to console\n"
            "3. Dump pesticides data to console\n"
            "4. Dump farm and parcel data to console\n"
            "5. Write all data to separate files\n"
            "6. Write all data to one combined JSON-LD file\n"
            "Enter choice (1/2/3/4/5/6): "
        )

        if choice == "1" and irrigation_data:
            converted_data = convert_irrigation_to_jsonld(
                irrigation_data, parcel_mapping
            )
            print(json.dumps(converted_data, indent=4))
        elif choice == "2" and fertilizations_data:
            converted_data = convert_fertilization_to_jsonld(
                fertilizations_data, parcel_mapping
            )
            print(json.dumps(converted_data, indent=4))
        elif choice == "3" and pesticides_data:
            converted_data = convert_pesticides_to_jsonld(
                pesticides_data, parcel_mapping
            )
            print(json.dumps(converted_data, indent=4))
        elif choice == "4" and farm_data_list:
            converted_farm_data = convert_farm_data(farm_data_list, json_ld_parcels)
            print(json.dumps(converted_farm_data, indent=4))
        elif choice == "5":
            dir_path = Path("example", "datasets")

            if irrigation_data:
                irrigation_output = convert_irrigation_to_jsonld(
                    irrigation_data, parcel_mapping
                )
                with open(
                    dir_path.joinpath("irrigation_output.jsonld"), "w"
                ) as irrig_file:
                    json.dump(irrigation_output, irrig_file, indent=4)
                print("Irrigation data written to irrigation_output.jsonld")

            if fertilizations_data:
                fertilization_output = convert_fertilization_to_jsonld(
                    fertilizations_data, parcel_mapping
                )
                with open(
                    dir_path.joinpath("fertilization_output.jsonld"), "w"
                ) as fert_file:
                    json.dump(fertilization_output, fert_file, indent=4)
                print("Fertilization data written to fertilization_output.jsonld")

            if pesticides_data:
                pesticides_output = convert_fertilization_to_jsonld(
                    pesticides_data, parcel_mapping
                )
                with open(
                    dir_path.joinpath("pesticides_output.jsonld"), "w"
                ) as pest_file:
                    json.dump(pesticides_output, pest_file, indent=4)
                print("Pesticides data written to fertilization_output.jsonld")

            if farm_data_list:
                farm_output = convert_farm_data(farm_data_list, json_ld_parcels)
                with open(dir_path.joinpath("farm_output.jsonld"), "w") as farm_file:
                    json.dump(farm_output, farm_file, indent=4)
                print("Farm data written to farm_output.jsonld")

        elif choice == "6":  # Combined JSON-LD file option
            irrigation_output = convert_irrigation_to_jsonld(
                irrigation_data, parcel_mapping
            )
            fertilization_output = convert_fertilization_to_jsonld(
                fertilizations_data, parcel_mapping
            )
            pesticides_output = convert_pesticides_to_jsonld(
                pesticides_data, parcel_mapping
            )
            farm_output = convert_farm_data(farm_data_list, json_ld_parcels)
            combined_output = create_combined_jsonld(
                irrigation_output, fertilization_output, pesticides_output, farm_output
            )

            aim_farm_calendar_filename = Path(
                "example", "datasets", generate_aim_filename(input_file)
            )

            with open(aim_farm_calendar_filename, "w") as combined_file:
                json.dump(combined_output, combined_file, indent=4)
            print("All data written to combined_output.jsonld")

            hasReport = input("Do you want to create a PDF report? (Y/N)")
            if hasReport == "Y":

                report_types = [
                    "work-book",
                    "plant-protection",
                    "irrigations",
                    "fertilisations",
                    "harvests",
                    "GlobalGAP",
                ]
                report_srv.register()
                token = report_srv.authenticate()
                dataset_id = report_srv.upload_dataset(
                    aim_farm_calendar_filename, token
                )
                report_srv.generate_reports_for_dataset(
                    dataset_id, report_types, token, isDownload=True
                )

        else:
            print("Invalid choice or no data for the selected option.")
    else:
        print("No recognizable data type found in the input file.")


if __name__ == "__main__":

    main()
