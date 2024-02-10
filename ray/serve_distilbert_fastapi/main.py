from fastapi import FastAPI
import torch
from transformers import pipeline

from ray import serve
from ray.serve.handle import DeploymentHandle


app = FastAPI()


@serve.deployment(num_replicas=1)
@serve.ingress(app)
class APIIngress:
    def __init__(self, distilbert_model_handle) -> None:
        self.handle: DeploymentHandle = distilbert_model_handle.options(
            use_new_handle_api=True,
        )

    @app.get("/classify")
    async def classify(self, sentence: str):
        return await self.handle.classify.remote(sentence)


@serve.deployment(
    ray_actor_options={"num_gpus": 1},
    autoscaling_config={"min_replicas": 0, "max_replicas": 2},
)
class DistilBertModel:
    def __init__(self):
        self.classifier = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased",
            framework="pt",
            # Transformers requires you to pass device with index
            device=torch.device("cuda:0"),
        )

    def classify(self, sentence: str):
        return self.classifier(sentence)


entrypoint = APIIngress.bind(DistilBertModel.bind())
