from transformers import AutoModel, AutoTokenizer
import torch
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


# Initialize model and tokenizer
model_name = "BlackBeenie/mdeberta-v3-base-msmarco-v3-bpr"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)


ES_PASSWORD = ""
# Initialize Elasticsearch client
es = Elasticsearch(
    "https://localhost:9200",
    http_auth=("elastic", ES_PASSWORD),  # Replace with actual credentials
    verify_certs=False,
)

index_name = "text-vector-index"
mapping = {
    "mappings": {
        "properties": {
            "vector": {
                "type": "dense_vector",
                "dims": 768,
                "index": 'true',
            },
            "text": {
                "type": "text"
            }
        }
    }
}

# Create an index with the specified mapping
es.indices.create(index=index_name, body=mapping, ignore=400)


# Function to generate BERT embeddings
def generate_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding="max_length", max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    # Get the mean of the last hidden state as the embedding
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embedding.tolist()

# Example documents
documents = [
    {"text": "Example sentence 1"},
    {"text": "Example sentence 2"},
    {"text": "Another example sentence"},
    {"text": "Yet another example sentence"},
    {"text": "One more example sentence"},
    {"text": "The final example sentence"},
]

# Prepare documents with embeddings for bulk indexing
def prepare_documents(docs):
    global index_name
    for doc in docs:
        embedding = generate_embedding(doc["text"])
        yield {
            "_index": index_name,
            "_source": {
                "text": doc["text"],
                "vector": embedding,
            }
        }

# Bulk index documents with embeddings
bulk(es, prepare_documents(documents))

print("Documents indexed successfully.")
