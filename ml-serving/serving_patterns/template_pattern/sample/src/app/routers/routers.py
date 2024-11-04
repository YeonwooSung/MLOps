import uuid
from logging import getLogger
from typing import Any, Dict, List

from fastapi import APIRouter
from src.ml.prediction import Data, classifier

logger = getLogger(__name__)
router = APIRouter()


@router.get("/health")
def health() -> Dict[str, str]:
    return {
        "health": "ok",
    }


@router.get("/metadata")
def metadata() -> Dict[str, Any]:
    return {
        "data_type": "float32",
        "data_structure": (1, 4),
        "data_sample": [[5.1, 3.5, 1.4, 0.2]],
        "prediction_type": "float32",
        "prediction_structure": (1, 3),
        "prediction_sample": [0.97093159, 0.01558308, 0.01348537],
    }


@router.get("/label")
def label() -> Dict[int, str]:
    return classifier.label


@router.get("/predict/test")
def predict_test() -> Dict[str, List[float]]:
    job_id = str(uuid.uuid4())
    prediction = classifier.predict(data=Data().data)
    prediction_list = list(prediction)
    logger.info(f"test {job_id}: {prediction_list}")
    return {"prediction": prediction_list}


@router.get("/predict/test/label")
def predict_test_label() -> Dict[str, str]:
    job_id = str(uuid.uuid4())
    prediction = classifier.predict_label(data=Data().data)
    logger.info(f"test {job_id}: {prediction}")
    return {"prediction": prediction}


@router.post("/predict")
def predict(data: Data) -> Dict[str, List[float]]:
    job_id = str(uuid.uuid4())
    prediction = classifier.predict(data.data)
    prediction_list = list(prediction)
    logger.info(f"{job_id}: {prediction_list}")
    return {"prediction": prediction_list}


@router.post("/predict/label")
def predict_label(data: Data) -> Dict[str, str]:
    job_id = str(uuid.uuid4())
    prediction = classifier.predict_label(data.data)
    logger.info(f"test {job_id}: {prediction}")
    return {"prediction": prediction}
