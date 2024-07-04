"""Module to load and parse the data."""

from unstructured.chunking.title import chunk_by_title
from unstructured.partition.pdf import partition_pdf


def handle_pdf(file):
    """Handles PDF files and converts them to"""
    elements = partition_pdf("example-docs/layout-parser-paper-fast.pdf")
    chunks = chunk_by_title(elements)
    return chunks
