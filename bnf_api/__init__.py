"""
Gallica BnF API Package
----------------------
This package provides tools to search and retrieve information from the Gallica digital library
of the Bibliothèque nationale de France (BnF) using their SRU API.
"""

from .api import GallicaAPI
from .search import SearchAPI
from .config import DEFAULT_MAX_RECORDS, DEFAULT_START_RECORD, BNF_SRU_URL, DOCUMENT_TYPES

__all__ = [
    'GallicaAPI',
    'SearchAPI',
    'DEFAULT_MAX_RECORDS',
    'DEFAULT_START_RECORD',
    'BNF_SRU_URL',
    'DOCUMENT_TYPES'
]
