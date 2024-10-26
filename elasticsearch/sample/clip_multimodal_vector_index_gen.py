from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
import json
import base64
from PIL import Image
import io
import requests


# Initialize the CLIP model for embeddings
model = SentenceTransformer("clip-ViT-B-32-multilingual-v1")

ES_PASSWORD = ""
# Initialize Elasticsearch client
es = Elasticsearch(
    "https://localhost:9200",
    http_auth=("elastic", ES_PASSWORD),  # Replace with actual credentials
    verify_certs=False,
)

# Create index with a custom mapping for embedding storage
index_name = "multimodal-index"

# Define Elasticsearch index mapping
mapping = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "text": {"type": "text"},
            "image": {"type": "binary"},
            "embedding": {"type": "dense_vector", "dims": 512}
        }
    }
}


# Check if index exists, if not, create it
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=mapping)

def encode_image(image_path_or_url):
    """Load and encode an image as a base64 string."""
    if image_path_or_url.startswith('http'):
        image = Image.open(requests.get(image_path_or_url, stream=True).raw)
    else:
        image = Image.open(image_path_or_url)
    
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def generate_and_index_document(text, image_path_or_url, doc_id):
    """
    Generates embeddings for text and image, and indexes them into Elasticsearch.
    :param text: The text to be indexed.
    :param image_path_or_url: Path or URL of the image.
    :param doc_id: Unique identifier for the document.
    """
    # Generate text and image embeddings using CLIP model
    embeddings = model.encode([text, Image.open(image_path_or_url)], convert_to_tensor=True)
    
    # Encode image to binary (base64) for Elasticsearch
    image_data = encode_image(image_path_or_url)
    
    # Prepare the document
    doc = {
        "id": doc_id,
        "text": text,
        "image": image_data,
        "embedding": embeddings[0].cpu().numpy().tolist()  # Store embedding as list of floats
    }

    # Index document into Elasticsearch
    es.index(index=index_name, id=doc_id, body=doc)
    print(f"Indexed document with ID: {doc_id}")


# Example usage: Index multiple documents
documents = [
    {"text": "A scenic mountain view.", "image": "path_or_url_to_image_1.jpg", "id": "1"},
    {"text": "A cat sitting on the grass.", "image": "path_or_url_to_image_2.jpg", "id": "2"},
    # Add more documents as needed
]

# Index each document
for doc in documents:
    generate_and_index_document(doc["text"], doc["image"], doc["id"])
