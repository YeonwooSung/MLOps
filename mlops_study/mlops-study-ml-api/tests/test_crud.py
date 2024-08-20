import unittest
from src.crud import ModelApiLog
from src.database import get_db


class TestModelApiLog(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        model_name = "ineligible_loan_model"
        model_version = "1.0.0"
        cls.model_api_log = ModelApiLog(model_name=model_name,
                                        model_version=model_version)

    def test_set_model_api_feature_log(self):
        # Given
        payload = {
            "applicant_id": "L000001",
            "gender": "Male",
            "married": "No",
            "family_dependents": "0",
            "property_area": "Rural"
        }
        db = get_db().__next__()
        # When
        self.model_api_log.set_model_api_feature_log(db=db,
                                                     payload=payload)

    def test_set_model_api_score_log(self):
        # Given
        payload = {
            "applicant_id": "L000001",
            "predict": "1",
            "score": 0.22222
        }
        db = get_db().__next__()
        # When
        self.model_api_log.set_model_api_feature_log(db=db,
                                                     payload=payload)


if __name__ == '__main__':
    unittest.main()
