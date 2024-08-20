import os
import sys
import joblib
import pandas as pd

mlops_data_store = os.getenv('MLOPS_DATA_STORE', "")
model_output_home = os.getenv('MODEL_OUTPUT_HOME', "")
feature_store_url = os.getenv('FEATURE_STORE_URL', "")


class Prediction:
    def __init__(self,
                 model_name: str,
                 model_version: str,
                 base_day: str):
        self._model_name = model_name
        self._model_version = model_version
        self._base_day = base_day

    def predict(self):
        # 피처 불러 오기
        features = ['gender',
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

        data_preparation_data_path = \
            f"{mlops_data_store}/data_preparation/{self._model_name}" \
            f"/{self._model_version}/{self._base_day}"
        feature_df = pd.read_csv(
            f"{data_preparation_data_path}"
            f"/{self._model_name}_{self._model_version}.csv")
        print(feature_df)

        x_pred = feature_df[features].values

        # 모델 불러오기
        model_file_name = f'{self._model_name}.joblib'
        logistic_model = joblib.load(f"{model_output_home}"
                                     f"/model_output/{model_file_name}")
        print(f"logistic_model = {logistic_model}")

        ###################################################################
        ## 4. 모델 예측
        ###################################################################
        # logistic_model의 분류값 확인
        print(f'logistic_model.classes_ = {logistic_model.classes_}')

        # 테스트 데이터셋의 모델예측 라벨데이터 추출
        predict = logistic_model.predict(x_pred)
        print('Target on test data (sample 20) =', predict[:20])

        # 테스트 데이터셋의 모델예측 probability(확률) 추출
        test_predict_proba = logistic_model.predict_proba(x_pred)
        print(f'test_predict_proba (sample 5) = {test_predict_proba[:5]}')

        # 예측 라벨이 1인 경우의 probability 추출
        test_probabilities = pd.DataFrame(test_predict_proba)[1].to_list()
        print(f'test_probabilities (sample 5) = {test_probabilities[:5]}')

        # 예측결과 저장용 DataFrame 예시
        data = {'base_dt': self._base_day,
                'applicant_id': feature_df['applicant_id'].to_list(),
                'predict': predict,
                'probability': test_probabilities
                }
        test_predicted = pd.DataFrame(data=data)
        print(f"test_predicted = {test_predicted}")

        ###################################################################
        ## 5. 모델 예측 결과 저장
        ###################################################################
        from sqlalchemy import create_engine
        engine = create_engine(feature_store_url)

        with engine.connect() as conn:
            init_sql = f"""
                    delete
                      from mlops.ineligible_loan_model_result
                     where base_dt = '{self._base_day}'
                    """
            conn.execute(statement=init_sql)
            insert_rows = test_predicted.to_sql(name='ineligible_loan_model_result',
                                                con=conn,
                                                schema='mlops',
                                                if_exists='append',
                                                index=False)
            print(f"insert_rows = {insert_rows}")


if __name__ == "__main__":
    print(f"sys.argv = {sys.argv}")
    if len(sys.argv) != 4:
        print("Insufficient arguments.")
        sys.exit(1)

    _model_name = sys.argv[1]
    _model_version = sys.argv[2]
    _base_day = sys.argv[3]

    print(f"_model_name = {_model_name}")
    print(f"_model_version = {_model_version}")
    print(f"_base_day = {_base_day}")

    prediction = Prediction(model_name=_model_name,
                            model_version=_model_version,
                            base_day=_base_day)
    prediction.predict()
