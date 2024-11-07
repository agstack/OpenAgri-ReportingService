import requests


REPORTING_SERVICE_URL = "http://localhost:80"

def register():
    r = requests.post(
        url=REPORTING_SERVICE_URL + "/api/v1/user/register/",
        json={"email": "test.test@example.com", "password": "Test123321"}
    )

    return None

# This function is used to authenticate to the reporting service by making a POST request
# to the "/api/v1/login/access-token/" endpoint using a predefined username and password.
# It retrieves the access token from the response and returns it.
# If the authentication request fails (non-200 status code), the function returns nothing.
def authenticate() -> str:
    r = requests.post(
    REPORTING_SERVICE_URL + "/api/v1/login/access-token/",
        data={'username': 'test.test@example.com', 'password': 'Test123321'},
        timeout=10
    )
    token = r.json()['access_token']

    if r.status_code != 200:
        return

    return token


# Makes a POST request to upload the dataset to the reporting service.
# The Authorization header is set using the provided token.
# The file at the specified file path is included in the request as the 'data' payload.
# If the request is successful, extracts the dataset ID from the response.
def upload_dataset(farm_calendar_aim_filepath: str, token: str) -> int:
    r = requests.post(
        REPORTING_SERVICE_URL + "/api/v1/openagri-dataset/",
        headers={'Authorization': f'Bearer {token}'},
        # Define the file to upload
        files = {
            # 'data': json.dumps(combined_output)
            'data': open(farm_calendar_aim_filepath, 'rb')
            },
        timeout=5
        )

    if r.status_code != 200:
        return

    dataset_id = r.json()['id']
    print(f'Dataset uploaded with id: {dataset_id}')
    return dataset_id

# Makes a POST request to generate a report based on a dataset ID and report type.
# The Authorization header is set using the provided token.
# If the request is successful, extracts the report ID from the response.
# If the request fails (status_code != 200), it returns None.
def generate_report(dataset_id: int, report_type: str, token: str) -> int:
    r = requests.post(
        REPORTING_SERVICE_URL + f"/api/v1/openagri-report/{report_type}/dataset/{dataset_id}",
        headers={'Authorization': f'Bearer {token}'},
        timeout=5
    )

    if r.status_code != 200:
        return

    report_id = r.json()['id']
    print(f'{report_type} report created with id: {report_id}')
    return report_id


# Makes a GET request to download a report using the provided report ID.
# The Authorization header is set using the provided token.
# If the request is successful, writes the report content to a PDF file named 'report_<report_id>.pdf'.
# If the request fails (status_code != 200), it returns None.
def download_report(report_id: int, token: str, report_type=None):
    r = requests.get(
        REPORTING_SERVICE_URL + f"/api/v1/openagri-report/{report_id}",
        headers={'Authorization': f'Bearer {token}'},
        timeout=5
    )

    if r.status_code != 200:
        return

    from pathlib import Path

    pdf_report = r.content
    report_name = f'report_{report_id}_{report_type}.pdf' if report_type else f'report_{report_id}'
    with open(Path("example", "reports", report_name), 'wb') as pdf:
        pdf.write(pdf_report)
    print(f'Downloaded report: {report_name} for report with id: {report_id}')
    return report_name


def generate_reports_for_dataset(dataset_id: str, types: list, token: str, isDownload: bool=True):

    report_ids = []
    for t in types:
        report_ids.append((generate_report(dataset_id, t, token), t))

    if not isDownload:
        return

    report_names = []
    for id, report_type in report_ids:
        report_names.append(download_report(id, token, report_type))

    print("All reports downloaded!\n"
          f"{report_names}\n")
