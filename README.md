# reporting-service

# About

The reporting service is a service that generates .pdf reports based on information present in datasets.\
These datasets conform to the OCSM (OpenAgri Common Semantic Model) and are required to be JSON-LD compliant.

# Dependencies
This service depends on docker[27.0.3] and python[3.12]\
If you want to host it without using docker, then a python environment is recommended.

# Python libraries
A list of libraries that are required for this service is present in the "requirements.txt" file.\
This service uses FastAPI as a web framework to serve APIs, alembic for database migrations, fpdf2 for\
.pdf generation and sqlalchemy for database ORM mapping.

# Running
To run this service, first navigate to the root folder via terminal, and run:\
docker compose up\
Once it builds the database and backend service, you will be able to access it\
via localhost/docs, which will load the documentation.

# Usage
In order to create a report, you need data for that report.\
For this, there are two main APIs that are of significance:\
1. POST localhost/openagri-dataset/
2. POST localhost/openagri-report/{report_type}/dataset/{dataset_id}

The first one is used to upload a dataset to the service, this can be done\
via the documentation by uploading a file via the browser, or it can\
be called with a binary .json file in the body.\
It returns the ID of the dataset.

The second one is used to generate a .pdf report, it takes an *ID* of a dataset\
and a *type* of report and generates it if the service finds the required data\
inside the dataset.
The type can be any one of:\
*[work-book, plant-protection, irrigations, fertilisations, harvests, GlobalGAP]*