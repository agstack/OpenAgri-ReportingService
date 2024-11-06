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

<h3> Deploying via docker </h3>

After installing <code> docker </code> you can run the following commands to run the application:
```
docker compose build
docker compose up
```

The application will be served on http://127.0.0.1:80 (I.E. typing localhost/docs in your browser will load the swagger documentation)

# Documentation
Examples:
<h3>GET</h3>
```
/api/v1/openagri-report/{report_id}
```
Example response:
```
A .pdf file that contains the report
```
<h3>POST</h3>
```
/api/v1/openagri-report/{report_type}/dataset/{dataset_id}
```
Example response:
```
{
    "id": 1
}
```
<h3>DELETE</h3>
```
/api/v1/openagri-report/{report_id}
```
Example response:
```
{
    "message": "Successfully deleted report with ID:1"
}
```
<h3>GET</h3>
```
/api/v1/openagri-dataset/{dataset_id}
```
Example response:
```
{
  "@context": [
    "https://w3id.org/ocsm/main-context.jsonld"
  ],
  "@graph": [
    {
      "@id": "urn:openagri:pestMgmt:2ba53329-612c-47f3-a7f9-67f5f74f98f0",
      "@type": "ChemicalControlOperation",
      "description": "treatment description",
      "hasAppliedAmount": {
        "@id": "urn:openagri:pestMgmt:amount:762c62ca-bca2-464e-be18-94caf4596d3a",
        "@type": "QuantityValue",
        "numericValue": 1176,
        "unit": "http://qudt.org/vocab/unit/GM"
      },
      .
      .
      .
}
```
This response has been reduced in length, but the format should conform to the OCSM, as this format is expected when uploading.
<h3>POST<h3>
```
/api/v1/openagri-dataset/
```
Example response:
```
{
    "id": 1
}
```
<h3>DELETE</h3>
```
/api/v1/openagri-dataset/{dataset_id}
```
Example response:
```
{
    "message": "Successfully removed dataset with ID:1."
}
```


<h3> Example usage </h3>

In order to create a report, you need data for that report.\
For this, there are two main APIs that are of significance:\
1. POST localhost/api/v1/openagri-dataset/
2. POST localhost/api/v1/openagri-report/{report_type}/dataset/{dataset_id}

The first one is used to upload a dataset to the service.\
It returns the ID of the dataset.

The second one is used to generate a .pdf report, it takes an *ID* of a dataset\
and a *type* of report and generates it if the service finds the required data\
inside the dataset.\
The type can be any one of:\
*[work-book, plant-protection, irrigations, fertilisations, harvests, GlobalGAP]*

For more examples, please view the swagger documentation.

# Testing
Tests can be run on the same machine where it is deployed.\
They can be run by moving into the  ```/tests/``` dir and running ```pytest tests_.py``` \
This will run the tests on the machine and return response values for either passing or failing to run.

# Contribution
Please contact the maintainer of this repository.

# License
[European Union Public License 1.2](https://github.com/openagri-eu/reporting-service/blob/main/LICENSE)
