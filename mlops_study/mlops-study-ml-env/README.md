# mlops-study-ml-env
MLOps 실습 가이드 책에서 모델 개발을 실습하기 위해서 사용하는 시스템 환경을 구성하기 위한 프로젝트이다.
데이터 과학자가 ML모델을 개발하기 위해서 많이 사용하는 Jupyter Notebook과 ML 서비스를 개발하기 위해서 사용할 데이터베이스로 MariaDB 서비스를 구성할 수 있다.

## 프로젝트 구조
```text
.
├── jupyter
│   ├── data
│   │   ├── requirements
│   │   │   └── requirements.txt
│   │   └── work
│   │       ├── 01_data_extract.sql
│   │       ├── 02_ineligible_loan_model_training.ipynb
│   │       ├── model_output
│   │       │   ├── ineligible_loan_model.joblib
│   │       │   ├── label_encoders.joblib
│   │       │   ├── min_max_scalers.joblib
│   │       │   ├── one_hot_encoder.joblib
│   │       │   └── standard_scalers.joblib
│   │       └── support
│   │           ├── __init__.py
│   │           └── model
│   │               ├── __init__.py
│   │               └── evaluation
│   │                   ├── __init__.py
│   │                   └── lift.py
│   └── docker-compose.yml
├── mariadb
│   ├── data
│   │   ├── docker-compose.yml
│   │   ├── docker-entrypoint-initdb.d
│   │   │   ├── 01_create_tables.sql
│   │   │   └── 02_load_data.sql
│   │   ├── mlops_table_data
│   │   │   ├── mlops.cust_info.csv
│   │   │   ├── mlops.family_info.csv
│   │   │   ├── mlops.loan_applicant_info.csv
│   │   │   └── mlops.loan_default_account.csv
│   │   └── mysql
│   │       └── my.cnf
│   └── docker-compose.yml
├── nginx_example
│   ├── data
│   │   └── nginx
│   │       └── nginx.conf
│   └── docker-compose.yml
└── README.md
```
### jupyter
* 데이터 과학자가 사용하는 Jupyter Notebook 서비스를 실행할 수 있다.
* Jupyter Notebook 서비스에는 데이터 과학자가 미리 개발해 놓은 신용대출 부적격 모델과 관련된 코드와 파일이 존재한다.
### mariadb
* ML 서비스에서 사용하는 데이터베이스로 MariaDB 서비스를 실행할 수 있다.
* 데이터 과학자가 분석하기 위한 데이터가 준비되어 있으며, MariaDB 서비스를 실행 시 자동으로 데이터가 생성된다.
### nginx_example
* CHAPTER 8에서 ML 모델의 지속적 배포 시 모델 서비스의 가용성을 확보하기 위해서 추가로 구성되는 Nginx 서비스이다.
* Nginx 서비스는 실습을 통해서 구성하게 되며, 그 결과물을 저장해 놓았다.
