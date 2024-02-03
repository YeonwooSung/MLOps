# Simple Iris

- Apache-Airflow DAG workflow for sklearn iris dataest
- Use docker for operation

## Set up Airflow

Below are the instructions to set up Airflow admin account:

1. `docker ps` to check the container id

2. `docker exec -it <container_id> bash` to enter the container

3. `airflow users create --username admin --firstname <your_first_name> --lastname <your_last_name> --role Admin --email <your_email>`
