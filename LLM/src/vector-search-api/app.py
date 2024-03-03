import os
import requests
from flask import Flask, request, abort
from flask_cors import CORS
import json
from qdrant_client import QdrantClient
from qdrant_client.models import Filter
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = "neuralmind/bert-base-portuguese-cased"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

app = Flask(__name__)
CORS(app)

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
encoder = SentenceTransformer(model_name_or_path=EMBEDDING_MODEL, device="cpu")


def get_ids(args) -> list:
    """Extracts ids from request query string"""
    ids = request.args.get("ids", default="", type=str)
    if ids == "":
        return []

    if "," in ids:
        return ids.split(",")

    return [ids]


def get_filters(args) -> dict:
    """Auxiliary function to extract filters from query string"""
    must = [
        models.FieldCondition(
            key=arg.replace("filter.", ""), match=models.MatchValue(value=args.get(arg))
        )
        for arg in request.args
        if "filter." in arg
    ]

    return Filter(must=must)


@app.get("/<string:collection>/item")
def get_item(collection: str, seed_ids: str = None) -> dict:
    """Gets items based on given ids"""
    if seed_ids is None:
        seed_ids = get_ids(request.args)

    results = client.scroll(
        collection_name=collection,
        with_payload=["item_id", "title", "description"],
        with_vectors=False,
        scroll_filter=Filter(
            must=[
                models.FieldCondition(
                    key="item_id", match=models.MatchAny(any=seed_ids)
                ),
            ]
        ),
    )

    return [json.loads(result.model_dump_json()) for result in results[0]]


@app.get("/<string:collection>/similars")
def get_similars(collection: str) -> dict:
    lim = request.args.get("lim", default=10, type=int)
    ids = get_ids(request.args)
    score = request.args.get("score", default=0, type=float)
    filters = get_filters(request.args)

    seeds = get_item(collection, seed_ids=ids)
    seed_ids = [seed["id"] for seed in seeds]

    results = client.recommend(
        collection_name=collection,
        positive=seed_ids,
        negative=None,
        limit=lim,
        with_payload=["item_id", "title", "description"],
        with_vectors=False,
        score_threshold=score,
        query_filter=filters,
    )

    return [json.loads(result.model_dump_json()) for result in results]


@app.get("/<string:collection>/query")
def query(collection: str):
    """Query documents based on text string"""
    text = request.args.get("text", default="", type=str)
    lim = request.args.get("lim", default=10, type=int)
    filters = get_filters(request.args)

    results = client.search(
        collection_name=collection,
        query_vector=encoder.encode(text),
        limit=lim,
        with_payload=["item_id", "title", "description"],
        with_vectors=False,
        query_filter=filters,
    )

    return [json.loads(result.model_dump_json()) for result in results]


@app.get("/<string:collection>")
def info(collection: str):
    """Query documents based on text string"""
    collection = client.get_collection(collection_name=collection)

    return json.loads(collection.model_dump_json())


@app.get("/")
def ping():
    """Checks if connection to Qdrant is okay"""
    return json.loads(client.get_collections().model_dump_json())
