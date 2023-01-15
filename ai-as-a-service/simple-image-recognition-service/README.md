# Simple Image Recognition Service

This service provides a simple image recognition to users.

## Components

This service consists of the following components:

1. [Image crawler](./crawler-service/)
2. [Analysis service](./analysis-service/)
3. [UI service](./ui-service/)

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
