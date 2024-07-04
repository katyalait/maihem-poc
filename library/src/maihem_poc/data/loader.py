"""Module to load and parse the data."""
from unstructured.chunking.title import chunk_by_title
from unstructured.partition.docx import partition_docx
from unstructured.partition.pdf import partition_pdf


def chunker(elements):
    return chunk_by_title(elements, max_characters=500)


def handle_pdf(file):
    """Handles PDF files and converts them to"""
    elements = partition_pdf(file)
    chunks = chunk_by_title(elements)
    return chunks


def handle_docx(file):
    """Handles docx files and converts them to chunks"""
    elements = partition_docx(file)
    chunks = chunk_by_title(elements)
    return chunks
