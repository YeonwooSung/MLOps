import torch
from PIL import Image
import requests
import numpy as np
from transformers import AutoImageProcessor, AutoModelForImageClassification
import time


url = 'http://images.cocodataset.org/val2017/000000039769.jpg'
image = Image.open(requests.get(url, stream=True).raw)

processor = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224")
model = AutoModelForImageClassification.from_pretrained("google/vit-base-patch16-224").to("cuda")

processed_input = processor(image, return_tensors='pt').to(device="cuda")

start_time = time.time()
with torch.no_grad():
    _ = model(**processed_input)
print("Time taken for inference (pure): ", time.time() - start_time)

model = torch.compile(model)

start_time = time.time()
with torch.no_grad():
    _ = model(**processed_input)
print("Time taken for inference (compile): ", time.time() - start_time)
