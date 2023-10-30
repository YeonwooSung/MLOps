from transformers import AutoTokenizer
from onnxruntime import InferenceSession


tokenizer = AutoTokenizer.from_pretrained("onnx")
session = InferenceSession("onnx/model.onnx")

# ONNX Runtime expects NumPy arrays as input
inputs = tokenizer(
    "Using DeBERTa with ONNX Runtime!",
    return_tensors="np",
    return_token_type_ids=False
)

outputs = session.run(
    output_names=["logits"],
    input_feed=dict(inputs)
)
