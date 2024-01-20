# Dockerfile
FROM python:3.11.7-bullseye

# set up environment variables
ENV AIRFLOW_HOME=/usr/local/airflow

# install dependencies
RUN apt-get update && \
    apt-get install -y gcc libc-dev vim && \
    rm -rf /var/lib/apt/lists/*

# install airflow
RUN pip install "apache-airflow==2.7.3" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.7.3/constraints-3.11.txt"

# set up airflow
RUN mkdir -p $AIRFLOW_HOME
WORKDIR $AIRFLOW_HOME
RUN airflow db migrate

# copy the DAG file into the dags folder
COPY my_dag.py $AIRFLOW_HOME/dags/

# expose airflow port
EXPOSE 8080

# run the webserver and scheduler
CMD airflow webserver -p 8080 & airflow scheduler
