This command-line script (report_client.py) provides a simple way to interact with the Reporting service. It allows you to request the generation of three different types of reports (animal, irrigation, or compost) by uploading a corresponding JSON data file.

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
| --type   | Yes      | The type of report to generate. Must be one of animal, irrigation, or compost.  |
| --token  | Yes      | Your personal authentication bearer token for the service. |
| --file   | Yes      | The relative or absolute path to the JSON file containing the data for the report. |
| --url    | No       | The base URL of the reporting service. If not provided, it defaults to http://127.0.0.1:8009. |

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
How It Works

    Generate Report: The script sends a POST request to the appropriate endpoint (e.g., /api/v1/openagri-report/animal-report/) with your token and JSON file. The server accepts the request and returns a unique uuid for the report job.

    Download PDF: The script then enters a loop, sending GET requests to the retrieval endpoint (e.g., /api/v1/openagri-report/<uuid>/).

        If the server responds with status 202 Accepted, it means the PDF is still being created, and the script waits a few seconds before trying again.

        If the server responds with 200 OK, the PDF is ready. The script writes the content to a new file named <uuid>.pdf.

        The script will retry up to 10 times before timing out.

Important Notes

    The success of the report generation depends entirely on providing a correctly formatted JSON file. If the server's validation fails, the PDF generation will fail.

    The final PDF file will be saved in the same directory from which you execute the script.