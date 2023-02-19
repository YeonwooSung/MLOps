# Scikit-learn Iris classification model serving with FastAPI

This example shows how to serve a scikit-learn model with FastAPI.

## Components

* [Database](#database)

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

## Train and Save the Model

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
