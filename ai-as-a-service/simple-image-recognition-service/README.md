# Simple Image Recognition Service

This service provides a simple image recognition to users.

## Components

This service consists of the following components:

- [image crawler](./crawler-service/)

### Crawler service

The main aim of the crawler service is to crawl images from the web and store them in the S3 bucket.
After downloading images to the S3 bucket, the crawler service will send an analysis request to the analysis service via SQS queue.
