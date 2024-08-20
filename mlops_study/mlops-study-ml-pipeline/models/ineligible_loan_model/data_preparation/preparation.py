import os
import sys
import joblib
import pandas as pd

mlops_data_store = os.getenv('MLOPS_DATA_STORE', "")
model_output_home = os.getenv('MODEL_OUTPUT_HOME', "")
feature_store_url = os.getenv('FEATURE_STORE_URL', "")


class Preparation:
    def __init__(self,
                 model_name: str,
                 model_version: str,
                 base_day: str):
        self._model_name = model_name
        self._model_version = model_version
        self._base_day = base_day
        self._data_preparation_path = f"{mlops_data_store}/data_preparation/{self._model_name}/{self._model_version}/{self._base_day}"
        self._makedir()

    def _makedir(self):
        if not os.path.isdir(self._data_preparation_path):
            os.makedirs(self._data_preparation_path)

    def preprocessing(self):
        loan_df = self._get_features_extracted()
        print(f"loan_df 메모리 주소값 = {id(loan_df)}")

        self._fill_na_to_default(loan_df)
        self._replace_category_to_numeric(loan_df)
        loan_df = self._transform_to_one_hot_encoding(loan_df)
        self._transform_to_label_encoding(loan_df)

        numeric_features = ['applicant_income', 'coapplicant_income', 'loan_amount_term']
        self._transform_to_standard_scale(loan_df, numeric_features)
        self._transform_to_min_max_scale(loan_df, numeric_features)
        self._save_encoded_features(loan_df)

    def _save_encoded_features(self, loan_df):
        """
            피처 데이터 저장
            """
        feature_file_name = f"{self._model_name}_{self._model_version}.csv"
        loan_df.to_csv(f"{self._data_preparation_path}/{feature_file_name}", index=False)

    def _transform_to_min_max_scale(self, loan_df, numeric_features):
        """
            Normalization (정규화)

            - 'applicant_income', 'coapplicant_income', 'loan_amount_term' 피처 데이터로 각각 min_max_scaler 훈련(fit)하고 min_max_scalers 딕셔너리에 저장한다.
            - min_max_scalers 저장 및 불러오기
            - 훈련된 인코더를 사용하여 데이터를 표준화하고 기존 컬럼에 저장한다.
            """
        from sklearn.preprocessing import MinMaxScaler
        # min_max_scalers 불러오기
        min_max_scalers = joblib.load(f'{model_output_home}/model_output/min_max_scalers.joblib')
        # numeric_features 정규화
        print(f"numeric_features 정규화")
        for numeric_feature in numeric_features:
            min_max_scaler = min_max_scalers[numeric_feature]
            print(f"numeric_feature = {numeric_feature}")

            loan_df[numeric_feature] = min_max_scaler.transform(loan_df[[numeric_feature]])

    def _transform_to_standard_scale(self, loan_df, numeric_features):
        """
            Standardization(표준화)

            - 'applicant_income', 'coapplicant_income', 'loan_amount_term' 피처 데이터로 각각 standard_scaler 훈련(fit)하고 standard_scalers 딕셔너리에 저장한다.
            - standard_scalers 저장 및 불러오기
            - 훈련된 인코더를 사용하여 데이터를 표준화하고 기존 컬럼에 저장한다.

            ※ 언제 정규화를 하고 언제 표준화를 할까?
            - 명확한 답은 없다.
            - 통상적으로는 표준화를 통해 이상치를 제거하고, 정규화하여 상대적 크기에 대한 영향력을 줄인다.
            """
        from sklearn.preprocessing import StandardScaler
        # standard_scalers 불러오기
        standard_scalers = joblib.load(f'{model_output_home}/model_output/standard_scalers.joblib')
        # numeric_features 표준화
        print(f"numeric_features 표준화")
        for numeric_feature in numeric_features:
            standard_scaler = standard_scalers[numeric_feature]
            print(f"numeric_feature = {numeric_feature}")

            loan_df[numeric_feature] = standard_scaler.transform(loan_df[[numeric_feature]])

    def _transform_to_label_encoding(self, loan_df):
        """
        라벨 인코딩 (Label Encoding)

        - 'property_area', 'family_dependents' 피처 데이터로 각각 라벨 인코딩 훈련(fit)하고 label_encoders 딕셔너리에 저장한다.
        - label_encoders 저장 및 불러오기
        - 훈련된 인코더를 사용하여 데이터를 라벨 인코딩하고 기존 컬럼에 저장한다.
        """
        from sklearn.preprocessing import LabelEncoder
        categorical_features = ['property_area', 'family_dependents']
        # label_encoders 불러오기
        label_encoders = joblib.load(f'{model_output_home}/model_output/label_encoders.joblib')
        # 라벨 인코딩
        print(f"라벨 인코딩")
        for categorical_feature in categorical_features:
            label_encoder = label_encoders[categorical_feature]
            print(f"categorical_feature = {categorical_feature}")
            print(f"label_encoder.classes_ = {label_encoder.classes_}")

            loan_df[categorical_feature] = label_encoder.transform(loan_df[categorical_feature])

    def _transform_to_one_hot_encoding(self, loan_df):
        """
        원핫 인코딩 (One-Hot Encoding)

        - 'married', 'self_employed' 피처 데이터로 원핫 인코딩 훈련(fit)한다.
        - one_hot_encoder 저장 및 불러오기
        - 훈련된 인코더를 사용하여 데이터를 원핫 인코딩한다.
        - 원핫 인코딩된 컬럼명 조회
          ・ get_feature_names_out 메소드를 이용하여 원핫 인코딩된 컬럼명을 가져올 수 있다.
          ・ 컬러명 array : array(['married_No', 'married_Yes', 'self_employed_No', 'self_employed_Yes'], dtype=object)
        - 기존 피처 컬러 삭제
          ・ 원래 데이터를 가지고 있는 'married', 'self_employed' 컬럼을 삭제한다.
        """
        print(f"one_hot_encoding (시작)-loan_df 메모리 주소값 = {id(loan_df)}")
        from sklearn.preprocessing import OneHotEncoder
        one_hot_encoder = OneHotEncoder()
        one_hot_features = ['married', 'self_employed']
        # one_hot_encoder 불러오기
        one_hot_encoder = joblib.load(f'{model_output_home}/model_output/one_hot_encoder.joblib')
        # 원핫 인코딩된 컬럼명 조회
        encoded_feature_names = one_hot_encoder.get_feature_names_out(one_hot_features)
        # 원핫 인코딩
        one_hot_encoded_data = one_hot_encoder.transform(loan_df[one_hot_features]).toarray()
        loan_encoded_df = pd.DataFrame(data=one_hot_encoded_data, columns=encoded_feature_names)
        print(f"one_hot_encoding (concat 전)-loan_df 메모리 주소값 = {id(loan_df)}")
        loan_df = pd.concat([loan_df, loan_encoded_df], axis=1)
        print(f"one_hot_encoding (concat 후)-loan_df 메모리 주소값 = {id(loan_df)}")
        # 기존 피처 컬러 삭제
        loan_df = loan_df.drop(columns=one_hot_features)
        print(f"one_hot_encoding (drop 후)-loan_df 메모리 주소값 = {id(loan_df)}")
        return loan_df

    def _replace_category_to_numeric(self, loan_df):
        """
            Replace 변환

            - 범주형(Categorical) 변수 중 gender, education, loan_status를 숫자형 변수로 변환한다.
            - 이와 같이 변환하는 방법에는 다음에 소개할 원핫 인코딩 (One-Hot Encoding), 라벨 인코딩 (Label Encoding) 등이 있지만,
            - 간단히 replace 함수를 사용하여, 0과 1로 변환 하였다.
            """
        # gender
        loan_df.gender = loan_df.gender.replace({"Male": 1, "Female": 0})
        # education
        loan_df.education = loan_df.education.replace({"Graduate": 1, "Not Graduate": 0})

    def _fill_na_to_default(self, loan_df):
        """
        결측치(N/A) 제거

        - family_dependents와 loan_amount_term의 결측치를 채우는 작업을 수행한다.
        - 'fillna'는 결측치를 채우는 메서드이며, 'inplace=True'는 원본 데이터프레임을 직접 수정함을 의미한다.
        - loan_amount_term은 데이터 과학자가 대출서비스에서 발생하는 대출기간의 기본값은 60개월을 설정하므로 60으로 결측값을 채웠다.
        """
        # family_dependents
        loan_df['family_dependents'].fillna('0', inplace=True)
        # loan_amount_term
        loan_df['loan_amount_term'].fillna(60, inplace=True)

    def _get_features_extracted(self):
        ###########################################################################
        ## 1. 데이터추출
        ###########################################################################
        from sqlalchemy import create_engine, text
        engine = create_engine(feature_store_url)
        ## 데이터추출 (01_data_extract.sql) 결과를 조회한다.
        sql = f"""
            select *
              from mlops.ineligible_loan_model_features
             where base_dt = '{self._base_day}'
            """
        with engine.connect() as conn:
            loan_df = pd.read_sql(text(sql), con=conn)

        if loan_df.empty is True:
            raise ValueError("loan df is empty!")
        return loan_df


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

    preparation = Preparation(model_name=_model_name,
                              model_version=_model_version,
                              base_day=_base_day)
    preparation.preprocessing()
