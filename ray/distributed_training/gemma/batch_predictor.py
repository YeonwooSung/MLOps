# General
import argparse
import os
from huggingface_hub import login

# Serving
import datasets
import transformers
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers.pipelines import pipeline

# Ray
import ray

# Settings
datasets.disable_progress_bar()

# Variables
base_model_path = "google/gemma-2b-it"


# helpers
def get_args():
    parser = argparse.ArgumentParser(description='Batch prediction with Gemma on Ray on Vertex AI')
    parser.add_argument('--tuned_model_path', type=str, help='path of adapter model')
    parser.add_argument('--num_gpus', type=int, default=1, help='number of gpus')
    parser.add_argument('--batch_size', type=int, default=8, help='batch size')
    parser.add_argument('--sample_size', type=int, default=20, help='number of articles to summarize')
    parser.add_argument('--temperature', type=float, default=0.1, help='temperature for generating summaries')
    parser.add_argument('--max_new_tokens', type=int, default=50, help='max new token for generating summaries')
    parser.add_argument('--output_dir', type=str, help='output directory for predictions')
    args = parser.parse_args()
    return args


def main():

    # Set configuration
    args = get_args()
    config = vars(args)

    # Setting training
    login(token=os.environ['HF_TOKEN'], add_to_git_credential=True)
    transformers.set_seed(8)

    # Load dataset
    dataset_id = "xsum"
    sample_size = config["sample_size"]
    input_data = datasets.load_dataset(dataset_id, split="validation", trust_remote_code=True)
    input_data = input_data.select(range(sample_size))
    ray_input_data = ray.data.from_huggingface(input_data)

    # Generate predictions

    class Summarizer:

        def __init__(self):
            self.tokenizer = AutoTokenizer.from_pretrained(base_model_path)
            self.tokenizer.padding_side = "right"

            self.tuned_model = AutoModelForCausalLM.from_pretrained(
                config["tuned_model_path"],
                device_map='auto',
                torch_dtype=torch.float16
            )

            self.pipeline = pipeline(
                "text-generation",
                model=self.tuned_model,
                tokenizer=self.tokenizer,
                max_new_tokens=config["max_new_tokens"]
            )

        def __call__(self, batch: np.ndarray):

            # prepare dataset
            messages = [
                {
                    "role": "user",
                    "content": f"Summarize the following ARTICLE in one sentence.\n###ARTICLE: {document}"
                }
                for document in batch["document"]
            ]

            batch['prompt'] = [
                self.tokenizer.apply_chat_template([message], tokenize=False, add_generation_prompt=True)
                for message in messages
            ]

            # generate
            batch['generated_summary'] = [
                self.pipeline(
                    prompt,
                    do_sample=True,
                    temperature=config["temperature"],
                    add_special_tokens=True
                )[0]["generated_text"][len(prompt):]
                for prompt in batch['prompt']
            ]

            return batch


    predictions_data = ray_input_data.map_batches(
        Summarizer,
        concurrency=config["num_gpus"],
        num_gpus=1,
        batch_size=config['batch_size']
    )

    # Store resulting predictions
    predictions_data.write_json(config["output_dir"], try_create_dir=True)


if __name__ == "__main__":
    main()
