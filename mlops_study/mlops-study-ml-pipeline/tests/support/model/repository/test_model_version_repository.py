import os
import unittest

os.environ['FEATURE_STORE_URL'] = f"mysql+pymysql://root:root@localhost/mlops"


class TestModelVersionRepository(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        from support.model.repository.model_version_repository import (
            ModelVersionRepository
        )
        cls.model_version_repository = ModelVersionRepository()

    def test_get_final_ct_model_version(self):
        model_name = 'ineligible_loan_model'
        final_ct_model_version = self.model_version_repository. \
            get_final_ct_model_version(model_name=model_name)
        print(f"final_ct_model_version = {final_ct_model_version}")


if __name__ == '__main__':
    unittest.main()
