import os
import uvicorn
from fastapi import FastAPI
from fastapi import Depends
from sqlalchemy.orm import Session

from src.schemas import ModelFeatures, ModelScore
from src.services import ModelPredictService
from src.crud import ModelApiLog
from src.database import get_db

# 모델 환경 변수
MODEL_NAME = os.getenv("MODEL_NAME", "ineligible_loan_model")
MODEL_VERSION = os.getenv("MODEL_VERSION", "1.0.0")

app = FastAPI()

# 서비스 및 로그 객체 생성
model_api_log = ModelApiLog(model_name=MODEL_NAME,
                            model_version=MODEL_VERSION)
model_service = ModelPredictService(model_api_log=model_api_log)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/ineligible_loan_model/predict/", response_model=ModelScore)
async def predict(features: ModelFeatures, db: Session = Depends(get_db)):
    print("Start model service!")
    return model_service.predict(features=features, db=db)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
