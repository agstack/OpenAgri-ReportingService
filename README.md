# Reporting Service

:eu: *"This service was created in the context of OpenAgri project (https://horizon-openagri.eu/). OpenAgri has received funding from the EU’s Horizon Europe research and innovation programme under Grant Agreement no. 101134083."*
# Description

The reporting service generates .pdf reports based on information present in datasets.\
These datasets are required to conform to the OCSM (OpenAgri Common Semantic Model) as well as be JSON-LD compliant.

# Requirements
<ul>
    <li>git</li>
    <li>docker</li>
    <li>docker-compose</li>
</ul>

Docker version used during development: 27.0.3

# Installation

There are two ways to install this service, via docker or directly from source.

<h3> Deploying from source </h3>

When deploying from source, use python 3:12.\
Also, you should use a [venv](https://peps.python.org/pep-0405/) when doing this.

A list of libraries that are required for this service is present in the "requirements.txt" file.\
This service uses FastAPI as a web framework to serve APIs, alembic for database migrations, fpdf2 for\
.pdf generation, sqlalchemy for database ORM mapping and pytest for testing purposes.

<h3> Pre commit hook </h3>

When working with repo after "requirements.txt" is installed \
```shell
pip install -r requirements.txt (inside activated venv)
```
run:
```shell
pre-commit install
```

When pre-commit enabled and installed, after every commit ruff and black formatters \
will be activated to resolve formatting of python files.
<h3> Deploying via docker </h3>

After installing <code> docker </code> you can run the following commands to run the application:

```
docker compose build
docker compose up
```

The application will be served on http://127.0.0.1:8009 (I.E. typing localhost/docs in your browser will load the swagger documentation)

Full list of APIs available you can check [here](https://editor-next.swagger.io/?url=https://gist.githubusercontent.com/JoleVLF/b1bcdd77ac82aeb115a6c94fb3dadbdc/raw/32df1d94947b67dcc70f730a629d7c91161e532f/api.json)
# Documentation
<h3>GET</h3>

```
/api/v1/openagri-report/{report_id}/
```

## Path Params

### report_id
- **Type**: `uuid str`
- **Description**: UUID of the generated PDF file..


## Response

Response is generated PDF file.

<h3>POST</h3>

```
/api/v1/openagri-report/irrigation-report/
```

## Request Params

### data
- **Type**: `UploadFile`
- **Description**: API processes the data directly to generate the report if data passed. This parameter is not required and when it is, must be provided as an `UploadFile`.



## Response

Response is uuid of generated PDF file.

<h3>POST</h3>

```
/api/v1/openagri-report/compost-report/
```

## Request Params 

### observation_type_name
- **Type**: `str`
- **Description**: The name of the observation type for the report. The value of this parameter must be one of the following options:
  - "Pesticides"
  - "Irrigation"
  - "Fertilization"
  - "CropStressIndicator"
  - "CropGrowthObservation"

### data
- **Type**: `UploadFile`
- **Description**: API processes the data directly to generate the report if data is passed. This parameter is not required and when it is, must be provided as an `UploadFile`.


## Response 
Response is uuid of generated PDF file.

<h3> Example usage </h3>

Compost and Irrigation Report APIs can be used with and without Gatekeeper support.
If Gatekeeper is used, data file param can be ignored.
When service is run without Gatekeeper data must be provided in .json file format.


```shell

/api/v1/openagri-report/animal-report/

```

## Request Params

### animal_group
- **Type**: `Optional[str]`
- **Description**: The group or category the animal belongs to. This is an optional string field, and it can be left as `None` if not applicable.

### name
- **Type**: `Optional[str]`
- **Description**: The name of the animal. It is an optional string field, and if no name is provided, it can be set to `None`.

### parcel
- **Type**: `Optional[UUID4]`
- **Description**: A unique identifier for a parcel, represented as a UUID4. This is an optional field that can be left empty if not required.

### status
- **Type**: `Optional[int]`
- **Description**: The status code associated with the animal or the transaction. It is an optional integer field. If not specified, it defaults to `None`.

### data
- **Type**: `UploadFile`
- **Description**: API processes the data directly to generate the report if data passed. This parameter is not required and when it is, must be provided as an `UploadFile`.

The Animal Report API can be used with or without Gatekeeper support:

With Gatekeeper: The data file parameter can be ignored.
Without Gatekeeper: Data must be provided in JSON file format.
If no data file is provided and Gatekeeper is not enabled, the API fetches data from an external Farm Calendar service. The request is made with the provided filters, and the system retrieves the necessary animal data.

If a valid JSON file is uploaded, the API processes the data directly to generate the report

## Response

Response is uuid of generated PDF file.

<h2>Pytest</h2>
Pytest can be run on the same machine the service has been deployed to by moving into the tests dir and running:

```
pytest tests_.py 
```

This will run the tests and return success values for each api tested in the terminal.

<h3>These tests will NOT result in generated .pdf files.</h3>

# Contribution
Please contact the maintainer of this repository.

# License
This project code is licensed under the EUPL 1.2 license, see the [LICENSE](https://github.com/agstack/OpenAgri-ReportingService/blob/main/LICENSE) file for more details.
Please note that each service may have different licenses, which can be found their specific source code repository.
