# Parallel inferencing with KServe and Ray Serve

## Basic explanation for Ray-Serve Architecture

Delving deeper, Ray Serve's architecture is intrinsically linked to Ray.
It operates within a Ray cluster consisting of a head node and several worker nodes.
In this setup, Ray Serve functions as an instance of a Ray Cluster with additional ray actors:

- HTTP proxy actor: Manages incoming requests and forwards them to replicas.
- Replica: Each replica processes individual requests from the HTTP proxy and responds once they are completed.
- Controller actor: Oversees the management of other actors.

## Parallel Inferencing with KServe and Ray Serve

By default, KServe's custom model serving runtime handles model loading and prediction within the same process as the HTTP Server.
The integration of Ray Serve changes this paradigm.
After you enable Ray Serve, KServe launches a Ray Serve instance, leading to a significant change in operation:

![kserve and rayserve](./imgs/kserve_and_rayserve.jpeg)

Models are deployed to Ray Serve as replicas, allowing for parallel inferencing when serving multiple requests.

## Implementing Ray Serve with KServe

To enable Ray Serve on KServe, the process involves a few straightforward steps.

### Create a KServe custom model

First we need to create a custom serving runtime with two handler methods using the KServe API.
The `kserve.Model` base class requires at least a load handler and predict handler to implement custom model serving runtime.

1. `def load()` is a load handler for loading a model into memory. This is generally called within the init().

2.  `def predict()` is a prediction handler for implementing the logic to return a result.

The folowing python example shows each handler's implementation for serving a custom model.

```python
import base64
import io
from PIL import Image
from torchvision import models, transforms
from typing import Dict
import torch
from kserve import Model, ModelServer


class AlexNetModel(Model):
    def __init__(self):
        self.name = "custom-model"
        super().__init__(self.name)
        self.load()

    # 1. Load the model into memory
    def load(self):
        self.model = models.alexnet(pretrained=True)
        self.model.eval()
        self.ready = True


    # 2. Impletement the prediction result
    def predict(self, payload: Dict, headers: Dict[str, str] = None) -> Dict:
        import json
        payload = json.loads(payload.decode('utf-8'))
        img_data = payload["instances"][0]["image"]["b64"]
        raw_img_data = base64.b64decode(img_data)
        input_image = Image.open(io.BytesIO(raw_img_data))
        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])
        input_tensor = preprocess(input_image).unsqueeze(0)
        output = self.model(input_tensor)
        torch.nn.functional.softmax(output, dim=1)
        values, top_5 = torch.topk(output, 5)
        result = values.flatten().tolist()
        return {"predictions": result}


if __name__ == "__main__":
    ModelServer().start([AlexNetModel()])
```

### Enabling Ray Serve with KServe

The following code shows how to modify the original example to enable Ray Serve with KServe in 3 steps:

1. Import Ray Serve into your environment.

2. Define the Ray Serve application using a decorator and specify the number of replicas for scaling.

3. Start the KServe model server with a different parameter to incorporate Ray Serve.

```python
import base64
import io
from PIL import Image
from torchvision import models, transforms
from typing import Dict
import torch
from kserve import Model, ModelServer
# Step 1
from ray import serve


# Step 2
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

    def predict(self, payload: Dict, headers: Dict[str, str] = None) -> Dict:
        import json
        payload = json.loads(payload.decode('utf-8'))
        img_data = payload["instances"][0]["image"]["b64"]
        raw_img_data = base64.b64decode(img_data)
        input_image = Image.open(io.BytesIO(raw_img_data))
        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])
        input_tensor = preprocess(input_image).unsqueeze(0)
        output = self.model(input_tensor)
        torch.nn.functional.softmax(output, dim=1)
        values, top_5 = torch.topk(output, 5)
        result = values.flatten().tolist()
        return {"predictions": result}


if __name__ == "__main__":
    # Step 3
    ModelServer().start({"custom-model": AlexNetModel})
```

## References

- [IBM tech blog: AWB parallel inference with kserve and rayserve](https://developer.ibm.com/articles/awb-parallel-inference-with-kserve-and-rayserve/)
