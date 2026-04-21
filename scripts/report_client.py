#!/usr/bin/env python3
import requests
import time
import os
import argparse

# --- Configuration ---
# Maximum number of times to check for the PDF before giving up
MAX_RETRIES = 10
# Seconds to wait between check attempts
RETRY_DELAY_SECONDS = 3

# USAGE EXAMPLES:

# python report_client.py --type animal --token "your-long-auth-token-here" --file "path/to/animal_data.json"
# python report_client.py --type irrigation --token "your-long-auth-token-here" --file "data/irrigation_payload.json"
# python report_client.py --type pesticides --token "your-long-auth-token-here" --file "path/to/pesticides_data.json"
# python report_client.py --type fertilization --token "your-long-auth-token-here" --file "path/to/fertilization_data.json"
# python report_client.py --type compost --token "your-long-auth-token-here" --file "compost.json" --url "http://localhost:5000"
# standalone-observation does NOT require a token (auth is disabled for that endpoint):
# python report_client.py --type standalone-observation \
#     --file "standalone_observation_data.json" \
#     --farm-name "Demo Farm" --farm-municipality "Athens" \
#     --parcel-address "Country: GR | City: Athens | Postcode: 10000" \
#     --parcel-lat 37.9838 --parcel-lng 23.7275


# --- End Configuration ---

# Form fields supported by the standalone-observation endpoint
STANDALONE_FORM_FIELDS = (
    "title",
    "from_date",
    "to_date",
    "parcel_address",
    "parcel_identifier",
    "parcel_area",
    "parcel_lat",
    "parcel_lng",
    "farm_name",
    "farm_municipality",
    "farm_administrator",
    "farm_vat_id",
    "farm_contact_person",
    "farm_description",
)


def generate_report(
    report_type: str,
    base_url: str,
    token: str | None,
    json_file: str,
    form_fields: dict | None = None,
) -> str | None:
    """
    Calls the appropriate report endpoint and returns the report UUID.

    Args:
        report_type: The type of report ('animal', 'irrigation', 'pesticides',
            'fertilization', 'compost', 'standalone-observation').
        base_url: The base URL of the reporting service.
        token: The authentication bearer token (None for standalone-observation).
        json_file: The path to the JSON data file to upload.
        form_fields: Optional dict of multipart form fields (used by the
            standalone-observation endpoint to pass manual parcel/farm data).

    Returns:
        The report UUID string if successful, otherwise None.
    """
    # The API endpoint is dynamically constructed from the report_type
    report_url = f"{base_url}/api/v1/openagri-report/{report_type}-report/"
    print(f"➡️  Attempting to generate '{report_type}' report from '{json_file}'...")

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    try:
        with open(json_file, 'rb') as f:
            # The API expects the file in a multipart/form-data request
            files = {
                "data": (os.path.basename(json_file), f, "application/json")
            }
            response = requests.post(
                report_url,
                headers=headers,
                files=files,
                data=form_fields or None,
            )
            response.raise_for_status()  # Raises an exception for 4XX/5XX errors

        response_data = response.json()
        report_uuid = response_data.get("uuid")

        if not report_uuid:
            print("❌ Report generation failed: 'uuid' not found in the server response.")
            return None

        print(f"✅ Report generation started successfully. Report ID: {report_uuid}")
        return report_uuid

    except FileNotFoundError:
        print(f"❌ Error: The data file '{json_file}' was not found.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Report generation failed: {e}")
        if e.response is not None:
            print(f"   Server Response ({e.response.status_code}): {e.response.text}")
        return None


def download_pdf(
    report_uuid: str,
    base_url: str,
    token: str | None,
    report_type: str,
):
    """
    Polls the retrieval endpoint and downloads the generated PDF.
    The standalone-observation report uses a dedicated unauthenticated GET path.
    """
    print(f"⏳ Attempting to download PDF for report ID: {report_uuid}...")
    if report_type == "standalone-observation":
        pdf_url = f"{base_url}/api/v1/openagri-report/standalone-observation-report/{report_uuid}/"
        headers = {}
    else:
        pdf_url = f"{base_url}/api/v1/openagri-report/{report_uuid}/"
        headers = {"Authorization": f"Bearer {token}"} if token else {}

    for attempt in range(MAX_RETRIES):
        try:
            print(f"   Attempt {attempt + 1}/{MAX_RETRIES}... ", end="", flush=True)
            response = requests.get(pdf_url, headers=headers)

            if response.status_code == 202:
                print(f"PDF is still being generated. Retrying in {RETRY_DELAY_SECONDS}s...")
                time.sleep(RETRY_DELAY_SECONDS)
                continue

            response.raise_for_status()

            output_filename = f"{report_uuid}.pdf"
            with open(output_filename, 'wb') as f:
                f.write(response.content)
                f.flush()
                os.fsync(f.fileno())

            print(f"\n🎉 PDF downloaded successfully! Saved as '{output_filename}'")
            return

        except requests.exceptions.RequestException as e:
            print(f"\n❌ Failed to download PDF: {e}")
            if e.response is not None:
                print(f"   Server Response ({e.response.status_code}): {e.response.text}")
            return

    print(
        f"\n❌ Failed to retrieve PDF after {MAX_RETRIES} attempts. The report might still be processing or an error occurred on the server.")

def main():
    """
    Main function to parse arguments and run the reporting process.
    """
    parser = argparse.ArgumentParser(
        description="A command-line client to generate and download PDF reports from the reporting service.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "--type",
        required=True,
        choices=['animal', 'irrigation', 'compost', 'pesticides', 'fertilization', 'standalone-observation'],
        help="The type of report to generate."
    )
    parser.add_argument(
        "--token",
        default=None,
        help="Your authentication bearer token. Required for all report types EXCEPT standalone-observation."
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to the JSON data file to upload."
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8009",
        help="The base URL of the reporting service. (default: http://127.0.0.1:8009)"
    )

    # Manual parcel/farm fields used only by the standalone-observation endpoint.
    # All optional; sent as multipart form fields alongside the JSON file.
    standalone_group = parser.add_argument_group(
        "standalone-observation fields",
        "Manual parcel/farm data for --type standalone-observation (no Farm Calendar lookup).",
    )
    standalone_group.add_argument("--title", default=None, help="Report title (default: 'Observation Report').")
    standalone_group.add_argument("--from-date", default=None, help="Reporting period start (YYYY-MM-DD).")
    standalone_group.add_argument("--to-date", default=None, help="Reporting period end (YYYY-MM-DD).")
    standalone_group.add_argument("--parcel-address", default=None)
    standalone_group.add_argument("--parcel-identifier", default=None)
    standalone_group.add_argument("--parcel-area", default=None, help="Parcel area in m2.")
    standalone_group.add_argument("--parcel-lat", default=None, help="Parcel latitude (enables satellite image).")
    standalone_group.add_argument("--parcel-lng", default=None, help="Parcel longitude (enables satellite image).")
    standalone_group.add_argument("--farm-name", default=None)
    standalone_group.add_argument("--farm-municipality", default=None)
    standalone_group.add_argument("--farm-administrator", default=None)
    standalone_group.add_argument("--farm-vat-id", default=None)
    standalone_group.add_argument("--farm-contact-person", default=None)
    standalone_group.add_argument("--farm-description", default=None)

    args = parser.parse_args()

    if args.type != "standalone-observation" and not args.token:
        parser.error("--token is required for all report types except standalone-observation.")

    form_fields = None
    if args.type == "standalone-observation":
        # argparse stores --foo-bar as foo_bar; the endpoint expects the same names
        form_fields = {}
        for field in STANDALONE_FORM_FIELDS:
            value = getattr(args, field, None)
            if value is not None and value != "":
                form_fields[field] = value

    report_id = generate_report(args.type, args.url, args.token, args.file, form_fields)
    if report_id:
        download_pdf(report_id, args.url, args.token, args.type)


if __name__ == "__main__":
    main()