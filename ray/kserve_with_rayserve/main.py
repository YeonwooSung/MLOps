import base64
import io
from PIL import Image
from torchvision import models, transforms
import torch
from kserve import Model, ModelServer
import json

from ray import serve



@serve.deployment(name="custom-model", num_replicas=1)
class AlexNetModel(Model):
    def __init__(self):
        self.name = "custom-model"
        super().__init__(self.name)
        self.load()

    def load(self):
        self.model = models.alexnet(pretrained=True)
        self.model.eval()
        self.ready = True

    def predict(self, payload: dict, headers: dict[str, str] = None) -> dict:
        payload = json.loads(payload.decode('utf-8'))
        img_data = payload["instances"][0]["image"]["b64"]
        raw_img_data = base64.b64decode(img_data)

        input_image = Image.open(io.BytesIO(raw_img_data))
        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
        ])

        input_tensor = preprocess(input_image).unsqueeze(0)
        output = self.model(input_tensor)

        torch.nn.functional.softmax(output, dim=1)
        values, top_5 = torch.topk(output, 5)
        result = values.flatten().tolist()

        return {"predictions": result}


if __name__ == "__main__":
    ModelServer().start({"custom-model": AlexNetModel})
