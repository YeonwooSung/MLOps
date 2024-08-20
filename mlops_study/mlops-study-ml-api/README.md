# mlops-study-ml-api
MLOps 실습 가이드 책의 CHAPTER 7에서 다루는 실습 개발의 결과물로 모델에서 사용하는 피처를 입력하여 API를 요청하면, 모델의 예측값을 응답받는다.

## 프로젝트 구조
```text
.
├── docker
│   ├── Dockerfile
│   └── docker-compose.yml
├── resources
│   ├── encoders
│   │   ├── label_encoders.joblib
│   │   ├── min_max_scalers.joblib
│   │   ├── one_hot_encoder.joblib
│   │   └── standard_scalers.joblib
│   └── model
│       └── ineligible_loan_model.joblib
├── src
│   ├── __init__.py
│   ├── crud.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── services.py
├── tests
│   ├── __init__.py
│   ├── test_crud.py
│   └── test_services.py
├── app.py
├── requirements.txt
└── README.md
```
### docker
* ML 모델 API 서비스를 제공하기 위해서 docker images로 빌드하고 docker-compose로 서비스를 관리한다.
### resources
* 모델 API를 제공하기 위해서 필요한 인코더와 모델 파일을 관리한다.
### src
* 모델 API 서비스의 소스 파일을 관리한다.
### tests
* 모델 API 서비스를 개발하고 테스트하기 위한 테스트 케이스를 관리한다.

## 서비스 실행 및 중지
### Start
```shell
cd ./docker/
docker-compose up -d
```
### Stop
```text
cd ./docker/
docker-compose down
```
## API 호출
### Curl
```shell
curl -X 'POST' \
  'http://localhost:8000/ineligible_loan_model/predict/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
 "applicant_id": "LP002840",
 "gender": "Female",
 "married": "No",
 "family_dependents": "0",
 "education": "Graduate",
 "self_employed": "No",
 "applicant_income": 2378,
 "coapplicant_income": 0,
 "loan_amount_term": 360.0,
 "credit_history": 1.0,
 "property_area": "Urban"
}'
```
### Response body
```text
{
  "applicant_id": "LP002840",
  "predict": 0,
  "score": 0.09998178167547511
}
```