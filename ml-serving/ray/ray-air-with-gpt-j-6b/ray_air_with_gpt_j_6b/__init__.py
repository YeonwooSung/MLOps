import ray

model_id = "EleutherAI/gpt-j-6B"
revision = "float16"  # use float16 weights to fit in 16GB GPUs
prompt = (
    "In a shocking finding, scientists discovered a herd of unicorns living in a remote, "
    "previously unexplored valley, in the Andes Mountains. Even more surprising to the "
    "researchers was the fact that the unicorns spoke perfect English."
)

ray.init(
    runtime_env={
        "pip": [
            "accelerate>=0.16.0",
            "transformers>=4.26.0",
            "torch",
        ]
    }
)
