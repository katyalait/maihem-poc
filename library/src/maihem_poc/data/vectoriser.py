"""Module for creating vectorised data"""

import os

import pandas as pd

from maihem_poc.data.loader import handle_docx, handle_pdf
from maihem_poc.data.db import save_file, load_file

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")


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
    save_file(vector_df, filename, 'vectordb')
