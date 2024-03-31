# Reference: <https://github.com/microsoft/DeepSpeed/issues/5049>

import argparse

import torch
from datasets import load_dataset
from torch.optim import AdamW
from torch.utils.data import DataLoader
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig, get_linear_schedule_with_warmup, set_seed

from accelerate import Accelerator, DistributedType
from accelerate.logging import get_logger
from torch.utils.data import Dataset

from accelerate.utils import DummyOptim, DummyScheduler, set_seed

import math

from accelerate.utils import DeepSpeedPlugin, FullyShardedDataParallelPlugin

from transformers import get_scheduler


from deepspeed.utils import set_z3_leaf_modules  # mixtra;
from deepspeed.accelerator import get_accelerator

from transformers.models.mixtral.modeling_mixtral import MixtralSparseMoeBlock, MixtralForCausalLM

from transformers.integrations import is_deepspeed_zero3_enabled

from peft import prepare_model_for_kbit_training, LoraConfig, get_peft_model, PeftModel


MAX_GPU_BATCH_SIZE = 4


class RandomDataset(Dataset):
    def __init__(self, num_samples: int = 1000, max_length: int = 4096, vocab_size: int = 100, tokenizer=None):
        self.num_samples = num_samples
        self.max_length = max_length
        self.input_ids = torch.randint(2, vocab_size, (num_samples, max_length))
        self.attention_mask = torch.ones_like(self.input_ids)

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        return {
            "input_ids": self.input_ids[idx],
            "attention_mask": self.attention_mask[idx],
            "labels": self.input_ids[idx],
        }


def training_function(args):
    get_accelerator().set_device(args.local_rank)

    # Initialize accelerator
    deepPlugin = DeepSpeedPlugin(hf_ds_config='./ds_config.json', zero3_init_flag=True)
    accelerator = Accelerator(mixed_precision='bf16', deepspeed_plugin=deepPlugin, gradient_accumulation_steps=1)

    # Sample hyper-parameters for learning rate, batch size, seed and a few other HPs
    lr = 2e-5
    num_epochs = 2
    seed = 42
    batch_size = 1
    warmup_ratio = 0.03

    model_id = "mistralai/Mixtral-8x7B-v0.1"

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    dataset = RandomDataset(num_samples=1000, tokenizer=tokenizer)
    train_dataloader = DataLoader(
        dataset, shuffle=True, collate_fn=None, batch_size=batch_size, drop_last=True
    )

    if accelerator.is_main_process:
        print(f'before prepare dataloader len: {len(train_dataloader)}')

    num_update_steps_per_epoch = math.ceil(len(train_dataloader) / accelerator.gradient_accumulation_steps)
    max_train_steps = num_epochs * num_update_steps_per_epoch


    config = AutoConfig.from_pretrained(model_id)  #
    model = AutoModelForCausalLM.from_pretrained(
            model_id,
            config=config,
            use_flash_attention_2=True,
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=(not is_deepspeed_zero3_enabled())
        )

    # Prepare model for k-bit training
    model = prepare_model_for_kbit_training(model)
    tokenizer.pad_token = "!" #Not EOS, will explain another time.\

    # CUTOFF_LEN = 256  #Our dataset has shot text
    LORA_R = 8
    LORA_ALPHA = 2 * LORA_R
    LORA_DROPOUT = 0.1

    config = LoraConfig(r=LORA_R,
                        lora_alpha=LORA_ALPHA,
                        target_modules=[ "w1", "w2", "w3"],  #just targetting the MoE layers.lora_dropout=LORA_DROPOUT,
                        bias="none",
                        task_type="CAUSAL_LM",
                        lora_dropout=LORA_DROPOUT
                        )

    model = get_peft_model(model, config)

    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
    model.config.use_cache = False  # turn off when gradient checkpointing is enabled
    print("Gradient checkpointing enabled.")

    set_z3_leaf_modules(model, [MixtralSparseMoeBlock])  # z3_leaf

    model.train() #

    optimizer_cls = (
        torch.optim.AdamW
        if accelerator.state.deepspeed_plugin is None
            or "optimizer" not in accelerator.state.deepspeed_plugin.deepspeed_config
            else DummyOptim
    )

    optimizer = optimizer_cls(params=model.parameters(), lr=lr)


    if (
        accelerator.state.deepspeed_plugin is None
        or "scheduler" not in accelerator.state.deepspeed_plugin.deepspeed_config
    ):
        lr_scheduler = get_scheduler(
            name='linear',
            optimizer=optimizer,
            num_warmup_steps=math.ceil(max_train_steps * warmup_ratio),
            num_training_steps=max_train_steps,
        )
    else:
        lr_scheduler = DummyScheduler(
            optimizer, total_num_steps=max_train_steps, warmup_num_steps=math.ceil(max_train_steps * warmup_ratio)
        )

    model, optimizer, train_dataloader, lr_scheduler = accelerator.prepare(
        model, optimizer, train_dataloader, lr_scheduler
    )


    # Now we train the model
    for epoch in range(num_epochs):
        for step, batch in enumerate(train_dataloader):
            with accelerator.accumulate(model):
                model.train()
                outputs = model(**batch)
                loss = outputs.loss

                print(f" epoch: {epoch}, step: {step} loss: {loss}")

                accelerator.backward(loss)

                print(f"finish backward")

                optimizer.step()
                lr_scheduler.step()
                optimizer.zero_grad()

                print(f"finish optimizer step")



def main():
    parser = argparse.ArgumentParser(description="Simple example of training script.")
    parser.add_argument(
        "--model_path",
        type=str,
        default="path_to_mixtral-8x7b",)
    parser.add_argument(
        "--mixed_precision",
        type=str,
        default="bf16",
        choices=["no", "fp16", "bf16", "fp8"],
        help="Whether to use mixed precision. Choose"
        "between fp16 and bf16 (bfloat16). Bf16 requires PyTorch >= 1.10."
        "and an Nvidia Ampere GPU.",
    )
    parser.add_argument(
        "--local_rank",
        type=int,
        default=-1,
    )
    args = parser.parse_args()
    training_function(args)


if __name__ == "__main__":
    main()
