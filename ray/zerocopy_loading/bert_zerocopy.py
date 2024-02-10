import copy
import torch
from transformers import BertModel, BertTokenizerFast
import ray


def extract_tensors(m: torch.nn.Module) -> tuple[torch.nn.Module, list[dict]]:
    """
    Remove the tensors from a PyTorch model, convert them to NumPy
    arrays, and return the stripped model and tensors.

    Args:
        m: The model to strip tensors from.
    """
    tensors = []
    for _, module in m.named_modules():
        # Store the tensors in Python dictionaries
        params = {
            name: torch.clone(param).detach().numpy()
            for name, param in module.named_parameters(recurse=False)
        }
        buffers = {
            name: torch.clone(buf).detach().numpy()
            for name, buf in module.named_buffers(recurse=False)
        }
        tensors.append({"params": params, "buffers": buffers})
    
    # Make a copy of the original model and strip all tensors and
    # buffers out of the copy.
    m_copy = copy.deepcopy(m)
    for _, module in m_copy.named_modules():
        for name in ([name for name, _ in module.named_parameters(recurse=False)]
                     + [name for name, _ in module.named_buffers(recurse=False)]):
            setattr(module, name, None)   

    # Make sure the copy is configured for inference.
    m_copy.train(False)
    return m_copy, tensors


def replace_tensors(m: torch.nn.Module, tensors: list[dict]):
    """
    Restore the tensors that extract_tensors() stripped out of a PyTorch model.

    Args:
        m: The model to restore tensors to.
        tensors: The tensors to restore to the model.
    """
    modules = [module for _, module in m.named_modules()] 
    for module, tensor_dict in zip(modules, tensors):
        # There are separate APIs to set parameters and buffers.
        for name, array in tensor_dict["params"].items():
            module.register_parameter(name, 
                torch.nn.Parameter(torch.as_tensor(array)))
        for name, array in tensor_dict["buffers"].items():
            module.register_buffer(name, torch.as_tensor(array))


def main():
    bert = BertModel.from_pretrained("bert-base-uncased")
    # torch.save(bert, "bert.pt")

    bert_ref = ray.put(extract_tensors(bert))

    bert_skeleton, bert_weights = ray.get(bert_ref)

    # Load tensors into the model's graph of Python objects
    replace_tensors(bert_skeleton, bert_weights)

    # Preprocess an example input string for BERT.
    test_text = "All work and no play makes Jack a dull boy."
    tokenizer = BertTokenizerFast.from_pretrained("bert-base-uncased")
    test_tokens = tokenizer(test_text, return_tensors="pt")

    # Run the original model and the copy that we just loaded
    print("Original model's output:")
    print(bert(**test_tokens).last_hidden_state)
    print("\nModel output after zero-copy model loading:")
    print(bert_skeleton(**test_tokens).last_hidden_state)
