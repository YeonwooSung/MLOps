import os
import unittest

os.environ['FEATURE_STORE_URL'] = f"mysql+pymysql://root:root@localhost/mlops"


class TestModelVersion(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        from support.model.model_version import ModelVersion
        model_name = "ineligible_loan_model"
        cls.model_version = ModelVersion(model_name=model_name)

    def test_get_final_ct_model_version(self):
        final_ct_model_version = self.model_version.get_final_ct_model_version()
        print(f"final_ct_model_version = {final_ct_model_version}")

    def test_get_next_ct_model_version(self):
        next_ct_model_version = self.model_version.get_next_ct_model_version()
        print(f"next_ct_model_version = {next_ct_model_version}")


if __name__ == '__main__':
    unittest.main()
