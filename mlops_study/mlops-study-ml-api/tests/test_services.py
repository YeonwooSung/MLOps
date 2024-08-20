import unittest

from src.schemas import ModelFeatures
from src.services import ModelPredictService
from src.crud import ModelApiLog
from src.database import get_db


class TestModelPredictService(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        model_name = "ineligible_loan_model"
        model_version = "1.0.0"
        model_api_log = ModelApiLog(model_name=model_name,
                                    model_version=model_version)
        cls.model_service = ModelPredictService(model_api_log=model_api_log,
                                                resources_path="../resources")

    def test_predict(self):
        # Given
        features = ModelFeatures(applicant_id='LP001002',
                                 gender='Male',
                                 married='No',
                                 family_dependents='1',
                                 education='Graduate',
                                 self_employed='No',
                                 applicant_income=5849,
                                 coapplicant_income=0,
                                 loan_amount_term=360,
                                 credit_history=1.0,
                                 property_area='Urban')
        db = get_db().__next__()
        # When
        model_score = self.model_service.predict(db=db, features=features)
        print(f"model_score = {model_score}")
