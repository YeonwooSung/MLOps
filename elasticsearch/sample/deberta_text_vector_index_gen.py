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
    {"text": "The name of the game is to find the best sentence"},
    {"text": "The quick brown fox jumps over the lazy dog"},
    {"text": "The quick brown fox jumps over the lazy cat"},
    {"text": "The quick brown fox jumps over the lazy rabbit"},
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


# Query the index with a sample text
query_text = "Example sentence"
query_embedding = generate_embedding(query_text)

# Perform a cosine similarity search (retrieve top 5 similar documents)
query = {
    "query": {
        "script_score": {
            "query": {
                "match_all": {}
            },
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                "params": {
                    "query_vector": query_embedding
                }
            }
        }
    },
    "size": 5
}

# Execute the search query
response = es.search(index=index_name, body=query)

# Print the search results
print("Search results:")
for hit in response["hits"]["hits"]:
    print(f"Document: {hit['_source']['text']}")
    print(f"Similarity score: {hit['_score']}")
    print()
