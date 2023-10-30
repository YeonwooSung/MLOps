# ONNX

[ONNX (Open Neural Network eXchange)](https://onnx.ai/) is an open standard that defines a common set of operators and a common file format to represent deep learning models in a wide variety of frameworks, including PyTorch and TensorFlow.
When a model is exported to the ONNX format, these operators are used to construct a computational graph (often called an intermediate representation) which represents the flow of data through the neural network.

By exposing a graph with standardized operators and data types, ONNX makes it easy to switch between frameworks.
For example, a model trained in PyTorch can be exported to ONNX format and then imported in TensorFlow (and vice versa).

## Exporting a 🤗 Transformers model to ONNX with CLI

To export a 🤗 Transformers model to ONNX, first install an extra dependency:

```bash
$ pip install optimum[exporters]
```

To check out all available arguments, refer to the [🤗 Optimum docs](https://huggingface.co/docs/optimum/exporters/onnx/usage_guides/export_a_model#exporting-a-model-to-onnx-using-the-cli), or view help in command line:

```bash
$ optimum-cli export onnx --help
```

To export a model’s checkpoint from the 🤗 Hub, for example, `distilbert-base-uncased-distilled-squad`, run the following command:

```bash
$ optimum-cli export onnx --model distilbert-base-uncased-distilled-squad distilbert_base_uncased_squad_onnx/
```

After exporting the '.onnx' format file, you could load and use the onnx exported model as following:

```python
from transformers import AutoTokenizer
from optimum.onnxruntime import ORTModelForQuestionAnswering


tokenizer = AutoTokenizer.from_pretrained("distilbert_base_uncased_squad_onnx")
model = ORTModelForQuestionAnswering.from_pretrained("distilbert_base_uncased_squad_onnx")

inputs = tokenizer("What am I using?", "Using DistilBERT with ONNX Runtime!", return_tensors="pt")

outputs = model(**inputs)
```

You could also export the model to ONNX as following:

```python
from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer


model_checkpoint = "distilbert_base_uncased_squad"
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
```
