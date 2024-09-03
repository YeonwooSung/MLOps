from transformers import AutoProcessor, AutoModelForCausalLM
from vrag.cfg import ModelCfg, KeywordGenerationCfg, QuestionAnsweringCfg, RetrievedPassage, RetrievalCfg
from transformers.image_utils import load_image
from PIL import Image
from vrag.wiki_retrieval import WikipediaRetriever


def format_messages(prompt: str) -> list:
    messages = [{
        "role": "user",
        "content": "<|image_1|>\n" + prompt,
    }
    ]
    return messages


class VisualQuestionRAG:
    """Pipeline for Visual Question Answering with Retrieval Augmented Generation from Wikipedia.
       Attributes:
             cfg: the model configuration.
             model: the loaded Vision Language Model.
             processor: the huggingface transformers' processor for the VLM.
             retriever: an instance of the Wikipedia retriever to be used for retrieval.
    """

    def __init__(self,
                 retriever: WikipediaRetriever,
                 cfg: ModelCfg = ModelCfg(),
                 ):
        self.cfg = cfg
        self.model = AutoModelForCausalLM.from_pretrained(cfg.model,
                                                          torch_dtype=cfg.torch_dtype,
                                                          device_map=cfg.device_map,
                                                          **cfg.model_kwargs)
        self.processor = AutoProcessor.from_pretrained(cfg.model, **cfg.processor_kwargs)
        self.retriever = retriever

    def generate(self,
                 prompt: str,
                 img: Image.Image,
                 **kwargs) -> str:
        messages = format_messages(prompt)
        text = self.processor.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(text, [img], return_tensors="pt").to(self.model.device)
        generated_tokens = self.model.generate(**inputs,
                                               eos_token_id=self.processor.tokenizer.eos_token_id,
                                               **kwargs)[:, inputs['input_ids'].shape[1]:]
        generated_text = self.processor.batch_decode(generated_tokens,
                                                     skip_special_tokens=True,
                                                     clean_up_tokenization_spaces=False)[0]

        return generated_text

    def generate_keywords(self,
                          query: str,
                          img: str | Image.Image,
                          template: KeywordGenerationCfg = KeywordGenerationCfg(),
                          ) -> str:
        prompt = template.format_template(query)
        generated_text = self.generate(prompt=prompt, img=img, **template.generation_kwargs)
        return generated_text

    def rag_question_answering(self,
                               question: str,
                               retrieval_results: list[RetrievedPassage],
                               img: str | Image.Image,
                               template: QuestionAnsweringCfg = QuestionAnsweringCfg(),
                               ) -> str:
        prompt = template.format_template(question=question, retrieval_results=retrieval_results)
        generated_text = self.generate(prompt=prompt,
                                       img=img,
                                       **template.generation_kwargs)
        return generated_text

    def __call__(self,
                 question: str,
                 img_or_img_path: str | Image.Image,
                 keyword_generation_cfg: KeywordGenerationCfg = KeywordGenerationCfg(),
                 retrieval_cfg: RetrievalCfg = RetrievalCfg(),
                 answer_generation_cfg: QuestionAnsweringCfg = QuestionAnsweringCfg(),
                 ) -> tuple[str, str, list[RetrievedPassage]]:
        """
        Args:
            question: The user's question.
            img_or_img_path: If a string, the image will be loaded from the path or url. Otherwise, a PIL Image object
                             is accepted.
            keyword_generation_cfg: an instance of the KeywordGenerationCfg class. It specifies the configuration for
                                    keyword generation.
            retrieval_cfg: an instance of the RetrievalCfg class. It specifies the configuration for passage retrieval.
            answer_generation_cfg: an instance of the QuestionAnsweringCfg class. It specifies the configuration for the
                                   generation of the retrieval augmented answer.


        Returns:
           A tuple containing the answer to the user's question, the keywords used for retrieval, and the selected
           passages.

        """
        img = load_image(img_or_img_path)
        keywords = self.generate_keywords(query=question, img=img, template=keyword_generation_cfg)
        selected_passages = self.retriever(question=question, keywords=keywords, retrieval_cfg=retrieval_cfg)
        answer = self.rag_question_answering(question=question,
                                             img=img,
                                             retrieval_results=selected_passages,
                                             template=answer_generation_cfg)
        return answer, keywords, selected_passages
