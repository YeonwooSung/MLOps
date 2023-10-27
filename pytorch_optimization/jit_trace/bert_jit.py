from transformers import BertTokenizer, BertModel
import numpy as np
import torch
from time import perf_counter


def timer(f, *args):
    start = perf_counter()
    f(*args)
    return (1000 * (perf_counter() - start))


script_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', torchscript=True)
script_model = BertModel.from_pretrained("bert-base-uncased", torchscript=True)


# Tokenizing input text
text = "[CLS] Who was Jim Henson ? [SEP] Jim Henson was a puppeteer [SEP]"
tokenized_text = script_tokenizer.tokenize(text)

# Masking one of the input tokens
masked_index = 8

tokenized_text[masked_index] = '[MASK]'

indexed_tokens = script_tokenizer.convert_tokens_to_ids(tokenized_text)
print(indexed_tokens)

segments_ids = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1]
print(segments_ids)

# Creating a dummy input
tokens_tensor = torch.tensor([indexed_tokens])
segments_tensors = torch.tensor([segments_ids])

# trace with torch.jit.trace
traced_model = torch.jit.trace(script_model, [tokens_tensor, segments_tensors])

np.mean([timer(traced_model, tokens_tensor, segments_tensors) for _ in range(100)])

traced_model_gpu = torch.jit.trace(script_model.cuda(), [tokens_tensor.cuda(), segments_tensors.cuda()])

np.mean([timer(traced_model_gpu, tokens_tensor.cuda(), segments_tensors.cuda()) for _ in range(100)])
