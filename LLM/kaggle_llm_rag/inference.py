from transformers import AutoModelForCausalLM, AutoTokenizer
import itertools
import random
import argparse
import os
import pandas as pd
import numpy as np
from string import Template
from pathlib import Path
import time
import torch
from tqdm.auto import tqdm
import gc
import itertools


#os.environ["TOKENIZERS_PARALLELISM"] = "false"

def precision_at_k(r, k):
    """Precision at k"""
    assert k <= len(r)
    assert k != 0
    return sum(int(x) for x in r[:k]) / k


def MAP_at_3(predictions, true_items):
    """Score is mean average precision at 3"""
    U = len(predictions)
    map_at_3 = 0.0
    for u in range(U):
        user_preds = predictions[u]
        user_true = true_items[u]
        user_results = [1 if item == user_true else 0 for item in user_preds]
        for k in range(min(len(user_preds), 3)):
            map_at_3 += precision_at_k(user_results, k+1) * user_results[k]
    return map_at_3 / U


def longest_common_prefix(strs: list) -> str:
    """
    Longest common prefix의 최대 길이는 결국
    가장 짧은 문자열의 길이와 같거나 짧다.
    따라서, 가장 짧은 문자열의 substring을 하나씩 줄여가며
    모든 문자열에 존재하는지 확인하면 된다.
    """
    if not strs:
        return ""

    shortest = min(strs, key=len)

    for i, char in enumerate(shortest):
        for other in strs:
            if other[i] != char:
                return shortest[:i]

    return shortest


if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument('--device', type=str, required=True)
    ap.add_argument('--model_name', type=str, required=True)
    ap.add_argument('--quantization', type=int, required=True)
    ap.add_argument('--model_type', type=int, required=True)
    ap.add_argument('--test_file', type=str, required=True)
    args = ap.parse_args()

    if args.device == "auto":
        DEVICE_MAP = "auto"
        DEVICE = "cuda:0"
    else:
        DEVICE_MAP = {"":args.device}
        DEVICE = args.device

    llm_backbone = args.model_name

    test = pd.read_parquet(args.test_file).reset_index(drop=True)

    new_obs = []
    for idx, row in test.iterrows():
        for opt in "ABCDE":
            new_obs.append((row["id"], row["context"], row["context_v2"], row["prompt"], row[opt]))

    df = pd.DataFrame(new_obs, columns=["id", "context", "context_v2", "question", "answer"])
    print(df.head(1))

    tokenizer = AutoTokenizer.from_pretrained(
        llm_backbone,
        use_fast=True,
        trust_remote_code=True,
        padding_side="right",
        truncation_side="left"
    )

    if tokenizer.pad_token is None:
        if tokenizer.unk_token is not None:
            tokenizer.pad_token = tokenizer.unk_token
        else:
            tokenizer.pad_token = tokenizer.eos_token
    
    from transformers import BitsAndBytesConfig
    
#     quantization_config = BitsAndBytesConfig(
#        load_in_4bit=True,
#        bnb_4bit_quant_type="nf4",
#        bnb_4bit_use_double_quant=False,
#        bnb_4bit_compute_dtype=torch.float16
#     )

    if args.quantization == 0:
        quantization_config = None

    elif args.quantization == 1:
        quantization_config = BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_threshold=0.0,
        )


    model = AutoModelForCausalLM.from_pretrained(
        llm_backbone,
        torch_dtype=torch.float16,
        quantization_config=quantization_config,
        device_map=DEVICE_MAP,
        low_cpu_mem_usage=True,
        trust_remote_code=True
    ).eval()

    head_weights = torch.load(llm_backbone + "/head.pth", map_location="cpu")
    hidden_size = head_weights.shape[1]
    print(hidden_size)
    # hidden_size = 32000

    head = torch.nn.Linear(hidden_size, 1, bias=False)
    head.weight.data = head_weights
    head.to(DEVICE).eval()

    model.config.pad_token_id = tokenizer.pad_token_id
    
    gc.collect()


    

    import itertools
    import random
    maps = []

    progress_bar = tqdm(df.iterrows(), total=len(df))

    preds = []
    instructions = []
    pooled = []
    past_key_values = None
    for idx,row in progress_bar:
        
        inst = f"Answer: {row['answer']}\n###\nIs this answer correct? "
        #inst = "a b c d"*10_000
        instructions.append(inst)
        
        if idx % 5 == 0:
            
            if past_key_values is not None:
                del past_key_values
            
            preprompt = f"{row['context_v2']}\n###\nQuestion: {row['question']}\n###\n"
            #preprompt = "a b c d"*10_000
            inputs = tokenizer(preprompt, return_tensors='pt', add_special_tokens=False, truncation=True, padding="longest", max_length=1024)
            
            tok_length = inputs["input_ids"].shape[1] + tokenizer(instructions, return_tensors='pt', add_special_tokens=False, truncation=True, padding="longest", max_length=1024)["input_ids"].shape[1]
            
            BATCH_SIZE = 5

            with torch.no_grad():
                past_key_values = list(model(input_ids=inputs["input_ids"].to(DEVICE)).past_key_values)

            #
            # autoregressive generation의 경우, query는 마지막으로 생성된 토큰만 사용
            # 그러나, key와 value의 경우에는 지금까지 생성에 사용된 모든 토큰들이 사용됨
            # 따라서, query는 캐싱할 필요가 없으나, key & value는 캐싱해야 함
            #

            for idx0 in range(len(past_key_values)):
                past_key_values[idx0] = list(past_key_values[idx0])
                for idx1 in range(len(past_key_values[idx0])):
                    past_key_values[idx0][idx1] = past_key_values[idx0][idx1].expand(BATCH_SIZE,-1,-1,-1)
            del inputs


        if (idx+1) % BATCH_SIZE == 0 or idx == len(df) - 1:

            inputs = tokenizer(instructions, return_tensors='pt', add_special_tokens=False, truncation=True, padding="longest")

            with torch.no_grad():
                out = model(input_ids=inputs["input_ids"].to(DEVICE), past_key_values=past_key_values).logits
                
                for jjj in range(len(out)):
                    att_idx = inputs["attention_mask"].sum(dim=1)[jjj]-1
                    pooled.append(out[jjj,att_idx,:].float().unsqueeze(0))

            instructions = []
            del out
            del inputs

        if (idx+1) % 5 == 0:
            with torch.no_grad():
                pooled = torch.cat(pooled)
                
                if args.model_type == 2:
                    new_poolings = pooled.reshape(1,-1)
                    new_poolings = new_poolings.reshape(5, new_poolings.size(-1)//5)
                    permutations = list(itertools.permutations(range(new_poolings.size(0))))
                    tta_logits = torch.zeros((5,1)).to(new_poolings.device)
                    for perm in permutations:
                        permuted_poolings = new_poolings[torch.tensor(perm)]
                        o = head(permuted_poolings.float().reshape(1,-1))
                        tta_logits[torch.tensor(perm)] += o.reshape(-1,1)
                    logits = tta_logits / len(permutations)
                    logits = logits[:,0]
                    logits = logits.detach().cpu().numpy()
                else:
                    new_poolings = []

                    indexes = np.arange(0, 5)
                    for jj in indexes:
                        if args.model_type == 1:
                            other_embeddings = pooled[[jjj for jjj in indexes if jjj != jj]]
                            new_poolings.append(torch.cat([pooled[jj], torch.mean(other_embeddings, dim=0)]))
                        else:
                            new_poolings.append(pooled[jj])
                    new_poolings = torch.stack(new_poolings)
                    
                    logits = head(new_poolings)
                    logits = logits[:,0]
                    logits = logits.detach().cpu().numpy()

                for lg in logits:
                    preds.append(lg)

            del logits
            pooled = []

    print(inst)
    np.save(f"scores_{llm_backbone.split('/')[-1]}_{args.test_file[:-3]}", preds)
