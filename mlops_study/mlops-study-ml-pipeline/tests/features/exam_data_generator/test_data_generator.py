import os
import unittest
from airflow.models import Variable
from airflow.models.xcom_arg import PlainXComArg
from support.date_values import DateValues
from tests import context

home_dir = os.path.expanduser("~")
airflow_dags_path = Variable.get("AIRFLOW_DAGS_PATH")
os.environ['MLOPS_DATA_STORE'] = f"{home_dir}/airflow/mlops_data_store"
os.environ['MODEL_OUTPUT_HOME'] = f"{airflow_dags_path}/models/ineligible_loan_model"
os.environ['FEATURE_STORE_URL'] = f"mysql+pymysql://root:root@localhost/mlops"


class TestDataGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        from support.infra.db import Db
        cls.mysql = Db()
        # Common Given
        import features.exam_data_generator.exam_data_generator as data_generator
        cls.base_day = DateValues().get_before_one_day()
        cls.context = context
        cls.data_generator = data_generator

    def test_get_date_params(self):
        date_params: PlainXComArg = self.data_generator.get_date_params("00010101", "00010104")
        actual = date_params.operator.execute(self.context)
        expected = [{'base_day': '00010101'}, {'base_day': '00010102'}, {'base_day': '00010103'},
                    {'base_day': '00010104'}]
        self.assertListEqual(expected, actual)

    def test_validate_exam_date(self):
        start_day = "20230501"
        end_day = "20230530"
        date_list = DateValues.get_date_list(start_day, end_day)
        self.data_generator.validate_exam_date(date_list, start_day, end_day)
        start_day = "20231201"
        end_day = "20240331"
        date_list = DateValues.get_date_list(start_day, end_day)
        self.data_generator.validate_exam_date(date_list, start_day, end_day)

    def test_validate_exam_date_on_exception(self):
        start_day = "20230501"
        end_day = "20230630"
        date_list = DateValues.get_date_list(start_day, end_day)
        with self.assertRaises(ValueError):
            self.data_generator.validate_exam_date(date_list, start_day, end_day)
        start_day = "20231101"
        end_day = "20231231"
        date_list = DateValues.get_date_list(start_day, end_day)
        with self.assertRaises(ValueError):
            self.data_generator.validate_exam_date(date_list, start_day, end_day)
