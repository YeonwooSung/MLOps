import os
import json
from typing import Union, Dict
from datetime import datetime

from airflow import DAG
from airflow.models import Variable
from airflow.decorators import task
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.bash import BashOperator

from support.callback_functions import success_callback, failure_callback

model_name = "ineligible_loan_model"
airflow_dags_path = Variable.get("AIRFLOW_DAGS_PATH")
os.environ['FEATURE_STORE_URL'] = f"mysql+pymysql://root:root@localhost/mlops_meta"
xcom_model_version_key = "ct_model_version"
xcom_training_cutoff_date_key = "training_cutoff_date"

# 추가
xcom_model_version_value = \
    "{{ ti.xcom_pull(key='" + xcom_model_version_key + "') }}"
xcom_training_cutoff_date_value = \
    "{{ ti.xcom_pull(key='" + xcom_training_cutoff_date_key + "') }}"
xcom_encoders_path_value = \
    f"data_preparation/{model_name}/ct/{xcom_training_cutoff_date_value}/encoders"
xcom_model_path_value = \
    f"model/{model_name}/{xcom_model_version_value}/{xcom_training_cutoff_date_value}"
service1 = "ineligible_loan_model_api_1"
service2 = "ineligible_loan_model_api_2"
api_env = {"MODEL_NAME": model_name,
           "MODEL_VERSION": xcom_model_version_value,
           "ENCODERS_PATH": xcom_encoders_path_value,
           "MODEL_PATH": xcom_model_path_value
           }


@task(task_id="CT모델버전조회")
def push_ct_model_version_to_xcom(**context):
    print(f"### type(context) = {type(context)}")
    print(f"### context = {context}")
    from support.model.model_version import ModelVersion
    model_version = ModelVersion(model_name=model_name)
    ct_model_version = model_version.get_final_ct_model_version()
    print(f"ct_model_version = {ct_model_version}")
    context['task_instance'].xcom_push(key=xcom_model_version_key,
                                       value=ct_model_version)
    print(f"###2 type(context) = {type(context)}")
    print(f"###2 context = {context}")


@task(task_id="CT모델학습기준일조회")
def push_training_cutoff_date_to_xcom(**context):
    from support.model.model_ct_logger import ModelCtLogger
    ct_model_version = \
        context['task_instance'].xcom_pull(key=xcom_model_version_key)
    print(f"ct_model_version = {ct_model_version}")
    model_ct_logger = ModelCtLogger(model_name=model_name,
                                    model_version=ct_model_version)
    training_cutoff_date = model_ct_logger.get_training_cutoff_date()
    print(f"training_cutoff_date = {training_cutoff_date}")
    context['task_instance'].xcom_push(key=xcom_training_cutoff_date_key,
                                       value=training_cutoff_date)


def _load_json(text: str) -> Union[Dict, None]:
    try:
        return json.loads(text)
    except json.decoder.JSONDecodeError as e:
        return None


def _get_api_services():
    api_services = []
    command = f"cd {airflow_dags_path}/models/ineligible_loan_model_cd && " \
              f"docker compose ps --filter status=running --format json"
    with os.popen(command) as cmd:
        outputs = cmd.read().split("\n")
    for output in outputs:
        api_services.append(_load_json(output))
    api_services = list(filter(None, api_services))
    return api_services


def get_next_branch():
    api_services = _get_api_services()
    expected_service_num = 2
    if api_services and len(api_services) == expected_service_num:
        task_id = "MODEL_API01_재시작"
    else:
        task_id = "서비스장애알림"
    return task_id


with DAG(dag_id="ineligible_loan_model_cd",
         default_args={
             "owner": "mlops.study",
             "depends_on_past": False,
             "email": ["mlops.study@gmail.com"],
             "on_failure_callback": failure_callback,
             "on_success_callback": success_callback,
         },
         description="부적격대출모델CD",
         schedule=None,
         start_date=datetime(2023, 10, 1),
         catchup=False,
         tags=["mlops", "study"],
         ) as dag:
    get_model_ver = push_ct_model_version_to_xcom()

    get_cutoff_date = push_training_cutoff_date_to_xcom()

    branching = BranchPythonOperator(
        task_id='대상서비스확인',
        python_callable=get_next_branch,
        dag=dag,
    )

    failure_notification = EmptyOperator(task_id="서비스장애알림")

    restart_api01 = BashOperator(
        task_id="MODEL_API01_재시작",
        bash_command=f"cd {airflow_dags_path}"
                     f"/models/ineligible_loan_model_cd && "
                     f"docker-compose stop {service1} && "
                     f"docker-compose rm -f {service1} && "
                     f"docker-compose up -d {service1}",
        env=api_env,
        append_env=True,
        retries=1,
    )

    restart_api02 = BashOperator(
        task_id="MODEL_API02_재시작",
        bash_command=f"cd {airflow_dags_path}"
                     f"/models/ineligible_loan_model_cd && "
                     f"docker-compose stop {service2} && "
                     f"docker-compose rm -f {service2} && "
                     f"docker-compose up -d {service2}",
        env=api_env,
        append_env=True,
        retries=1,
    )

    get_model_ver >> get_cutoff_date >> branching >> restart_api01 >> restart_api02
    branching >> failure_notification
