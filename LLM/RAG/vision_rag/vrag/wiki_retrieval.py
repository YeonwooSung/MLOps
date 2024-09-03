import warnings

import wikipedia
from wikipedia import WikipediaPage
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from vrag.cfg import RetrievalCfg, EmbeddingModelCfg, RetrievedPassage


class WikipediaRetriever:
    def __init__(self,
                 embedding_cfg: EmbeddingModelCfg = EmbeddingModelCfg(),
                 ):
        self.embeddings_cfg = embedding_cfg
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_cfg.embedding_model_name,
                                                model_kwargs=embedding_cfg.embedding_model_kwargs,
                                                encode_kwargs=embedding_cfg.encode_kwargs)

    @staticmethod
    def find_pages(keywords: str, n_pages: int) -> list[WikipediaPage]:
        titles = wikipedia.search(keywords, results=n_pages)
        pages = []
        for t in titles:
            try:
                pages.append(wikipedia.page(t, auto_suggest=False))
            except Exception as e:
                warnings.warn(str(e))
        return pages

    def select_passages(self,
                        pages: list[WikipediaPage],
                        question: str,
                        keywords: str,
                        retrieval_cfg: RetrievalCfg) -> list[RetrievedPassage]:
        splitter = RecursiveCharacterTextSplitter(chunk_size=retrieval_cfg.chunk_size,
                                                  chunk_overlap=retrieval_cfg.chunk_overlap,
                                                  length_function=retrieval_cfg.length_function,
                                                  )
        page_splits = splitter.create_documents(texts=[p.content for p in pages],
                                                metadatas=[{'page_no': i} for i in range(len(pages))])
        db = FAISS.from_documents(page_splits, self.embeddings)
        docs = db.similarity_search(question + retrieval_cfg.query_separator + keywords,
                                    k=retrieval_cfg.n_passages)
        return [RetrievedPassage(passage=docs[i].page_content,
                                 page=pages[docs[i].metadata['page_no']].title,
                                 url=pages[docs[i].metadata['page_no']].url)
                for i in range(retrieval_cfg.n_passages)]

    def __call__(self,
                 question: str,
                 keywords: str,
                 retrieval_cfg: RetrievalCfg) -> list[RetrievedPassage]:
        pages = self.find_pages(keywords, n_pages=retrieval_cfg.n_pages)
        if len(pages) < 1:
            warnings.warn(f"Unable to retrieve any page with the keywords {keywords}")
            selected_passages = []
        else:
            selected_passages = self.select_passages(pages=pages,
                                                     question=question,
                                                     keywords=keywords,
                                                     retrieval_cfg=retrieval_cfg)
        return selected_passages
