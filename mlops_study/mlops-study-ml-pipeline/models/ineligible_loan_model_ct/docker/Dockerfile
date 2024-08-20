FROM python:3.9-slim
LABEL maintainer="mlops.study@gmail.com"

ARG USER_HOME=/home/mlops
ARG SUPPORT_SOURCE_PATH=support
ARG PREPARATION_SOURCE_PATH=models/ineligible_loan_model_ct/data_preparation
ARG MODEL_SOURCE_PATH=models/ineligible_loan_model_ct/model
ARG REQUIREMENTS_PATH=models/ineligible_loan_model_ct/docker

RUN groupadd --gid 1000 mlops \
    && useradd --uid 1000 --gid mlops --shell /bin/bash --create-home mlops

COPY --chown=mlops:mlops ${SUPPORT_SOURCE_PATH}/ ${USER_HOME}/support/
COPY --chown=mlops:mlops ${PREPARATION_SOURCE_PATH}/preparation.py \
     ${USER_HOME}/data_preparation/
COPY --chown=mlops:mlops ${MODEL_SOURCE_PATH}/training.py ${USER_HOME}/model/
COPY --chown=mlops:mlops ${REQUIREMENTS_PATH}/requirements.txt ${USER_HOME}/

USER mlops

RUN mkdir -p ${USER_HOME}/mlops_data_store \
    && pip install --no-cache-dir -r ${USER_HOME}/requirements.txt

WORKDIR ${USER_HOME}