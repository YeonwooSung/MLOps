# Train LLM on M1 Macbook

1. Install mlx-lm
```bash
pip insall mlx-lm
```

2. Log in to huggingface hub

```bash
huggingface-hub login
```

3. Download and convert dataset into jsonl format (refer [this repo](https://github.com/ml-explore/mlx-examples/blob/main/llms/mlx_lm/LORA.md#data))

- [Sample dataset for training](https://huggingface.co/datasets/gretelai/synthetic_text_to_sql)

4. Download and convert the huggingface model to mlx compatible one
```bash
python -m mlx_lm.convert --hf-path meta-llama/Meta-Llama-3-8B --mlx-path models/mlx -q
```

5. Finetuning

```bash
python -m mlx_lm.lora --model models/mlx --data data/synthetic_text_to_sql --train --iters 1000
```

6. Generation

```bash
python -m mlx_lm.generate --model models/mlx \
                --max-tokens 500 \
               --adapter-path adapters \
               --prompt "List all transactions and customers from the 'Africa' region."
```

## References

- [Part 3: Fine-tuning your LLM using the MLX framework](https://apeatling.com/articles/part-3-fine-tuning-your-llm-using-the-mlx-framework/)
