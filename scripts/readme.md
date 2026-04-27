This command-line script (report_client.py) provides a simple way to interact with the Reporting service. It allows you to request the generation of any supported report type (animal, irrigation, compost, pesticides, fertilization, standalone-observation) by uploading a corresponding JSON data file.

The script handles the entire workflow:

    It sends the initial request to start the PDF generation process.

    It waits and periodically checks the server's status.

    Once the PDF is ready, it downloads the file to the same directory where the script is run.

Prerequisites

    Python 3.6+

    The requests library. If you don't have it, install it via pip:

    pip install requests

    A valid authentication token from the reporting service.

    A correctly formatted JSON data file for the report you wish to generate.

Usage

The script is run from your terminal and accepts four command-line arguments.
```
python3 report_client.py --type <REPORT_TYPE> --token <YOUR_TOKEN> --file <PATH_TO_JSON> [--url <SERVICE_URL>]
```
Command-Line Arguments


| Argument | Required | Description |
|----------|----------|----|
| --type   | Yes      | The type of report to generate. One of animal, irrigation, compost, pesticides, fertilization, standalone-observation.  |
| --token  | Conditional | Your personal authentication bearer token. Required for **all** report types **except** standalone-observation, which is fully unauthenticated. |
| --file   | Yes      | The relative or absolute path to the JSON file containing the data for the report. |
| --url    | No       | The base URL of the reporting service. If not provided, it defaults to http://127.0.0.1:8009. |
| --title, --from-date, --to-date, --parcel-*, --farm-* | No | Manual parcel/farm fields, used only by `--type standalone-observation`. See the standalone section below. |

Example Commands
Animal Report
```
python3 report_client.py --type animal --token "your-auth-token-here" --file "./animal_data.json"
```
Irrigation Report
```
python3 report_client.py --type irrigation --token "your-auth-token-here" --file "data/irrigation_data.json"
```
Compost Report (with a custom URL)
```
python3 report_client.py --type compost --token "your-auth-token-here" --file "compost.json" --url "http://api.myfarm.com"
```

Standalone Observation Report

This endpoint is intended for environments where no Farm Calendar service is available
and **no authentication is required** (no token needed). Parcel and farm information
are NOT looked up from external services — they must be supplied manually as
command-line flags. The JSON file must be a **pure JSON-LD observation array**
(top-level `[ ... ]`), not the `{"@graph": [...]}` envelope used by the other endpoints.
See `standalone_observation_data.json` for an example.

```
python3 report_client.py --type standalone-observation \
    --file "./standalone_observation_data.json" \
    --title "Compost B-42 Observations" \
    --from-date 2025-10-10 --to-date 2025-10-12 \
    --parcel-address "Country: GR | City: Athens | Postcode: 10000" \
    --parcel-identifier "PARCEL-B42" \
    --parcel-area 12500 \
    --parcel-lat 37.9838 --parcel-lng 23.7275 \
    --farm-name "Demo Farm" \
    --farm-municipality "Athens" \
    --farm-administrator "John Doe" \
    --farm-vat-id "EL123456789" \
    --farm-contact-person "Jane Roe" \
    --farm-description "Demonstration compost farm."
```

When `--parcel-lat` and `--parcel-lng` are both provided, the report will also
include a Sentinel-2 satellite tile centered on those coordinates (network
permitting; the report still renders without it).

How It Works

    Generate Report: The script sends a POST request to the appropriate endpoint (e.g., /api/v1/openagri-report/animal-report/) with your token (when required) and JSON file. The server accepts the request and returns a unique uuid for the report job.

    Download PDF: The script then enters a loop, sending GET requests to the retrieval endpoint:

        - For all auth'd report types: /api/v1/openagri-report/<uuid>/ (with Bearer token).
        - For --type standalone-observation: /api/v1/openagri-report/standalone-observation-report/<uuid>/ (no Authorization header — the endpoint is intentionally unauthenticated and serves PDFs from a shared `standalone/` folder rather than a per-user folder).

        If the server responds with status 202 Accepted, it means the PDF is still being created, and the script waits a few seconds before trying again.

        If the server responds with 200 OK, the PDF is ready. The script writes the content to a new file named <uuid>.pdf.

        The script will retry up to 10 times before timing out.

Important Notes

    The success of the report generation depends entirely on providing a correctly formatted JSON file. If the server's validation fails, the PDF generation will fail.

    The final PDF file will be saved in the same directory from which you execute the script.