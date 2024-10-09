# MLOps study

All credits to @[mlops-study](https://github.com/mlops-study)

## Setup

This project hardly uses Docker, MariaDB and Apache Airflow.

First, we will create the docker network so that containers can communicate with each other.
```sh
docker network create mlops_study_network
```

Then, we will create the Jupyter container:
```sh
cd mlops-study-ml-env/jupyter

# execute docker-compose to run Jupyter
docker-compose up -d

# After few seconds, check the Jupyter container is running
docker ps
# check docker-compose logs
docker-compose logs

# go back to the root directory
cd ../..
```

Now, we could open jupyter notebook via web browser. For the authorization token, you can check the logs of the Jupyter container (`docker-compose logs`).

Next, we will create the MariaDB container.
To run the MariaDB on Docker run the following command:
```sh
cd mlops-study-ml-env/mariadb

# execute docker-compose to run MariaDB
docker-compose up -d

# After few seconds, check the MariaDB container is running
docker ps
# check docker-compose logs
docker-compose logs
```

By running the code above, both MariaDB and Adminer will be running on your local machine.
To access the Adminer, open your browser and type `http://localhost:8089` and use the following credentials:
- Server: db
- Username: root
- Password: root

## Run Airflow

To install and run airflow, run the following commands:
```sh
cd mlops-study-ml-pipeline/shell
sh airflow_install.sh
```
