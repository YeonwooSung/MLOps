from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta


# DAG 정의
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 11, 25),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'hello_airflow_dag',
    default_args=default_args,
    description='A simple tutorial DAG',
    schedule_interval=timedelta(days=1),
)

# 출력 함수 정의
def print_word(word):
    print(word)

# 문장
sentence = "hello airflow dag. fast campus lecture! we can do it."

# 각 단어를 순차적으로 출력하는 Task 생성
prev_task = None
for i, word in enumerate(sentence.split()):
    task = PythonOperator(
        task_id=f'print_word_{i}',
        python_callable=print_word,
        op_kwargs={'word': word},
        dag=dag,
    )

    if prev_task:
        prev_task >> task

    prev_task = task
