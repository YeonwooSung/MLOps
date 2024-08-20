from typing import List
from datetime import datetime

from airflow import DAG
from airflow.models import Variable
from airflow.decorators import task
from airflow.models.param import Param
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

from support.date_values import DateValues

conn_id = "feature_store"
airflow_dags_path = Variable.get("AIRFLOW_DAGS_PATH")
sql_file_path = f"{airflow_dags_path}/features/exam_data_generator/recipes/create_exam_data.sql"
base_day = DateValues.get_before_one_day()


def read_sql_file(file_path):
    with open(file_path, 'r') as file:
        sql_query_lines = file.read()
    return "".join(sql_query_lines)


def validate_exam_date(date_list, start_day, end_day):
    # The data for the date range from June 1, 2023, to November 30, 2023
    exam_date_list = DateValues.get_date_list("20230601", "20231130")
    subtract_date_list = list(set(date_list) - set(exam_date_list))
    subtract_date_list.sort()
    if len(date_list) != len(subtract_date_list):
        raise ValueError("The data for the date range from 2023-06-01, to 2023-11-30, "
                         "is crucial for generating exam data, "
                         "and the start date and end date cannot include dates outside of this range.\n"
                         f"The dates you entered are as follows: start_day = {start_day}, end_day = {end_day}")


@task(task_id="DATE_PARAMS")
def get_date_params(start_day, end_day) -> List:
    print(f"start_day = {start_day}")
    print(f"end_day = {end_day}")
    date_params = []
    date_list = DateValues.get_date_list(start_day, end_day)
    validate_exam_date(date_list=date_list, start_day=start_day, end_day=end_day)
    for _date in date_list:
        date_params.append({"base_day": _date})
    print(f"date_params = {date_params}")
    return date_params


with DAG(dag_id="exam_data_generator",
         default_args={
             "owner": "mlops.study",
             "depends_on_past": False,
             "email": ["mlops.study@gmail.com"]
         },
         description="실습_데이터_생성",
         schedule=None,
         start_date=datetime(2023, 5, 1),
         catchup=False,
         tags=["mlops", "study"],
         params={
             "start_day": Param(
                 default="00010101",
                 type="string",
                 minLength=8,
                 maxLength=8,
             ),
             "end_day": Param(
                 default="00010101",
                 type="string",
                 minLength=8,
                 maxLength=8,
             )
         }
         ) as dag:
    data_generate = SQLExecuteQueryOperator.partial(
        task_id=f"실습_데이터_생성",
        conn_id=conn_id,
        sql=read_sql_file(sql_file_path),
        split_statements=True
    ).expand(
        params=get_date_params(start_day="{{ params.start_day }}",
                               end_day="{{ params.end_day }}")
    )
