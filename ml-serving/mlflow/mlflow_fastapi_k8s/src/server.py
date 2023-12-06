from fastapi import FastAPI
from pydantic import BaseModel
import mlflow.sklearn


app = FastAPI()

class InputData(BaseModel):
    feature1: float
    feature2: float
    feature3: float
    feature4: float


# Load the model (replace with your model path)
MODEL_PATH = "runs:/<RUN_ID>/model"
model = mlflow.sklearn.load_model(MODEL_PATH)


@app.post("/predict/")
async def predict(input_data: InputData):
    # Extract input features from the request
    features = [input_data.feature1, input_data.feature2, input_data.feature3, input_data.feature4]

    # Make predictions using the loaded model
    prediction = model.predict([features])[0]

    # Create a response dictionary
    response_data = {"prediction": prediction}

    return response_data
