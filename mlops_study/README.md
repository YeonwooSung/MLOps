# MLOps study

All credits to @[mlops-study](https://github.com/mlops-study)

## Setup

This project hardly uses Docker, MariaDB and Apache Airflow.

To run the MariaDB on Docker run the following command:
```sh
cd mlops-study-ml-env/mariadb

# execute docker-compose to run MariaDB
docker-compose up -d

# After few seconds, check the MariaDB container is running
docker ps
# check docker-compose logs
docker-compose logs -f
```

By running the code above, both MariaDB and Adminer will be running on your local machine.
To access the Adminer, open your browser and type `http://localhost:8089` and use the following credentials:
- Server: db
- Username: root
- Password: root
