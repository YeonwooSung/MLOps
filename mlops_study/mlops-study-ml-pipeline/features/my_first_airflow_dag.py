import pendulum
from textwrap import dedent
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

from support.callback_functions import success_callback, failure_callback

# 로컬 타임존 생성
local_timezone = pendulum.timezone("Asia/Seoul")

with DAG(dag_id='my_first_airflow_dag',
         default_args={
             "owner": "mlops.study",
             "depends_on_past": False,
             "email": ["mlops.study@gmail.com"],
             "email_on_failure": False,
             "email_on_retry": False,
             "retries": 1,
             "retry_delay": timedelta(minutes=5),
             "on_failure_callback": failure_callback,
             "on_success_callback": success_callback,
         },
         description='우리가 처음 만들어 보는 Airflow Dag 입니다.',
         schedule="0 8 * * *",
         start_date=datetime(2023, 5, 1, tzinfo=local_timezone),
         catchup=False,
         tags=["mlops", "study"],
         ) as dag:
    task1 = BashOperator(
        task_id="print_date",
        bash_command="date",
    )

    task2 = BashOperator(
        task_id="sleep",
        depends_on_past=False,
        bash_command="sleep 5",
        retries=3,
    )

    templated_command = dedent(
        """
        {% for i in range(5) %}
            echo "ds = {{ ds }}"
            echo "macros.ds_add(ds, {{ i }}) = {{ macros.ds_add(ds, i) }}"
        {% endfor %}
        """
    )

    task3 = BashOperator(
        task_id="templated",
        bash_command=templated_command,
    )

    task1 >> [task2, task3]
