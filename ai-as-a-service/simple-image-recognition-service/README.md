# Simple Image Recognition Service

This service provides a simple image recognition to users.

## Pre-requisites

Before deploying this service, you should have the following:

1) Set up AWS account, and configure AWS CLI with your credentials.
2) Install serverless framework.
3) Install node.js and npm.
4) Set up S3 bucket and SQS queue.
5) Set up AWS Rekognition service.
6) Set up a domain name and a certificate for the domain name.
7) Set suitable values to the environment variables in the serverless.yml in each service directory.
    a) [crawler-service/serverless.yml](./crawler-service/serverless.yml)
    b) [analysis-service/serverless.yml](./analysis-service/serverless.yml)
    c) [ui-service/serverless.yml](./ui-service/serverless.yml)
8) Open [frontend-service/app/code.js](./frontend-service/app/code.js) and set the proper values to BUCKET_ROOT and API_ROOT.

## Deploy and remove

If your AWS account is setup and and you have configured the following environment variables in your shell:

```sh
AWS_ACCOUNT_ID
AWS_DEFAULT_REGION
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
SIRS_BUCKET
SIRS_DOMAIN
```

Then the system can be deployed using:

```
$ bash ./deploy.sh
```

The system can be reomved using:

```
$ bash ./remove.sh
```

## Components

This service consists of the following components:

1. [Image crawler](./crawler-service/)
2. [Analysis service](./analysis-service/)
3. [UI service](./ui-service/)
4. [Frontend service](./frontend-service/)

### Crawler service

The main aim of the crawler service is to crawl images from the web and store them in the S3 bucket.
After downloading images to the S3 bucket, the crawler service will send an analysis request to the analysis service via SQS queue.
The crawler service works asynchronously for flexibility.

### Analysis service

The analysis service downloads images from the crawler service and analyzes them using the AWS Rekognition service.
All images that are sent from the crawler service are passed to the AWS Rekognition service.
The Rekognition service returns the set of labels that are associated with the image.
Each label has a confidence score that indicates the accuracy of the label.
The confidence score is a value between 0 and 100, where 100 means that the label is 100% accurate.
The analysis service generates word cloud with returned labels and stores it in the S3 bucket.
The analysis service works asynchronously for flexibility.

### UI service

The UI service provides 3 functionalities to support frontend service: 1) get list of URLs that are submitted for analysis, 2) get images that are related to the specific URL, and 3) submit a new URL for analysis.

To run this service, you should set a proper environment variable for domain and domain arn.
These variables could be found in [./ui-service/serverless.yml file](./ui-service/serverless.yml).
After setting proper values to the variables in the environment section, you could deploy the service successfully.

Also, deploying this service requires the "APIGatewayAdministrator" policy to be attached to the IAM role that is used for deployment.

### Frontend service

The frontend part of the entire service.
It is simply consisted with pure HTML, CSS, and JavaScript files.
Thus, unlike other microservices in this application, this service is not implemented with serverless framework, but directly deployed to the S3 bucket.

Since this service requries neither complex logics nor awesome UX functionalities, it is implemented with simple HTML, CSS, and JavaScript files.
Frameworks or libraries such as React, Vue, or Angular are not necessary for this service.
Always, simple is the best!
