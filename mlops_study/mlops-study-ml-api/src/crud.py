import json
from typing import Union, Dict
from sqlalchemy.orm import Session

from src import models


class ModelApiLog:
    def __init__(self,
                 model_name: str,
                 model_version: str):
        self._model_name = model_name
        self._model_version = model_version

    def set_model_api_feature_log(self,
                                  db: Session,
                                  payload: Union[str, Dict]):
        self._set_model_api_log(db=db, log_type="FEATURE", payload=payload)

    def set_model_api_score_log(self,
                                db: Session,
                                payload: Union[str, Dict]):
        self._set_model_api_log(db=db, log_type="SCORE", payload=payload)

    def _set_model_api_log(self,
                           db: Session,
                           log_type: str,
                           payload: Union[str, Dict]):
        payload = json.dumps(payload) \
            if isinstance(payload, dict) else payload
        model_api_log = models.ModelApiLog(model_name=self._model_name,
                                           model_version=self._model_version,
                                           log_type=log_type,
                                           payload=payload)
        db.add(model_api_log)
        db.commit()
