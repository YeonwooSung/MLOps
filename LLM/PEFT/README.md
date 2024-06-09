# Parameter Efficient Fine-Tuning

PEFT (Parameter-Efficient Fine-Tuning) is a technology for efficiently adapting large pretrained models to various downstream applications without fine-tuning all of a model’s parameters because it is prohibitively costly.
PEFT methods only fine-tune a small number of (extra) model parameters - significantly decreasing computational and storage costs - while yielding performance comparable to a fully fine-tuned model.
This makes it more accessible to train and store large language models (LLMs) on consumer hardware.

## ReFT

ReFT methods operate on a frozen base model and learn task-specific interventions on hidden representations.
It tries to find the intervention or hidden representation that is most useful for the downstream task, and then fine-tunes the model to use this representation.

## References

- [HuggingFace PEFT](https://huggingface.co/docs/peft/en/index)
- [pyreft](https://github.com/stanfordnlp/pyreft)

### Papers

- [ReFT: Representation Finetuning for Language Models](https://arxiv.org/abs/2404.03592)
