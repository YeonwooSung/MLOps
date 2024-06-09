# Different Techniques of Finetuning

There are several ways to fine-tune language models for specific tasks. Below are some of the popular methods:

1. Full Fine-Tuning
2. Parameter Efficient Fine-Tuning (PEFT)
3. Alignment Training

## 1. Full Fine-Tuning

*Full Fine-Tuning*

A process in which a pre-trained model learns from scratch with entirely new data.
It updates all the layers and parameters of the model.
Though it can potentially result in high accuracy, it remains computationally expensive and time-consuming.
Ideally, it should be used against tasks that differ quite significantly from the one the model was originally trained on.

## 2. PEFT

*Parameter Efficient Fine-Tuning (PEFT)*

Under the PEFT approach, only a slice — or small updates on parameters — is done to only a small part of the model.
This often involves freezing some layers or parts of the model.
This way, the model is finetuned more quickly and with less resource usage.
The following are among the most popular ways: LoRA (Low Rank Adaptation), AdaLoRA, and Adaption Prompt (LLaMA Adapter).
PEFT could be helpful for transfer learning in a few cases where the new job is much the same as the task for which the model originated.
Here is a description of the practice of [QLoRA finetuning](https://levelup.gitconnected.com/unleash-mistral-7b-power-how-to-efficiently-fine-tune-a-llm-on-your-own-data-4e4386a6bbdc?gi=2592c2a8632a).

## 3. Alignment Training

*Alignment Training*

This is a method for aligning a model with human preferences to increase its utility and safety.
By leveraging human or AI preference in the training loop, one can attain large improvements.
And here’s a somewhat simple implementation if you’d like to try one that’s a bit easier than the usual RLHF: training by [Direct Preference Optimization (DPO)](https://towardsdatascience.com/optimizing-small-language-models-on-a-free-t4-gpu-008c37700d57).
