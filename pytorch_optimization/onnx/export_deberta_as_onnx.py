from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer


model_checkpoint = "microsoft/deberta-v3-base"
save_directory = "onnx/"

#
# Load a pretrained model from transformers and export it to ONNX
#

# load the pretrained model
ort_model = ORTModelForSequenceClassification.from_pretrained(
    model_checkpoint,
    from_transformers=True,
    export=True
)
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

# Save the onnx model and tokenizer
ort_model.save_pretrained(save_directory)
tokenizer.save_pretrained(save_directory)
