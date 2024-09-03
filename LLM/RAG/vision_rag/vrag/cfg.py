from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from importlib import resources as resources
from typing import Callable

import torch


@dataclass
class ModelCfg:
    model: str = "microsoft/Phi-3.5-vision-instruct"
    device_map: str = 'cuda'
    torch_dtype: torch.dtype | str = torch.float16
    model_kwargs: dict = field(default_factory=lambda: {'trust_remote_code':True, '_attn_implementation': 'eager'})
    #CHANGE _ATTN_IMPLENTATION TO 'flash_attention_2' IF SUPPORTED
    processor_kwargs: dict = field(default_factory=lambda: {'trust_remote_code':True, 'num_crops':16})


@dataclass
class RetrievalCfg:
    n_pages: int = 20
    n_passages: int = 7
    chunk_size: int = 300
    chunk_overlap: int = 150
    separators: list = field(default_factory=lambda: ["\n\n", "\n", ".", ","])
    length_function: Callable = len
    query_separator: str = 'Keywords: '


@dataclass
class EmbeddingModelCfg:
    embedding_model_name: str = "Snowflake/snowflake-arctic-embed-l"
    embedding_model_kwargs: dict = field(default_factory=lambda: {'device': 'cuda',
                                                                  'model_kwargs': {'torch_dtype': torch.float16},
                                                                  })
    encode_kwargs: dict = field(default_factory=lambda: {'normalize_embeddings': True})


@dataclass
class RetrievedPassage:
    passage: str
    page: str
    url: str


class TemplateCfg(ABC):
    template: str
    generation_kwargs: dict

    @abstractmethod
    def format_template(self, *args, **kwargs):
        raise NotImplementedError


def load_template(file: str) -> str:
    with resources.files("vrag.templates").joinpath(file).open('r') as f:
        instruction_template = f.read()
    return instruction_template


@dataclass
class KeywordGenerationCfg(TemplateCfg):
    template: str = load_template("keyword_generation.txt")
    prompt_addition: str = 'Keywords: '
    generation_kwargs: dict = field(default_factory=lambda: {'max_new_tokens': 64})

    def format_template(self, question: str) -> str:
        return self.template.format(question=question)


@dataclass
class QuestionAnsweringCfg(TemplateCfg):
    qa_template: str = load_template('question_answering.txt')
    passage_template: str = load_template('passage_quote.txt')
    generation_kwargs: dict = field(default_factory=lambda: {'max_new_tokens': 256})
    model_answer_split: str = 'Assistant: '

    def format_template(self, question: str, retrieval_results: list[RetrievedPassage]) -> str:
        retrieved = ''
        for result in retrieval_results:
            retrieved += self.passage_template.format(page=result.page, passage=result.passage)
        return self.qa_template.format(passages=retrieved, question=question)
