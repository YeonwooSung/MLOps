import json
from typing import Union, Dict
from support.model.repository.model_ct_logger_repository import (
    ModelCtLoggerRepository
)


class ModelCtLogger:
    DEFAULT_REPOSITORY = ModelCtLoggerRepository()

    def __init__(self,
                 model_name: str,
                 model_version: str,
                 repository: ModelCtLoggerRepository = DEFAULT_REPOSITORY):
        self._model_name = model_name
        self._model_version = model_version
        self._repository = repository

    def logging_started(self, cutoff_date: str):
        self._repository.logging_init(model_name=self._model_name,
                                      model_version=self._model_version)
        self._repository.logging_started(model_name=self._model_name,
                                         model_version=self._model_version,
                                         cutoff_date=cutoff_date)

    def logging_finished(self, metrics: Union[str, Dict]):
        if isinstance(metrics, dict):
            metrics = json.dumps(metrics)
        self._repository.logging_finished(model_name=self._model_name,
                                          model_version=self._model_version,
                                          metrics=metrics)

    def get_training_cutoff_date(self):
        return self._repository.get_training_cutoff_date(
            model_name=self._model_name,
            model_version=self._model_version
        )
