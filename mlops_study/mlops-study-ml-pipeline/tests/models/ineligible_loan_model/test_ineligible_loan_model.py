import os
import unittest
from airflow.models import Variable

from support.date_values import DateValues

from tests import context

os.environ['FEATURE_STORE_URL'] = f"mysql+pymysql://root:root@localhost/mlops"
airflow_dags_path = Variable.get("AIRFLOW_DAGS_PATH")
os.environ['MODEL_OUTPUT_HOME'] = (f"{airflow_dags_path}"
                                   f"/models/ineligible_loan_model")
home_dir = os.path.expanduser("~")
os.environ['MLOPS_DATA_STORE'] = f"{home_dir}/airflow/mlops_data_store"


class TestIneligibleLoanModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Common Given
        cls.base_day = DateValues().get_before_one_day()  # 오늘 날짜의 D-1
        cls.context = context

    def test_data_extract(self):
        import models.ineligible_loan_model.ineligible_loan_model as model

        # When
        model.data_extract.__setattr__('sql',
                                       model.read_sql_file(model.sql_file_path).replace('{{ yesterday_ds_nodash }}',
                                                                                        self.base_day))
        model.data_extract.execute(self.context)

    def test_data_preparation(self):
        import models.ineligible_loan_model.ineligible_loan_model as model
        from models.ineligible_loan_model.data_preparation.preparation import Preparation

        # When
        preparation = Preparation(model_name=model.model_name,
                                  model_version=model.model_version,
                                  base_day=self.base_day)
        preparation.preprocessing()

    def test_data_preparation_of_dag_task(self):
        import models.ineligible_loan_model.ineligible_loan_model as model
        env = {"PYTHON_FILE": "/home/mlops/data_preparation/preparation.py",
               "MODEL_NAME": model.model_name,
               "MODEL_VERSION": model.model_version,
               "BASE_DAY": self.base_day}
        model.data_preparation.__setattr__("env", env)
        model.data_preparation.execute(self.context)

    def test_prediction(self):
        import models.ineligible_loan_model.ineligible_loan_model as model
        from models.ineligible_loan_model.model.prediction import Prediction

        # When
        prediction = Prediction(model_name=model.model_name,
                                model_version=model.model_version,
                                base_day=self.base_day)
        prediction.predict()

    def test_prediction_of_dag_task(self):
        import models.ineligible_loan_model.ineligible_loan_model as model
        env = {"PYTHON_FILE": "/home/mlops/model/prediction.py",
               "MODEL_NAME": model.model_name,
               "MODEL_VERSION": model.model_version,
               "BASE_DAY": self.base_day}
        model.prediction.__setattr__("env", env)
        model.prediction.execute(self.context)


if __name__ == '__main__':
    unittest.main()
