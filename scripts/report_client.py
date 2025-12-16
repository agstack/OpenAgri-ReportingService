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


# --- End Configuration ---

def generate_report(report_type: str, base_url: str, token: str, json_file: str) -> str | None:
    """
    Calls the appropriate report endpoint and returns the report UUID.

    Args:
        report_type: The type of report ('animal', 'irrigation', 'pesticides', 'fertilization', 'compost').
        base_url: The base URL of the reporting service.
        token: The authentication bearer token.
        json_file: The path to the JSON data file to upload.

    Returns:
        The report UUID string if successful, otherwise None.
    """
    # The API endpoint is dynamically constructed from the report_type
    report_url = f"{base_url}/api/v1/openagri-report/{report_type}-report/"
    print(f"➡️  Attempting to generate '{report_type}' report from '{json_file}'...")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        with open(json_file, 'rb') as f:
            # The API expects the file in a multipart/form-data request
            files = {
                "data": (os.path.basename(json_file), f, "application/json")
            }
            response = requests.post(report_url, headers=headers, files=files)
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


def download_pdf(report_uuid: str, base_url: str, token: str):
    """
    Polls the retrieval endpoint and downloads the generated PDF.
    """
    print(f"⏳ Attempting to download PDF for report ID: {report_uuid}...")
    pdf_url = f"{base_url}/api/v1/openagri-report/{report_uuid}/"

    headers = {
        "Authorization": f"Bearer {token}"
    }

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
        choices=['animal', 'irrigation', 'compost', 'pesticides', 'fertilization'],
        help="The type of report to generate."
    )
    parser.add_argument(
        "--token",
        required=True,
        help="Your authentication bearer token."
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

    args = parser.parse_args()

    report_id = generate_report(args.type, args.url, args.token, args.file)
    if report_id:
        download_pdf(report_id, args.url, args.token)


if __name__ == "__main__":
    main()