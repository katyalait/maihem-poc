"""Module for creating vectorised data"""

import os

import pandas as pd
from openai import OpenAI

from .loader import handle_pdf

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")


def get_embedding_openai(text):
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    text = text.replace("\n", " ")
    return (
        client.embeddings.create(
            input=[text], model="nomic-ai/nomic-embed-text-v1.5-GGUF"
        )
        .data[0]
        .embedding
    )


def vectorise_chunks(chunks: list, embedding_function: str, **embedding_kwargs) -> list:
    """Convert each chunk using hte nominated embedding function"""
    embedding_function = getattr(__name__, embedding_function)
    for chunk in chunks:
        yield chunk, embedding_function(chunk, **embedding_kwargs)


def vector_from_data(
    filename: str,
    file_type: str = "auto",
    embedding_function: str = "get_embedding",
    **kwargs
) -> pd.DataFrame:
    with open(filename, encoding="utf-8") as f:
        file = f.read()

    if file_type == "pdf":
        # in case we want to parallelize this at some point
        vectors = [
            (text, embedding, filename)
            for text, embedding in vectorise_chunks(
                handle_pdf(file), embedding_function, **kwargs
            )
        ]
    else:
        raise TypeError("Unknown file type for vectoriser function `vector_from_data`")

    return pd.DataFrame(vectors, columns=["text", "embedding", "filename"])


def create_vectordb(filename: str, file_type: str = "auto", **kwargs):
    if file_type == "auto":
        if filename.endswith(".pdf"):
            file_type = "pdf"
        ...
    vector_df = vector_from_data(filename, file_type, **kwargs)
