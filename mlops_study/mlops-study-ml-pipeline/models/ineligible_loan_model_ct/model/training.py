import os
import sys
import joblib
import pandas as pd

mlops_data_store = os.getenv('MLOPS_DATA_STORE', "")


class Training:
    def __init__(self,
                 model_name: str,
                 model_version: str,
                 base_day: str):
        self._model_name = model_name
        self._model_version = model_version
        self._base_day = base_day
        self._data_preparation_path = f"{mlops_data_store}/data_preparation" \
                                      f"/{self._model_name}/ct/{self._base_day}"
        self._model_output_path = f"{mlops_data_store}/model/{self._model_name}" \
                                  f"/{self._model_version}/{self._base_day}"
        self._makedir()

    def _makedir(self):
        if not os.path.isdir(self._model_output_path):
            os.makedirs(self._model_output_path)

    def train(self):
        metrics = {}

        # 학습 데이터 가져오기
        loan_df = pd.read_csv(f"{self._data_preparation_path}"
                              f"/{self._model_name}.csv")
        print(f"len(loan_df) = {len(loan_df)}")

        ###########################################################################
        ## 3. 모델 학습
        ###########################################################################
        from sklearn.linear_model import LogisticRegression
        from support.model.evaluation.lift import Lift

        """
        Train, Test 데이터셋 분리
        """
        # random 처리 시 항상 동일한 결과를 생성될 수 있도록, random_state값을 설정한다.
        random_state = 100

        # "random_state" 값이 동일하면 항상 학습 세트와 테스트 세트에서 동일한 정확한 데이터를 얻게 된다.
        # 데이터를 무작위로 분할할 때, 일반적으로 데이터를 학습 세트와 테스트 세트로 나누는 과정에서 무작위성을 도입한다.
        # 이는 실험의 재현성과 결과의 일관성을 보장하기 위해서 사용된다.
        loan_train = loan_df.sample(frac=0.65, random_state=random_state)
        loan_test = loan_df.drop(loan_train.index)

        # index 재설정
        loan_train = loan_train.reset_index(drop=True)
        loan_test = loan_test.reset_index(drop=True)

        ## 결과 확인
        print("######### loan_train #########")
        loan_train.info()
        print("\n######### loan_test #########")
        loan_test.info()

        ## 모델 피처와 타겟
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
        target = 'loan_status'

        x_train = loan_train[features].values
        y_train = loan_train[target].values

        x_test = loan_test[features].values
        y_test = loan_test[target].values

        ## 모델 학습
        logistic_model = LogisticRegression(max_iter=100)
        logistic_model.fit(x_train, y_train)

        ## 로지스틱회귀 모델학습 결과확인
        # 학습모델의 coefficient(계수)확인
        print('Coefficient of model :', logistic_model.coef_)
        # 학습모델의 intercept(절편)확인
        print('Intercept of model', logistic_model.intercept_)

        # 모델학습(Train 데이터셋) Lift 결과확인
        train_predict_proba = logistic_model.predict_proba(x_train)
        train_probabilities = pd.DataFrame(train_predict_proba)[1].to_list()
        train_lift = Lift(probabilities=train_probabilities,
                          labels=y_train,
                          cut_count=10)
        print(f'{train_lift.get_cum_lift()}')

        # 모델학습(Train 데이터셋) Accuracy 결과확인
        score = logistic_model.score(x_train, y_train)
        print('accuracy_score overall :', score)
        print('accuracy_score percent :', round(score * 100, 2))

        metrics["Coefficient of model"] = logistic_model.coef_.tolist()
        metrics["Intercept of model"] = logistic_model.intercept_.tolist()
        metrics["train"] = {
            "accuracy_score overall": score,
            "accuracy_score percent": round(score * 100, 2)
        }
        metrics["train"].update(train_lift.get_cum_lift().to_dict())
        ###########################################################################
        ## 4. 모델 예측
        ###########################################################################
        # 테스트 데이터셋의 모델예측 probability(확률) 추출
        test_predict_proba = logistic_model.predict_proba(x_test)
        print(f'test_predict_proba (sample 5) = {test_predict_proba[:5]}')

        # 예측 라벨이 1인 경우의 probability 추출
        test_probabilities = pd.DataFrame(test_predict_proba)[1].to_list()
        print(f'test_probabilities (sample 5) = {test_probabilities[:5]}')

        # 모델학습(Test 데이터셋)의 Lift 결과확인
        test_lift = Lift(probabilities=test_probabilities,
                         labels=y_test,
                         cut_count=10)
        print(f'{test_lift.get_cum_lift()}')

        # 모델학습(Test 데이터셋) Accuracy 결과확인
        score = logistic_model.score(x_test, y_test)
        print('accuracy_score overall :', score)
        print('accuracy_score percent :', round(score * 100, 2))

        metrics["test"] = {
            "accuracy_score overall": score,
            "accuracy_score percent": round(score * 100, 2)
        }
        metrics["test"].update(test_lift.get_cum_lift().to_dict())

        ###########################################################################
        ## 5. 모델 저장
        ###########################################################################
        # 모델파일을 로컬 저장소에 저장
        model_file_name = f'{self._model_name}.joblib'
        # 모델 저장
        joblib.dump(logistic_model,
                    f"{self._model_output_path}/{model_file_name}")
        print(f"metrics = {metrics}")
        return metrics


if __name__ == "__main__":
    print(f"sys.argv = {sys.argv}")
    if len(sys.argv) != 3:
        print("Insufficient arguments.")
        sys.exit(1)

    from support.date_values import DateValues
    from support.model.model_version import ModelVersion
    from support.model.model_ct_logger import ModelCtLogger

    _model_name = sys.argv[1]
    _base_day = sys.argv[2]
    _model_version = \
        ModelVersion(model_name=_model_name).get_next_ct_model_version()
    _base_ym = DateValues().get_before_one_month(_base_day)

    print(f"_model_name = {_model_name}")
    print(f"_base_day = {_base_day}")
    print(f"_model_version = {_model_version}")
    print(f"_base_ym = {_base_ym}")

    _ct_logger = ModelCtLogger(model_name=_model_name,
                               model_version=_model_version)
    _ct_logger.logging_started(cutoff_date=_base_ym)
    training = Training(model_name=_model_name,
                        model_version=_model_version,
                        base_day=_base_ym)
    _metrics = training.train()
    _ct_logger.logging_finished(metrics=_metrics)
