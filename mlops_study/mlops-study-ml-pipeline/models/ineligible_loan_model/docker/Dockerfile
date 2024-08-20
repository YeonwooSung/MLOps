FROM python:3.9-slim
LABEL maintainer="mlops.study@gmail.com"

ARG USER_HOME=/home/mlops
ARG PREPARATION_SOURCE_PATH=data_preparation
ARG MODEL_SOURCE_PATH=model
ARG MODEL_OUTPUT_PATH=model_output
ARG REQUIREMENTS_PATH=docker

RUN groupadd --gid 1000 mlops \
    && useradd --uid 1000 --gid mlops --shell /bin/bash --create-home mlops

COPY --chown=mlops:mlops ${PREPARATION_SOURCE_PATH}/preparation.py \
     ${USER_HOME}/data_preparation/
COPY --chown=mlops:mlops ${MODEL_SOURCE_PATH}/prediction.py \
     ${USER_HOME}/model/
COPY --chown=mlops:mlops ${MODEL_OUTPUT_PATH}/ \
     ${USER_HOME}/model_output/
COPY --chown=mlops:mlops ${REQUIREMENTS_PATH}/requirements.txt \
     ${USER_HOME}/

USER mlops

RUN mkdir -p ${USER_HOME}/mlops_data_store \
    && pip install --no-cache-dir \
          -r ${USER_HOME}/requirements.txt

WORKDIR ${USER_HOME}
