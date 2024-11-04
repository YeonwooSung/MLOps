# 배치 추론 패턴

## 목적

배치로 추론을 실행

## 전제

- Python 3.8 이상
- Docker
- Docker compose

## 사용법

0. 현재 디렉토리

```sh
$ pwd
~/ml-system-in-actions/chapter4_serving_patterns/batch_pattern
```

1. Docker 이미지 빌드

```sh
$ make build_all
# 실행 커맨드
# docker build \
#     -t shibui/ml-system-in-actions:batch_pattern_api_0.0.1 \
#     -f Dockerfile.api \
#     .
# docker build \
#     -t shibui/ml-system-in-actions:batch_pattern_batch_0.0.1 \
#     -f Dockerfile.batch \
#     .
```

2. Docker compose 로 각 서비스 기동

```sh
$ make c_up
# 실행 커맨드
# docker-compose \
#     -f ./docker-compose.yml \
#     up -d
```

3. 기동한 배치 시스템 확인

```sh
$ docker ps -a
# 출력
# CONTAINER ID   IMAGE                                                   COMMAND                  CREATED          STATUS          PORTS                               NAMES
# 08ca4db52176   shibui/ml-system-in-actions:batch_pattern_api_0.0.1     "./run.sh"               15 seconds ago   Up 14 seconds   0.0.0.0:8000->8000/tcp              api
# ab5f46b1e866   shibui/ml-system-in-actions:batch_pattern_batch_0.0.1   "python -m src.task.…"   15 seconds ago   Up 14 seconds                                       job
# d1d49ea39bf0   mysql:5.7                                               "docker-entrypoint.s…"   16 seconds ago   Up 15 seconds   0.0.0.0:3306->3306/tcp, 33060/tcp   mysql


$ docker logs job -f
# 출력
# 2021-01-30 12:41:52,739     INFO waiting for batch to start
# 2021-01-30 12:42:52,689     INFO starting batch
# 2021-01-30 12:42:52,795     INFO predict data size: 4000
# 2021-01-30 12:42:52,796    DEBUG prediction log: 4002 [4.3, 2.4, 3, 2.1] [0.13043216 0.5781998  0.29136813]
# 2021-01-30 12:42:52,798    DEBUG prediction log: 4003 [4.3, 2.4, 3, 2.1] [0.13043216 0.5781998  0.29136813]
# 2021-01-30 12:42:52,799    DEBUG prediction log: 4004 [4.3, 2.4, 3, 2.1] [0.13043216 0.5781998  0.29136813]
# 2021-01-30 12:42:52,800    DEBUG prediction log: 4005 [4, 3.9, 3, 6] [0.36126029 0.25740659 0.3813332 ]
# 2021-01-30 12:42:52,801    DEBUG prediction log: 4006 [4, 3.9, 3, 6] [0.36126029 0.25740659 0.3813332 ]
# 2021-01-30 12:42:52,807    DEBUG prediction log: 4007 [4, 3.9, 3, 6] [0.36126029 0.25740659 0.3813332 ]
# 2021-01-30 12:42:52,808    DEBUG prediction log: 4001 [4.3, 2.4, 3, 2.1] [0.13043216 0.5781998  0.29136813]
# 2021-01-30 12:42:52,808    DEBUG prediction log: 4009 [6, 3.9, 5.3, 5.7] [0.35905859 0.25630024 0.3846412 ]
```

4. Docker compose 정지

```sh
$ make c_down
# 실행 커맨드
# docker-compose \
#     -f ./docker-compose.yml \
#     down
```
