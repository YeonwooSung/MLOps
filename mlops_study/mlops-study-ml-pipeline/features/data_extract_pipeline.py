import pendulum
from datetime import datetime
from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from support.callback_functions import success_callback, failure_callback

local_timezone = pendulum.timezone("Asia/Seoul")
conn_id = "feature_store"

with DAG(dag_id="data_extract_pipeline",
         default_args={
             "owner": "mlops.study",
             "depends_on_past": False,
             "email": ["mlops.study@gmail.com"],
             "on_failure_callback": failure_callback,
             "on_success_callback": success_callback,
         },
         description="데이터추출_파이프라인",
         schedule=None,
         start_date=datetime(2023, 5, 1, tzinfo=local_timezone),
         catchup=False,
         tags=["mlops", "study"],
         ) as dag:
    task1_sql = """
        create database if not exists temp
        """
    task1 = SQLExecuteQueryOperator(
        task_id="create_database_temp",
        conn_id=conn_id,
        sql=task1_sql
    )

    task2_sql = """
        drop table if exists temp.ineligible_loan_model_features_01
        """
    task2 = SQLExecuteQueryOperator(
        task_id="drop_table_ineligible_loan_model_features_01",
        conn_id=conn_id,
        sql=task2_sql
    )

    task3_sql = """
        create table temp.ineligible_loan_model_features_01 as
        select a.applicant_id
              ,a.cust_id
              ,b.gender
              ,b.married
              ,b.education
              ,b.self_employed
              ,a.applicant_income
              ,a.coapplicant_income
              ,a.loan_amount_term
              ,a.credit_history
              ,a.property_area
          from mlops.loan_applicant_info a left outer join
               mlops.cust_info           b on (    a.applicant_date = b.base_dt
                                               and a.cust_id = b.cust_id)
         where a.applicant_date = '{{ yesterday_ds_nodash }}'
        """
    task3 = SQLExecuteQueryOperator(
        task_id="create_table_ineligible_loan_model_features_01",
        conn_id=conn_id,
        sql=task3_sql
    )

    task4_sql = """
        drop table if exists temp.ineligible_loan_model_features_02
        """
    task4 = SQLExecuteQueryOperator(
        task_id="drop_table_ineligible_loan_model_features_02",
        conn_id=conn_id,
        sql=task4_sql
    )

    task5_sql = """
        create table temp.ineligible_loan_model_features_02 as
        select c.cust_id
              ,c.family_dependents
          from (select a.cust_id
                      ,case when count(1) >= 3
                            then '3+'
                            else cast(count(1) as char)
                        end as family_dependents
                  from mlops.loan_applicant_info a inner join
                       mlops.family_info         b on (    a.applicant_date = b.base_dt
                                                       and a.cust_id = b.cust_id)
                 where a.applicant_date = '{{ yesterday_ds_nodash }}'
                 group by a.cust_id
               ) c
        """
    task5 = SQLExecuteQueryOperator(
        task_id="create_table_ineligible_loan_model_features_02",
        conn_id=conn_id,
        sql=task5_sql
    )

    task6_sql = """
        delete
          from mlops.ineligible_loan_model_features
         where base_dt = '{{ yesterday_ds_nodash }}'
        """
    task6 = SQLExecuteQueryOperator(
        task_id="delete_ineligible_loan_model_features",
        conn_id=conn_id,
        sql=task6_sql
    )

    task7_sql = """
        insert 
          into mlops.ineligible_loan_model_features
              (base_dt
              ,applicant_id
              ,gender
              ,married
              ,family_dependents
              ,education
              ,self_employed
              ,applicant_income  
              ,coapplicant_income
              ,loan_amount_term  
              ,credit_history    
              ,property_area
              )
        select '{{ yesterday_ds_nodash }}' as base_dt
              ,a.applicant_id
              ,a.gender
              ,a.married
              ,b.family_dependents
              ,a.education
              ,a.self_employed
              ,a.applicant_income  
              ,a.coapplicant_income
              ,a.loan_amount_term  
              ,a.credit_history    
              ,a.property_area
          from temp.ineligible_loan_model_features_01 a left outer join
               temp.ineligible_loan_model_features_02 b on (a.cust_id = b.cust_id)
        """
    task7 = SQLExecuteQueryOperator(
        task_id="insert_ineligible_loan_model_features",
        conn_id=conn_id,
        sql=task7_sql
    )

    task1 >> task2 >> task3 >> task4 >> task5 >> task6 >> task7
