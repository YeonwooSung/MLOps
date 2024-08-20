import os
import sys
import joblib
import pandas as pd

feature_store_url = os.getenv('FEATURE_STORE_URL', "")
model_output_home = os.getenv('MODEL_OUTPUT_HOME', "")
mlops_data_store = os.getenv('MLOPS_DATA_STORE', "")


class Preparation:
    def __init__(self,
                 model_name: str,
                 base_day: str):
        self._model_name = model_name
        self._base_day = base_day
        self._data_preparation_path = f"{mlops_data_store}/data_preparation" \
                                      f"/{self._model_name}/ct/{self._base_day}"
        self._encoder_path = f"{self._data_preparation_path}/encoders"
        self._makedir()

    def _makedir(self):
        if not os.path.isdir(self._encoder_path):
            os.makedirs(self._encoder_path)

    def preprocessing(self):
        loan_df = self._get_features_extracted()
        loan_df = self._set_random_sample(loan_df)
        self._fill_na_to_default(loan_df)
        self._replace_category_to_numeric(loan_df)
        loan_df = self._transform_to_one_hot_encoding(loan_df)
        self._transform_to_label_encoding(loan_df)
        numeric_features = ['applicant_income', 'coapplicant_income',
                            'loan_amount_term']
        self._transform_to_standard_scale(loan_df, numeric_features)
        self._transform_to_min_max_scale(loan_df, numeric_features)
        self._save_encoded_features(loan_df)

    def _save_encoded_features(self, loan_df):
        print("loan_df 결과 저장 예정!!!")
        """
        피처 데이터 저장
        """
        feature_file_name = f"{self._model_name}.csv"
        loan_df.to_csv(f"{self._data_preparation_path}"
                       f"/{feature_file_name}", index=False)

    def _transform_to_min_max_scale(self, loan_df, numeric_features):
        # 주석 생략 …
        from sklearn.preprocessing import MinMaxScaler

        # min/max scalers 학습(Fit)
        min_max_scalers = {}
        for numeric_feature in numeric_features:
            min_max_scaler = MinMaxScaler()
            min_max_scalers[numeric_feature] = \
                min_max_scaler.fit(loan_df[[numeric_feature]])

        # min_max_scalers 저장
        joblib.dump(min_max_scalers,
                    f'{self._encoder_path}/min_max_scalers.joblib')

        # numeric_features 정규화
        print(f"numeric_features 정규화")
        for numeric_feature in numeric_features:
            min_max_scaler = min_max_scalers[numeric_feature]
            print(f"numeric_feature = {numeric_feature}")

            loan_df[numeric_feature] = \
                min_max_scaler.transform(loan_df[[numeric_feature]])

    def _transform_to_standard_scale(self, loan_df, numeric_features):
        # 주석 생략 …
        from sklearn.preprocessing import StandardScaler

        # standard scalers 학습(Fit)
        standard_scalers = {}
        for numeric_feature in numeric_features:
            standard_scaler = StandardScaler()
            standard_scalers[numeric_feature] = \
                standard_scaler.fit(loan_df[[numeric_feature]])

        # standard_scalers 저장
        joblib.dump(standard_scalers,
                    f'{self._encoder_path}/standard_scalers.joblib')

        # numeric_features 표준화
        for numeric_feature in numeric_features:
            standard_scaler = standard_scalers[numeric_feature]
            print(f"numeric_feature = {numeric_feature}")

            loan_df[numeric_feature] = \
                standard_scaler.transform(loan_df[[numeric_feature]])

    def _transform_to_label_encoding(self, loan_df):
        # 주석 생략 …
        from sklearn.preprocessing import LabelEncoder
        categorical_features = ['property_area', 'family_dependents']

        # 라벨 인코딩 학습(Fit) 및 딕셔너리 저장
        label_encoders = {}
        for categorical_feature in categorical_features:
            label_encoder = LabelEncoder()
            label_encoders[categorical_feature] = \
                label_encoder.fit(loan_df[categorical_feature])

        # label_encoders 저장
        joblib.dump(label_encoders,
                    f'{self._encoder_path}/label_encoders.joblib')

        # 라벨 인코딩
        for categorical_feature in categorical_features:
            label_encoder = label_encoders[categorical_feature]
            print(f"categorical_feature = {categorical_feature}")
            print(f"label_encoder.classes_ = {label_encoder.classes_}")

            loan_df[categorical_feature] = \
                label_encoder.transform(loan_df[categorical_feature])

    def _transform_to_one_hot_encoding(self, loan_df):
        # 주석 생략 …
        from sklearn.preprocessing import OneHotEncoder
        one_hot_features = ['married', 'self_employed']

        # 원핫 인코딩 훈련(fit)
        one_hot_encoder = OneHotEncoder()
        one_hot_encoder.fit(loan_df[one_hot_features])
        # one_hot_encoder를 저장
        joblib.dump(one_hot_encoder,
                    f'{self._encoder_path}/one_hot_encoder.joblib')

        # 원핫 인코딩된 컬럼명 조회
        encoded_feature_names = \
            one_hot_encoder.get_feature_names_out(one_hot_features)
        # 원핫 인코딩
        one_hot_encoded_data = \
            one_hot_encoder.transform(loan_df[one_hot_features]).toarray()
        loan_encoded_df = pd.DataFrame(data=one_hot_encoded_data,
                                       columns=encoded_feature_names)
        loan_df = pd.concat([loan_df, loan_encoded_df], axis=1)
        # 기존 피처 컬러 삭제
        loan_df = loan_df.drop(columns=one_hot_features)
        return loan_df

    @staticmethod
    def _replace_category_to_numeric(loan_df):
        """
        Replace 변환
        - 범주형(Categorical) 변수 중 gender, education, loan_status를 숫자형 변수로
          변환한다.
        - 이와 같이 변환하는 방법에는 다음에 소개할 원핫 인코딩 (One-Hot Encoding), 라벨
          인코딩 (Label Encoding) 등이 있지만, 간단히 replace 함수를 사용하여, 0과 1로
          변환 하였다.
        """
        # gender
        loan_df.gender = loan_df.gender.replace({"Male": 1, "Female": 0})
        # education
        loan_df.education = loan_df.education.replace({"Graduate": 1,
                                                       "Not Graduate": 0})
        # loan_status
        loan_df.loan_status = loan_df.loan_status.replace({"Loan Default": 1,
                                                           "Creditworthy": 0})

    @staticmethod
    def _fill_na_to_default(loan_df):
        """
        결측치(N/A) 제거
        - family_dependents와 loan_amount_term의 결측치를 채우는 작업을 수행한다.
        - 'fillna'는 결측치를 채우는 메서드이며, 'inplace=True'는 원본 데이터프레임을 직접
          수정함을 의미한다.
        - loan_amount_term은 데이터 과학자가 대출서비스에서 발생하는 대출기간의 기본값은
          60개월을 설정하므로 60으로 결측값을 채웠다.
        """
        # family_dependents
        loan_df['family_dependents'].fillna('0', inplace=True)
        # loan_amount_term
        loan_df['loan_amount_term'].fillna(60, inplace=True)

    @staticmethod
    def _set_random_sample(loan_df):
        # random 처리 시 항상 동일한 결과를 생성될 수 있도록, random_state값을 설정한다.
        random_state = 100
        # df.sample(frac=1)은 데이터프레임을 완전히 섞는 작업을 수행한다.
        # random_state=random_state은 섞는 작업의 결과가 항상 동일하게 설정한다.
        # reset_index(drop=True)를 통해 인덱스를 재설정하고 이전의 인덱스를 삭제한다.
        loan_df = loan_df.sample(frac=1,
                                 random_state=random_state).reset_index(drop=True)
        return loan_df

    def _get_features_extracted(self):
        ###################################################################
        ## 1. 데이터추출
        ###################################################################
        from sqlalchemy import create_engine, text
        engine = create_engine(feature_store_url)
        ## 데이터추출 (01_data_extract.sql) 결과를 조회한다.
        sql = f"""
            select *
              from mlops.ineligible_loan_model_features_target
             where base_ym = '{self._base_day}'
            """
        with engine.connect() as conn:
            loan_df = pd.read_sql(text(sql), con=conn)

        if loan_df.empty is True:
            raise ValueError("loan df is empty!")
        return loan_df


if __name__ == "__main__":
    print(f"sys.argv = {sys.argv}")
    if len(sys.argv) != 3:
        print("Insufficient arguments.")
        sys.exit(1)

    from support.date_values import DateValues

    _model_name = sys.argv[1]
    _base_day = sys.argv[2]
    _base_ym = DateValues().get_before_one_month(_base_day)

    print(f"_model_name = {_model_name}")
    print(f"_base_day = {_base_day}")
    print(f"_base_ym = {_base_ym}")

    preparation = Preparation(model_name=_model_name,
                              base_day=_base_ym)
    preparation.preprocessing()
