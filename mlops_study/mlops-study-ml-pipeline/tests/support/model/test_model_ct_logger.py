import os
import unittest

os.environ['FEATURE_STORE_URL'] = f"mysql+pymysql://root:root@localhost/mlops"


class TestModelCtLogger(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        from support.model.model_ct_logger import ModelCtLogger
        model_name = "ineligible_loan_model"
        model_version = "1.0.1"
        cls.model_ct_logger = ModelCtLogger(model_name=model_name,
                                            model_version=model_version)

    def test_01_logging_started(self):
        cutoff_date = "202308"
        self.model_ct_logger.logging_started(cutoff_date=cutoff_date)

    def test_02_logging_finished(self):
        metrics = {"accuracy": 90.23211}
        self.model_ct_logger.logging_finished(metrics=metrics)

    def test_03_get_training_cutoff_date(self):
        training_cutoff_date = \
            self.model_ct_logger.get_training_cutoff_date()
        print(f"training_cutoff_date = {training_cutoff_date}")


if __name__ == '__main__':
    unittest.main()
