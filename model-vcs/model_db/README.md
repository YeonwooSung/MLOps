# Model management database

## Goal

Build a database and REST API service for managing models.

![img](./img/model_db.png)

## Usage

1. Build Docker image

```sh
$ make build
# 실행 커맨드
# docker build \
#     -t shibui/ml-system-in-actions:model_db_0.0.1 \
#     -f Dockerfile \
#     .
# 출력 생략
# dockerイメージ로 shibui/ml-system-in-actions:model_db_0.0.1 이 빌드됩니다.
```

2. Run Model DB service with Docker compose

```sh
$ make c_up
# docker compose \
#     -f ./docker-compose.yml \
#     up -d
```

3. Check the Model DB service

Runs within 15 seconds after the service starts.
Check the service with Swagger UI (http://localhost:8000/docs).

![img](./img/model_swagger.png)

4. 모델 DB 서비스 정지

```sh
$ make c_down
# docker compose \
#     -f ./docker-compose.yml \
#     down
```
