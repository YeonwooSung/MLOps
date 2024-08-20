import joblib
import pandas as pd
from sqlalchemy.orm import Session

from src.crud import ModelApiLog
from src.schemas import ModelFeatures, ModelScore


class ModelPredictService:
    RESOURCES_PATH = "resources"

    def __init__(self,
                 model_api_log: ModelApiLog,
                 resources_path: str = RESOURCES_PATH):
        self._model_api_log = model_api_log
        self._resources_path = resources_path
        self._load_encoders()
        self._load_model()

    def predict(self,
                db: Session,
                features: ModelFeatures) -> ModelScore:
        self._model_api_log. \
            set_model_api_feature_log(db=db, payload=features.__dict__)

        loan_df = pd.DataFrame.from_records([features.__dict__])
        loan_df = self._preprocessing(loan_df=loan_df)

        predict, predict_proba = self._model_predict(loan_df)
        print(f"predict={predict}, predict_proba={predict_proba}")

        model_score = ModelScore(applicant_id=features.applicant_id,
                                 predict=predict,
                                 score=predict_proba[0][1])

        self._model_api_log. \
            set_model_api_score_log(db=db, payload=model_score.__dict__)
        return model_score

    def _model_predict(self, loan_df):
        # 모델 피처와 타겟
        _features = ['gender',
                     'family_dependents',
                     'education',
                     'applicant_income',
                     'coapplicant_income',
                     'loan_amount_term',
                     'credit_history',
                     'property_area',
                     'married_No',
                     'married_Yes',
                     'self_employed_No',
                     'self_employed_Yes']
        x_pred = loan_df[_features].values
        print(f"x_pred = {x_pred}")  # 모델 디버그를 위해 출력한다.
        # 모델 예측 라벨(0/1) 데이터 추출
        predict = self._logistic_model.predict(x_pred)
        # 모델 예측 probability(확률) 추출
        predict_proba = self._logistic_model.predict_proba(x_pred)
        return predict, predict_proba

    def _preprocessing(self, loan_df: pd.DataFrame) -> pd.DataFrame:
        self._fill_na_to_default(loan_df)
        self._replace_category_to_numeric(loan_df)
        loan_df = self._transform_to_one_hot_encoding(loan_df)
        self._transform_to_label_encoding(loan_df)

        numeric_features = ['applicant_income', 'coapplicant_income',
                            'loan_amount_term']
        self._transform_to_standard_scale(loan_df, numeric_features)
        self._transform_to_min_max_scale(loan_df, numeric_features)
        return loan_df

    def _transform_to_min_max_scale(self, loan_df, numeric_features):
        # numeric_features 정규화
        for numeric_feature in numeric_features:
            min_max_scaler = self._min_max_scalers[numeric_feature]
            loan_df[numeric_feature] = min_max_scaler. \
                transform(loan_df[[numeric_feature]])

    def _transform_to_standard_scale(self, loan_df, numeric_features):
        # numeric_features 표준화
        for numeric_feature in numeric_features:
            standard_scaler = self._standard_scalers[numeric_feature]
            loan_df[numeric_feature] = standard_scaler. \
                transform(loan_df[[numeric_feature]])

    def _transform_to_label_encoding(self, loan_df):
        categorical_features = ['property_area', 'family_dependents']
        # 라벨 인코딩
        for categorical_feature in categorical_features:
            label_encoder = self._label_encoders[categorical_feature]
            loan_df[categorical_feature] = label_encoder. \
                transform(loan_df[categorical_feature])

    def _transform_to_one_hot_encoding(self, loan_df):
        one_hot_features = ['married', 'self_employed']
        # 원핫 인코딩된 컬럼명 조회
        encoded_feature_names = self._one_hot_encoder. \
            get_feature_names_out(one_hot_features)
        # 원핫 인코딩
        one_hot_encoded_data = self._one_hot_encoder. \
            transform(loan_df[one_hot_features]).toarray()
        loan_encoded_df = pd.DataFrame(data=one_hot_encoded_data,
                                       columns=encoded_feature_names)
        loan_df = pd.concat([loan_df, loan_encoded_df], axis=1)
        # 기존 피처 컬러 삭제
        loan_df = loan_df.drop(columns=one_hot_features)
        return loan_df

    @staticmethod
    def _replace_category_to_numeric(loan_df):
        # gender
        loan_df.gender = loan_df.gender.replace({"Male": 1, "Female": 0})
        # education
        loan_df.education = loan_df.education.replace({"Graduate": 1, "Not Graduate": 0})

    @staticmethod
    def _fill_na_to_default(loan_df):
        # family_dependents
        loan_df['family_dependents'].fillna('0', inplace=True)
        # loan_amount_term
        loan_df['loan_amount_term'].fillna(60, inplace=True)

    def _load_encoders(self):
        self._one_hot_encoder = joblib.load(f"{self._resources_path}/"
                                            f"encoders/one_hot_encoder.joblib")
        self._label_encoders = joblib.load(f"{self._resources_path}/"
                                           f"encoders/label_encoders.joblib")
        self._standard_scalers = joblib.load(f"{self._resources_path}/"
                                             f"encoders/standard_scalers.joblib")
        self._min_max_scalers = joblib.load(f"{self._resources_path}/"
                                            f"encoders/min_max_scalers.joblib")

    def _load_model(self):
        self._logistic_model = joblib.load(f"{self._resources_path}/"
                                           f"model/ineligible_loan_model.joblib")
