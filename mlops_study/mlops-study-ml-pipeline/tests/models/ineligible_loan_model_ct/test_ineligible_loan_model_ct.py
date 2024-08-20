import os
import unittest
from airflow.models import Variable
from support.date_values import DateValues
from tests import context

home_dir = os.path.expanduser("~")
airflow_dags_path = Variable.get("AIRFLOW_DAGS_PATH")
os.environ['MLOPS_DATA_STORE'] = f"{home_dir}/airflow/mlops_data_store"
os.environ['MODEL_OUTPUT_HOME'] = f"{airflow_dags_path}/models/ineligible_loan_model"
os.environ['FEATURE_STORE_URL'] = f"mysql+pymysql://root:root@localhost/mlops"


class TestIneligibleLoanModelCt(unittest.TestCase):
    base_day = None

    @classmethod
    def setUpClass(cls) -> None:
        # Common Given
        cls.base_day = DateValues().get_current_date()  # 당일
        cls.base_ym = DateValues().get_before_one_month(cls.base_day)  # 오늘 날짜의 전월(M-1)
        cls.context = context

    def test_data_extract(self):
        import models.ineligible_loan_model_ct.ineligible_loan_model_ct as model

        # When
        model.data_extract.__setattr__('sql',
                                       model.read_sql_file(model.sql_file_path).replace('{{ ds_nodash }}',
                                                                                        self.base_day))
        model.data_extract.execute(self.context)

    def test_data_preparation(self):
        import models.ineligible_loan_model_ct.ineligible_loan_model_ct as model
        from models.ineligible_loan_model_ct.data_preparation.preparation import Preparation

        # When
        preparation = Preparation(model_name=model.model_name,
                                  base_day=self.base_ym)
        preparation.preprocessing()

    def test_data_preparation_of_dag_task(self):
        import models.ineligible_loan_model_ct.ineligible_loan_model_ct as model
        context = {}
        env = {"PYTHON_FILE": "/home/mlops/data_preparation/preparation.py",
               "MODEL_NAME": model.model_name,
               "BASE_DAY": self.base_day}
        model.data_preparation.__setattr__("env", env)
        model.data_preparation.execute(context)

    def test_training(self):
        import models.ineligible_loan_model_ct.ineligible_loan_model_ct as model
        from models.ineligible_loan_model_ct.model.training import Training
        ct_model_version = "1.0.0"

        # When
        training = Training(model_name=model.model_name,
                            model_version=ct_model_version,
                            base_day=self.base_ym)
        training.train()

    def test_training_of_dag_task(self):
        import models.ineligible_loan_model_ct.ineligible_loan_model_ct as model
        env = {"PYTHON_FILE": "/home/mlops/model/training.py",
               "MODEL_NAME": model.model_name,
               "BASE_DAY": self.base_day}
        model.training.__setattr__("env", env)
        model.training.execute(self.context)


if __name__ == '__main__':
    unittest.main()
