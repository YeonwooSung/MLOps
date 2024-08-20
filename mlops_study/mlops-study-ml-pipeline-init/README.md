# mlops-study-ml-pipeline-init
MLOps 구축 가이드북에서 실습을 진행하기 위해서 사용되며, Aiflow를 처음 접하는 실습자를 위해서 쉽게 standalone으로 구성할 수 있도록 제공되는 프로젝트이다.
해당 프로젝트를 다운로드 받아서, ariflow_install.sh 파일을 실행하면 쉽게 Airflow 2.7.2 설치하고 DAG를 개발해 볼 수 있다.
mlops-study-ml-pipeline-init을 기반으로 mlops-study-ml-pipeline 프로젝트의 ML 파이프라인을 개발해 보면서, 해당 프로젝트가 더 풍성해지는 것을 경험해 볼 수 있다.

## 프로젝트 구조
```text
.
├── features
│   ├── __init__.py
│   └── exam_data_generator
│       ├── __init__.py
│       ├── exam_data_generator.py
│       └── recipes
│           ├── __init__.py
│           └── create_exam_data.sql
├── models
│   └── __init__.py
├── shell
│   ├── airflow_install.sh
│   ├── airflow_run.sh
│   ├── airflow_stop.sh
│   └── create_user.sh
├── support
│   ├── __init__.py
│   └── date_values.py
├── README.md
└── requirements.txt
```

### features
* exam_data_generator (실습용 데이터 생성기)
  * 실습용 데이터 생성기는 책에서 사용하는 실습용 데이터를 생성해주는 Airflow DAG로 개발되어져 있다.
  * 이미, mlops-study-ml-env 프로젝트를 설정하고 나면, 2023-06-01 ~ 2025-12-31 기간의 실습용 데이터는 적재되어 있다.
  * 이 기간 이후 실습에 사용되는 데이터가 존재하지 않으면 실습에 필요한 데이터를 생성해 주어야 한다.

### models
* 책에서 실습하는 ML모델 파이프라인을 Airflow의 DAG로 개발하는 공간으로 사용된다.

### shell
* Airflow를 설치하고, 서비스를 실행 또는 종료하는 등의 작업을 실행하는 쉘 스크립트를 관리한다.
* 각각의 쉘 스크립트 파일은 아래와 같은 기능을 수행한다.
  * airflow_install.sh
    * 현재 설치된 Python 버전에 맞는 Airflow 2.7.2 버전을 설치한다.
      ```shell
      ~/Study/mlops-study-ml-pipeline/shell/airflow_install.sh
      ```
  * airflow_run.sh
    * Airflow의 scheduler, triggerer 그리고 webserver 서비스를 실행한다.
    * 실습을 다시 시작할 때, airflow_run.sh 쉘을 실행시키면 쉽게 Airflow를 사용할 수 있다.
      ```shell
      ~/Study/mlops-study-ml-pipeline/shell/airflow_run.sh
      ```
  * airflow_stop.sh
    * Airflow의 scheduler, triggerer 그리고 webserver 서비스를 중지한다.
    * 실습이 종료되고 아래와 같이 Airflow 서비스를 종료해야 한다.
    * Airflow 서비스를 정상종료 하지 못하였을 때에도 아래의 쉡을 먼저 실행하고, airflow_run.sh을 실행한다. 
      ```shell
      ~/Study/mlops-study-ml-pipeline/shell/airflow_stop.sh
      ```
  * create_user.sh
    * 실습에서 사용하는 mlops 사용자를 추가할 수 있다.
      ```shell
      ~/Study/mlops-study-ml-pipeline/shell/create_user.sh
      ```
  * create_symbolic_link.sh
    * ML 파이프라인 프로젝트내에 개발한 DAG와 공통모듈을 Airflow에 바로 반영하기 위해서, 심볼릭 링크를 사용한다.
    * create_symbolic_link.sh 스크립트를 실행하면, 프로젝트의 패키지가 Airflow Home 디렉토리에 반영되어, Airflow Web UI에서 실행해 볼 수 있다.
      ```shell
      ~/Study/mlops-study-ml-pipeline/shell/create_symbolic_link.sh
      ```

### support
* ML 파이프라인을 개발 하면서, 공통으로 사용하는 모듈을 개발하고 관리한다.
* date_values.py 모듈은 Date와 관련된 기능을 사전에 개발해 놓았으며, 실습 과정에서 사용하게 된다.

### requirements.txt
* ML 파이프라인 프로젝트에 필요한 외부 패키지 및 라이브러리의 목록을 포함하는 텍스트 파일이다.
* pip를 사용하여 의존성 패키지를 설치하는데 사용한다.
  ```shell
  cd ~/Study/mlops-study-ml-pipeline && pip install -r requirements.txt
  ```

## Airflow provider packages 설치
### Airflow apache-airflow-providers-mysql
```shell
brew install mysql pkg-config
pip install mysqlclient mysql-connector-python
pip install apache-airflow-providers-mysql
```

## (Windows 11 사용자) PyCharm Terminal Shell path
### mlops-study-ml-pipeline 프로젝트 Terminal
```text
wsl.exe --distribution Ubuntu -- bash --rcfile <(echo '. ~/.bashrc; source ~/Study/mlops-study-ml-pipeline/.venv/bin/activate')
```
### mlops-study-ml-api 프로젝트 Terminal
```text
wsl.exe --distribution Ubuntu -- bash --rcfile <(echo '. ~/.bashrc; source .venv/bin/activate')
```

## 실습에 필요한 Values
### 6.2.2 데이터처리 SQL 작성
#### 날짜값 조회
```text
select CONCAT(DATE_FORMAT(DATE_ADD(STR_TO_DATE('20231201', '%Y%m%d'
                                            ), INTERVAL -6 MONTH
                                ), '%Y%m'
                       ), '01'
           ) as start_date
      ,DATE_FORMAT(LAST_DAY(DATE_ADD(STR_TO_DATE('20231201', '%Y%m%d'
                                                ), INTERVAL -1 MONTH
                                    )
                           ), '%Y%m%d'
                  ) as end_date;
```
#### 날짜값 수정
```text
'20230601' → CONCAT(DATE_FORMAT(DATE_ADD(STR_TO_DATE('{{ ds_nodash }}', '%Y%m%d'), INTERVAL -6 MONTH), '%Y%m'), '01')
'20231130' → DATE_FORMAT(LAST_DAY(DATE_ADD(STR_TO_DATE('{{ ds_nodash }}', '%Y%m%d'), INTERVAL -1 MONTH)), '%Y%m%d')
```
