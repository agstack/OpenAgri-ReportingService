# Reporting Service

# Description

The reporting service generates .pdf reports based on information present in datasets.\
These datasets are to required conform to the OCSM (OpenAgri Common Semantic Model) as well as be JSON-LD compliant.

# Requirements
<ul>
    <li>git</li>
    <li>docker</li>
    <li>docker-compose</li>
</ul>

Docker version used during development: 27.0.3

# Installation
After installing <code> docker </code> you can run the following commands to run the application:
```
docker compose build
docker compose up
```

The application will be served on http://127.0.0.1:80 (I.E. typing localhost/docs in your browser will load the swagger documentation)

# Documentation.
Examples:
<h3>POST</h1>
/api/v1/openagri-report/{report_type}/dataset/{dataset_id}
<h3>GET</h3>
/api/v1/openagri-dataset/{dataset_id}

\
For more examples, please view the swagger documentation.

# Contribution
Please contact the maintainer of this repository.

# License
<a html="https://github.com/openagri-eu/reporting-service/blob/main/LICENSE">European Union Public License 1.2</a>

# Other
If attempting to deploy without docker, then python:3.12 is required.\
Use a <a href="https://peps.python.org/pep-0405/">venv</a> when doing a direct deployment.


# Python libraries
A list of libraries that are required for this service is present in the "requirements.txt" file.\
This service uses FastAPI as a web framework to serve APIs, alembic for database migrations, fpdf2 for\
.pdf generation, sqlalchemy for database ORM mapping and pytest for testing purposes.

# Example Usage
In order to create a report, you need data for that report.\
For this, there are two main APIs that are of significance:\
1. POST localhost/openagri-dataset/
2. POST localhost/openagri-report/{report_type}/dataset/{dataset_id}

The first one is used to upload a dataset to the service.\
It returns the ID of the dataset.

The second one is used to generate a .pdf report, it takes an *ID* of a dataset\
and a *type* of report and generates it if the service finds the required data\
inside the dataset.\
The type can be any one of:\
*[work-book, plant-protection, irrigations, fertilisations, harvests, GlobalGAP]*