from transformers import BertModel, BertTokenizer, BertConfig
import torch
import torch_tensorrt


enc = BertTokenizer.from_pretrained("bert-base-uncased")

# Tokenizing input text
text = "[CLS] Who was Jim Henson ? [SEP] Jim Henson was a puppeteer [SEP]"
tokenized_text = enc.tokenize(text)

# Masking one of the input tokens
masked_index = 8
tokenized_text[masked_index] = "[MASK]"
indexed_tokens = enc.convert_tokens_to_ids(tokenized_text)
segments_ids = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1]

# Creating a dummy input
tokens_tensor = torch.tensor([indexed_tokens])
segments_tensors = torch.tensor([segments_ids])
dummy_input = [tokens_tensor, segments_tensors]

# Initializing the model with the torchscript flag
# Flag set to True even though it is not necessary as this model does not have an LM Head.
config = BertConfig(
    vocab_size_or_config_json_file=32000,
    hidden_size=768,
    num_hidden_layers=12,
    num_attention_heads=12,
    intermediate_size=3072,
    torchscript=True,
)

# Instantiating the model
model = BertModel(config)

# The model needs to be in evaluation mode
model.eval()

# If you are instantiating the model with *from_pretrained* you can also easily set the TorchScript flag
model = BertModel.from_pretrained("bert-base-uncased", torchscript=True)

# set all the parameters to not require grad
for p in model.parameters():
    p.requires_grad_(False)

# Creating the trace
trt_ts_module = torch_tensorrt.compile(model,
    # If the inputs to the module are plain Tensors, specify them via the `inputs` argument:
    inputs = [tokens_tensor, segments_tensors],

    # For inputs containing tuples or lists of tensors, use the `input_signature` argument:
    # Below, we have an input consisting of a Tuple of two Tensors (Tuple[Tensor, Tensor])
    # input_signature = ( (torch_tensorrt.Input(shape=[1, 3, 224, 224], dtype=torch.half),
    #                      torch_tensorrt.Input(shape=[1, 3, 224, 224], dtype=torch.half)), ),

    enabled_precisions = {torch.float, torch.half}  , # Run with FP16
)
torch.jit.save(trt_ts_module, "traced_bert.pt")
