import torch
from PIL import Image
import requests
import numpy as np
from transformers import AutoImageProcessor, AutoModelForObjectDetection
import time


url = 'http://images.cocodataset.org/val2017/000000039769.jpg'
image = Image.open(requests.get(url, stream=True).raw)

processor = AutoImageProcessor.from_pretrained("facebook/detr-resnet-50")
model = AutoModelForObjectDetection.from_pretrained("facebook/detr-resnet-50").to("cuda")

texts = ["a photo of a cat", "a photo of a dog"]
inputs = processor(text=texts, images=image, return_tensors="pt").to("cuda")

start_time = time.time()
with torch.no_grad():
    _ = model(**processed_input)
print("Time taken for inference (pure): ", time.time() - start_time)

model = torch.compile(model)

start_time = time.time()
with torch.no_grad():
    _ = model(**inputs)
print("Time taken for inference (compile): ", time.time() - start_time)
