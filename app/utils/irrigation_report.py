from typing import List
from schemas.irrigation import *
from utils import EX


def parse_irr_jsonld_to_schema(jsonld: dict) -> List[SoilMoistureAggregation]:
    try:
        results = []
        for item in jsonld["@graph"]:
            # Parse period
            period = item["duringPeriod"]
            interval = Interval(
                hasBeginning=Instant(
                    inXSDDateTime=period["hasBeginning"]["inXSDDateTime"][:-1]
                ),
                hasEnd=Instant(inXSDDateTime=period["hasEnd"]["inXSDDateTime"][:-1]),
            )

            # Parse Saturation Analysis
            saturation = item["saturationAnalysis"]
            saturation_analysis = SaturationAnalysis(
                numberOfSaturationDays=saturation["numberOfSaturationDays"],
                hasSaturationDates=[
                    datetime.fromisoformat(d["@value"][:-1])
                    for d in saturation["hasSaturationDates"]
                ],
                hasFieldCapacities=[
                    QuantityValue(
                        numericValue=field["numericValue"],
                        unit=field["unit"],
                        atDepth=Measure(
                            hasNumericValue=float(field["atDepth"]["hasNumericValue"]),
                            hasUnit=field["atDepth"]["hasUnit"],
                        ),
                    )
                    for field in saturation["hasFieldCapacities"]
                ],
            )

            stress = item["stressAnalysis"]
            stress_analysis = StressAnalysis(
                numberOfStressDays=stress["numberOfStressDays"],
                hasStressDates=[
                    datetime.fromisoformat(d["@value"][:-1])
                    for d in stress["hasStressDates"]
                ],
                hasStressLevels=[
                    QuantityValue(
                        numericValue=level["numericValue"],
                        unit=level["unit"],
                        atDepth=Measure(
                            hasNumericValue=float(level["atDepth"]["hasNumericValue"]),
                            hasUnit=level["atDepth"]["hasUnit"],
                        ),
                    )
                    for level in stress["hasStressLevels"]
                ],
            )

            # Parse Irrigation Analysis
            irrigation = item["irrigationAnalysis"]
            irrigation_analysis = IrrigationAnalysis(
                numberOfIrrigationOperations=irrigation["numberOfIrrigationOperations"],
                numberOfHighDoseIrrigationOperations=irrigation[
                    "numberOfHighDoseIrrigationOperations"
                ],
                hasHighDoseIrrigationOperationDates=[
                    datetime.fromisoformat(d["@value"][:-1])
                    for d in irrigation["hasHighDoseIrrigationOperationDates"]
                ],
            )

            # Construct the main schema object
            aggregation = SoilMoistureAggregation(
                description=item["description"],
                duringPeriod=interval,
                numberOfPrecipitationEvents=item["numberOfPrecipitationEvents"],
                saturationAnalysis=saturation_analysis,
                stressAnalysis=stress_analysis,
                irrigationAnalysis=irrigation_analysis,
            )
            results.append(aggregation)
    except Exception as e:
        return None
    return results


def create_pdf_from_aggregations(aggregations: List[SoilMoistureAggregation]):
    pdf = EX()
    pdf.set_title("Soil Moisture Aggregation Report")
    pdf.add_page()

    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 10, "Soil Moisture Aggregations")
    pdf.ln(10)

    for agg in aggregations:
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 10, "Description:", ln=True)

        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 10, agg.description)
        pdf.ln(5)

        # Period Table
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 10, "Period Information", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.cell(
            0, 10, f"  Start: {agg.duringPeriod.hasBeginning.inXSDDateTime}", ln=True
        )
        pdf.cell(0, 10, f"  End: {(agg.duringPeriod.hasEnd.inXSDDateTime)}", ln=True)
        pdf.ln(5)

        # Saturation Analysis
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 10, "Saturation Analysis", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.cell(
            0,
            10,
            f"  Number of Saturation Days: {agg.saturationAnalysis.numberOfSaturationDays}",
            ln=True,
        )
        pdf.cell(
            0,
            10,
            f"  Saturation Dates: {', '.join([str(d) for d in agg.saturationAnalysis.hasSaturationDates])}",
            ln=True,
        )
        for field in agg.saturationAnalysis.hasFieldCapacities:
            pdf.cell(
                0,
                10,
                f"  Field Capacity: {field.numericValue}{field.unit} at {field.atDepth.hasNumericValue}{field.atDepth.hasUnit}",
                ln=True,
            )
        pdf.ln(5)

        # Stress Analysis
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 10, "Stress Analysis", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.cell(
            0,
            10,
            f"  Number of Stress Days: {agg.stressAnalysis.numberOfStressDays}",
            ln=True,
        )
        pdf.cell(
            0,
            10,
            f"  Stress Dates: {', '.join([str(d) for d in agg.stressAnalysis.hasStressDates])}",
            ln=True,
        )
        for level in agg.stressAnalysis.hasStressLevels:
            pdf.cell(
                0,
                10,
                f"  Stress Level: {level.numericValue}{level.unit} at {level.atDepth.hasNumericValue}{level.atDepth.hasUnit}",
                ln=True,
            )
        pdf.ln(5)

        # Irrigation Analysis
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 10, "Irrigation Analysis", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.cell(
            0,
            10,
            f"  Number of Irrigation Operations: {agg.irrigationAnalysis.numberOfIrrigationOperations}",
            ln=True,
        )
        pdf.cell(
            0,
            10,
            f"  High Dose Operations: {agg.irrigationAnalysis.numberOfHighDoseIrrigationOperations}",
            ln=True,
        )
        pdf.cell(
            0,
            10,
            f"  High Dose Dates: {', '.join([str(d) for d in agg.irrigationAnalysis.hasHighDoseIrrigationOperationDates])}",
            ln=True,
        )
        pdf.ln(10)

    return pdf
