# libraries
import argparse

# ray libraries
import ray
import ray.train.huggingface.transformers
from ray.train import ScalingConfig, RunConfig, CheckpointConfig
from ray.train.torch import TorchTrainer

# custom module
from train import train_func


# helpers
def get_args():
    parser = argparse.ArgumentParser(description='Supervised tuning Gemma on Ray on Vertex AI')

    # some gemma parameters
    parser.add_argument("--train_batch_size", type=int, default=1, help="train batch size")
    parser.add_argument("--eval_batch_size", type=int, default=1, help="eval batch size")
    parser.add_argument("--gradient_accumulation_steps", type=int, default=4, help="gradient accumulation steps")
    parser.add_argument("--learning_rate", type=float, default=2e-4, help="learning rate")
    parser.add_argument("--max_steps", type=int, default=100, help="max steps")
    parser.add_argument("--save_steps", type=int, default=10, help="save steps")
    parser.add_argument("--logging_steps", type=int, default=10, help="logging steps")

    # ray parameters
    parser.add_argument('--num-workers', dest='num_workers', type=int, default=1, help='Number of workers')
    parser.add_argument('--use-gpu', dest='use_gpu', action='store_true', default=False, help='Use GPU')
    parser.add_argument('--experiment-name', dest='experiment_name', type=str, default='gemma-on-rov', help='Experiment name')
    parser.add_argument('--logging-dir', dest='logging_dir', type=str, help='Logging directory')
    args = parser.parse_args()
    return args


def main():

    args = get_args()
    config = vars(args)

    # initialize ray session
    ray.shutdown()
    ray.init()

    # training config
    train_loop_config = {
        "per_device_train_batch_size": config['train_batch_size'],
        "per_device_eval_batch_size": config['eval_batch_size'],
        "gradient_accumulation_steps": config['gradient_accumulation_steps'],
        "learning_rate": config['learning_rate'],
        "max_steps": config['max_steps'],
        "save_steps": config['save_steps'],
        "logging_steps": config['logging_steps'],
    }
    scaling_config = ScalingConfig(num_workers=config['num_workers'], use_gpu=config['use_gpu'])
    run_config = RunConfig(
        checkpoint_config=CheckpointConfig(num_to_keep=5,
        checkpoint_score_attribute="loss",
        checkpoint_score_order="min"),
        storage_path=config['logging_dir'],
        name=config['experiment_name']
    )
    trainer = TorchTrainer(
        train_loop_per_worker=train_func,
        train_loop_config=train_loop_config,
        run_config=run_config,
        scaling_config=scaling_config
    )
    # train
    _ = trainer.fit()

    ray.shutdown()


if __name__ == "__main__":
    main()
