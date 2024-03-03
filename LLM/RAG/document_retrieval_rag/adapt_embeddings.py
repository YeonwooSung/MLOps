import os
import openai
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from tqdm import tqdm
import chromadb
from llama_index import HuggingFaceEmbedding
import torch
import numpy as np


_ = load_dotenv(find_dotenv())
openai.api_key = os.environ['OPENAI_API_KEY']

openai_client = OpenAI()

# create client and a new collection
chroma_client = chromadb.EphemeralClient()
chroma_collection = chroma_client.create_collection("quickstart")

# define embedding function
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

#
# define prompts
#

PROMPT_DATASET = """
You are a helpful expert financial research assistant. 
You help users analyze financial statements to better understand companies.
Suggest 10 to 15 short questions that are important to ask when analyzing 
an annual report.
Do not output any compound questions (questions with multiple sentences 
or conjunctions).
Output each question on a separate line divided by a newline.
"""

PROMPT_EVALUATION = """
You are a helpful expert financial research assistant. 
You help users analyze financial statements to better understand companies.
For the given query, evaluate whether the following satement is relevant.
Output only 'yes' or 'no'.
"""


def generate_queries(model="gpt-3.5-turbo"):
    messages = [
        {
            "role": "system",
            "content": PROMPT_DATASET,
        },
    ]

    response = openai_client.chat.completions.create(
        model=model,
        messages=messages,
    )
    content = response.choices[0].message.content
    content = content.split("\n")
    return content


def evaluate_results(query, statement, model="gpt-3.5-turbo"):
    messages = [
    {
        "role": "system",
        "content": PROMPT_EVALUATION,
    },
    {
        "role": "user",
        "content": f"Query: {query}, Statement: {statement}"
    }
    ]

    response = openai_client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=1
    )
    content = response.choices[0].message.content
    if content == "yes":
        return 1
    return -1


def embedding_function(texts):
    return embed_model.encode(texts)


generated_queries = generate_queries()
for query in generated_queries:
    print(query)


results = chroma_collection.query(query_texts=generated_queries, n_results=10, include=['documents', 'embeddings'])
retrieved_documents = results['documents']

retrieved_embeddings = results['embeddings']
query_embeddings = embedding_function(generated_queries)

#
# Now we structure the training data into tuples.
#
# Each tuple will contain the embedding of the query, the embedding of a document, and the evaluation label (1, -1).
#

adapter_query_embeddings = []
adapter_doc_embeddings = []
adapter_labels = []

for q, query in enumerate(tqdm(generated_queries)):
    for d, document in enumerate(retrieved_documents[q]):
        adapter_query_embeddings.append(query_embeddings[q])
        adapter_doc_embeddings.append(retrieved_embeddings[q][d])
        adapter_labels.append(evaluate_results(query, document))

#
# When tuples are created, we put them in a Torch Dataset to prepare for the training.
#

adapter_query_embeddings = torch.Tensor(np.array(adapter_query_embeddings))
adapter_doc_embeddings = torch.Tensor(np.array(adapter_doc_embeddings))
adapter_labels = torch.Tensor(np.expand_dims(np.array(adapter_labels),1))
dataset = torch.utils.data.TensorDataset(adapter_query_embeddings, adapter_doc_embeddings, adapter_labels)

#
# Define the model
#
# We define a function that takes the query embedding, the document embedding, and the adaptor matrix as input.
# This function first multiplies the query embedding with the adaptor matrix and computes a cosine similarity between this result and the document embedding.
#

def model(query_embedding, document_embedding, adaptor_matrix):
    updated_query_embedding = torch.matmul(adaptor_matrix, query_embedding)
    return torch.cosine_similarity(updated_query_embedding, document_embedding, dim=0)

#
# Define the loss function
#
# Our goal is to minimize the cosine similarity computed by the previous function.
# To do this, we’ll use a Mean Square Error (MSE) loss to optimize the weights of the adaptor matrix.
#
def mse_loss(query_embedding, document_embedding, adaptor_matrix, label):
    return torch.nn.MSELoss()(model(query_embedding, document_embedding, adaptor_matrix), label)


#
# Run backpropagation
#

# Initialize the adaptor matrix
mat_size = len(adapter_query_embeddings[0])
adapter_matrix = torch.randn(mat_size, mat_size, requires_grad=True)

min_loss = float('inf')
best_matrix = None
for epoch in tqdm(range(100)):
    for query_embedding, document_embedding, label in dataset:
        loss = mse_loss(query_embedding, document_embedding, adapter_matrix, label)
        if loss < min_loss:
            min_loss = loss
            best_matrix = adapter_matrix.clone().detach().numpy()
        loss.backward()
        with torch.no_grad():
            adapter_matrix -= 0.01 * adapter_matrix.grad
            adapter_matrix.grad.zero_()
print("Best loss:", min_loss)

# Once the training is complete, the adapter can be used to scale the original embedding and adapt to the user task.
#
# All you need now is to take the original embedding output and multiply it with the adaptor matrix before feeding it to the retrieval system.

test_vector = torch.ones((mat_size,1))
scaled_vector = np.matmul(best_matrix, test_vector).numpy()

print(f"test_vector.shape: {test_vector.shape}")
print(f"scaled_vector.shape: {scaled_vector.shape}")
print(f"best_matrix.shape: {best_matrix.shape}")
