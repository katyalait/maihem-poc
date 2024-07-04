"""Module for creating vectorised data"""

import os

import pandas as pd
from openai import OpenAI
from unstructured.documents.elements import CompositeElement

from maihem_poc.data.loader import handle_docx, handle_pdf

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")


def get_embedding_openai(element: CompositeElement, model: str):
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    text = element.text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def vector_from_data(
    filename: str,
    file_type: str = "auto",
) -> pd.DataFrame:

    filename_no_path = filename.rsplit("/", maxsplit=1)[1]
    if file_type == "pdf":
        # in case we want to parallelize this at some point
        vectors = [
            (text, filename_no_path) for text in handle_pdf(filename)
        ]
    elif file_type == "docx":
        # in case we want to parallelize this at some point
        vectors = [
            (text, filename_no_path)
            for text in handle_docx(filename)
        ]
    else:
        raise TypeError("Unknown file type for vectoriser function `vector_from_data`")

    return pd.DataFrame(vectors, columns=["text", "filename"])


def create_vectordb(filename: str, file_type: str = "auto"):
    if file_type == "auto":
        if filename.endswith(".pdf"):
            file_type = "pdf"
        if filename.endswith(".docx"):
            file_type = "docx"
    vector_df = vector_from_data(filename, file_type)
    vector_df.to_csv(f"{filename}_vectordb.csv", index=False)
