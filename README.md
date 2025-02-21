# Reporting Service

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

# Documentation
<h3>POST</h3>

```
/api/v1/openagri-report/irrigation-report/
```

Response is generated PDF file.


<h3>POST</h3>

```
/api/v1/openagri-report/compost-report/
```

Response is generated PDF file.
Possible observation_type_name values = \
["Pesticides", "Irrigation", "Fertilization", "CropStressIndicator", "CropGrowthObservation"]


<h3> Example usage </h3>

Compost and Irrigation Report APIs can be used with and without Gatekeeper support.
If Gatekeeper is used, data file param can be ignored.
When service is run wihtout Gatekeeper data must be provided in .json file format.


```shell

/api/v1/openagri-report/animal-report/

```

Response: A generated PDF file containing the animal report.

Possible query parameters:

animal_group (Optional, string): Specifies the group of animals to include in the report.
name (Optional, string): Filters results by animal name.
parcel (Optional, UUID4): Identifies the specific parcel where the animals are located.
status (Optional, integer): Filters animals by their status.
Example Usage
The Animal Report API can be used with or without Gatekeeper support:

With Gatekeeper: The data file parameter can be ignored.
Without Gatekeeper: Data must be provided in JSON file format.
If no data file is provided and Gatekeeper is not enabled, the API fetches data from an external Farm Calendar service. The request is made with the provided filters, and the system retrieves the necessary animal data.

If a valid JSON file is uploaded, the API processes the data directly to generate the report

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
[European Union Public License 1.2](https://github.com/openagri-eu/reporting-service/blob/main/LICENSE)