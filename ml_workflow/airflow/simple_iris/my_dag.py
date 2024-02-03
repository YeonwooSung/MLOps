from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2021, 1, 1),
    # 기타 필요한 기본 인자들...
}

dag = DAG(
    'example_dag',
    default_args=default_args,
    description='An example DAG',
    schedule_interval=timedelta(days=1),
)

def example_task():
    # Task에서 수행할 작업
    pass

task = PythonOperator(
    task_id='example_task',
    python_callable=example_task,
    dag=dag,
)

task1 = PythonOperator(
    task_id='task1',
    python_callable=example_task,
    dag=dag,
)

task2 = PythonOperator(
    task_id='task2',
    python_callable=example_task,
    dag=dag,
)

# task1이 task2보다 먼저 실행되도록 설정
task1 >> task2
