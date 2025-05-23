# Scikit-learn Iris classification model serving with FastAPI

This example shows how to serve a scikit-learn model with FastAPI.

## Components

* [Database](#database)
* [Train and Save the Model Locally](#train-and-save-the-model-locally)

## Database

In this example, we use the PostgreSQL database to store the Iris data.

We will use Docker to run the PostgreSQL database and the data generation script.
As you might know, 2 different containers cannot communicate with each other by default.
To make 2 or more containers communicate with each other, we need to create a Docker network.

However, making a Docker network whenever restarting the containers is a bit annoying.
To overcome this, we will use the `docker-compose` for the Container Orchestration.
Since typing the docker-compose commands every time is also annoying, we will create a Makefile to automate the process.

```bash
$ cd db_setup
$ make server
```

## Train and Save the Model Locally

Source codes for training and saving the model are in the `train_and_save_model` directory.

The codes in the `train_and_save_model` directory are dependent on the db container, so before running the codes in the `train_and_save_model` directory, we need to make sure that the db container is running.

```bash
$ cd train_and_save_model
$ make dependency
$ make init
```

After running the above commands, run the training script:

```bash
$ python db_train.py
```

Then, run the validation script:

```bash
$ python db_validate_and_save.py
```

## Use MLflow for model registry

To serve a better model, we need to train same model with different hyperparameters and compare the performance of the models.
Every single time you train a model, you need to save not only the trained model but also the hyperparameters and the performance of the model.
To manage all the models, we need a model registry.

First, we need a backend store db to save the hyperparameters and the performance of the models.
In this example, we will use the PostgreSQL database to save the hyperparameters and the performance of the models.

```
version: "3"

services:
  mlflow-backend-store:
    image: postgres:14.0
    container_name: mlflow-backend-store
    environment:
      POSTGRES_USER: mlflowuser
      POSTGRES_PASSWORD: mlflowpassword
      POSTGRES_DB: mlflowdatabase
    healthcheck:
      test: ["CMD", "pg_isready", "-q", "-U", "mlflowuser", "-d", "mlflowdatabase"]
      interval: 10s
      timeout: 5s
      retries: 5
```

Next, we need a model registry store to save the trained models.
In general, people use AWS S3, Azure Blob Storage, or Google Cloud Storage to save the trained models.
However, in this exmaple, we will use the [MinIO](https://en.wikipedia.org/wiki/MinIO) to save the trained models.

```
version: "3"

services:
  mlflow-artifact-store:
    image: minio/minio
    container_name: mlflow-artifact-store
    ports:
      - 9000:9000
      - 9001:9001
    environment:
      MINIO_ROOT_USER: minio
      MINIO_ROOT_PASSWORD: miniostorage
    command: server /data/minio --console-address :9001
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3
```

The main reason that we use the MinIO is that we can use the MinIO as a local S3 storage.
This means that the codes that use the S3 storage can be used without any modification.

```python
# Set environments
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:9000"
os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:5001"
os.environ["AWS_ACCESS_KEY_ID"] = "minio"
os.environ["AWS_SECRET_ACCESS_KEY"] = "miniostorage"
```

Then, we will build a MLflow server to manage the models.

```Dockerfile
FROM amd64/python:3.9-slim

RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U pip &&\
    pip install mlflow psycopg2-binary boto3

RUN cd /tmp && \
    wget https://dl.min.io/client/mc/release/linux-amd64/mc && \
    chmod +x mc && \
    mv mc /usr/bin/mc
```

After writing the Dockerfile, add the related lines to the `docker-compose.yml` file, so that the MLflow server can communicate with the backend store db and the model registry store.

```
services:
  mlflow-server:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: mlflow-server
    depends_on:
      mlflow-backend-store:
        condition: service_healthy
      mlflow-artifact-store:
        condition: service_healthy
    ports:
      - 5001:5000
    environment:
      AWS_ACCESS_KEY_ID: minio
      AWS_SECRET_ACCESS_KEY: miniostorage
      MLFLOW_S3_ENDPOINT_URL: http://mlflow-artifact-store:9000
    command:
      - /bin/sh
      - -c
      - |
        mc config host add mlflowminio http://mlflow-artifact-store:9000 minio miniostorage &&
        mc mb --ignore-existing mlflowminio/mlflow
        mlflow server \
        --backend-store-uri postgresql://mlflowuser:mlflowpassword@mlflow-backend-store/mlflowdatabase \
        --default-artifact-root s3://mlflow/ \
        --host 0.0.0.0
```

To run the docker-compose file, run the following command:

```bash
$ docker compose up -d
```

After successfully running the docker-compose file, you can access the MLflow server at `http://localhost:5001`.
Also, you can access the MinIO server at `http://localhost:9001`.

After the MLflow server is running, we are now ready to save and load the model to/from the MLflow server.
For the python script that saves the model to the MLflow server, see the [model_registry/save_model_to_registry.py](./model_registry/save_model_to_registry.py) file.
For the python script that loads the model from the MLflow server, see the [model_registry/load_model_from_registry.py](./model_registry/load_model_from_registry.py) file.

Running instructions:

```bash
# save the model to the MLflow server
$ python save_model_to_registry.py

# load the model from the MLflow server
$ python load_model_from_registry.py --model-name "sk_model" --run-id "YOUR_RUN_ID"
```

When running the `load_model_from_registry.py` script, you need to specify the model name and the run id.

The default model name is `sk_model`, so you can just use it if you do not change the model name.

For the run id, you can find it in the MLflow server:

![mlflow main page](./imgs/mlflow1.png)

![mlflow model page](./imgs/mlflow2.png)

## Model Deployment

Now, we are ready to deploy the model.
Download the trained model from the mlflow server.

```
$ python download_model.py --model-name sk_model --run-id <run-id>
```

To run the docker-compose file, run the following command:

```bash
$ docker compose up -d
```

## Kafka

If the input data is sort of streaming data, it is more efficient to use some MOM (Message Oriented Middleware) to handle the data.
Clearly, Kafka is one of the most popular MOMs.
Therefore, we will adopt Kafka to handle the streaming data.
For example codes and Dockerfiles to run Kafka, see the [kafka](./kafka/) directory.

## Handling Streaming Data

To handle the streaming data, we need to use the Kafka consumer to consume the data from the Kafka server.
All codes could be find in the [stream](./stream/) directory.

As this example uses Grafana for visualization, we could check the data in the Grafana dashboard.

![Grafana login](./imgs/grafana1.png)

![Grafana dashboard](./imgs/grafana2.png)
