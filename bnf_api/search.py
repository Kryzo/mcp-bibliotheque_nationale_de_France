"""
Search utilities for the Gallica BnF API.
Provides functions to build different types of search queries.
"""

from typing import Dict, Any, List, Optional
from .api import GallicaAPI
from .config import DEFAULT_MAX_RECORDS, DEFAULT_START_RECORD


class SearchAPI:
    """
    Search utilities for the Gallica BnF API.
    """
    
    def __init__(self, gallica_api: GallicaAPI):
        """
        Initialize the Search API.
        
        Args:
            gallica_api: An initialized GallicaAPI instance
        """
        self.gallica_api = gallica_api
    
    def search_by_title(
        self,
        title: str,
        exact_match: bool = False,
        max_results: int = DEFAULT_MAX_RECORDS,
        start_record: int = DEFAULT_START_RECORD
    ) -> Dict[str, Any]:
        """
        Search for documents in the Gallica digital library by title.
        
        Args:
            title: The title to search for
            exact_match: If True, search for the exact title; otherwise, search for title containing the words
            max_results: Maximum number of results to return (1-50)
            start_record: Starting record for pagination
            
        Returns:
            Dictionary containing search results and metadata
        """
        if exact_match:
            query = f'dc.title all "{title}"'
        else:
            query = f'dc.title all {title}'
        
        return self.gallica_api.search(query, start_record, max_results)
    
    def search_by_author(
        self,
        author: str,
        exact_match: bool = False,
        max_results: int = DEFAULT_MAX_RECORDS,
        start_record: int = DEFAULT_START_RECORD
    ) -> Dict[str, Any]:
        """
        Search for documents in the Gallica digital library by author.
        
        Args:
            author: The author name to search for
            exact_match: If True, search for the exact author name; otherwise, search for author containing the words
            max_results: Maximum number of results to return (1-50)
            start_record: Starting record for pagination
            
        Returns:
            Dictionary containing search results and metadata
        """
        if exact_match:
            query = f'dc.creator all "{author}"'
        else:
            query = f'dc.creator all {author}'
        
        return self.gallica_api.search(query, start_record, max_results)
    
    def search_by_subject(
        self,
        subject: str,
        exact_match: bool = False,
        max_results: int = DEFAULT_MAX_RECORDS,
        start_record: int = DEFAULT_START_RECORD
    ) -> Dict[str, Any]:
        """
        Search for documents in the Gallica digital library by subject.
        
        Args:
            subject: The subject to search for
            exact_match: If True, search for the exact subject; otherwise, search for subject containing the words
            max_results: Maximum number of results to return (1-50)
            start_record: Starting record for pagination
            
        Returns:
            Dictionary containing search results and metadata
        """
        if exact_match:
            query = f'dc.subject all "{subject}"'
        else:
            query = f'dc.subject all {subject}'
        
        return self.gallica_api.search(query, start_record, max_results)
    
    def search_by_date(
        self,
        date: str,
        max_results: int = DEFAULT_MAX_RECORDS,
        start_record: int = DEFAULT_START_RECORD
    ) -> Dict[str, Any]:
        """
        Search for documents in the Gallica digital library by date.
        
        Args:
            date: The date to search for (format: YYYY or YYYY-MM or YYYY-MM-DD)
            max_results: Maximum number of results to return (1-50)
            start_record: Starting record for pagination
            
        Returns:
            Dictionary containing search results and metadata
        """
        query = f'dc.date all "{date}"'
        
        return self.gallica_api.search(query, start_record, max_results)
    
    def search_by_document_type(
        self,
        doc_type: str,
        max_results: int = DEFAULT_MAX_RECORDS,
        start_record: int = DEFAULT_START_RECORD
    ) -> Dict[str, Any]:
        """
        Search for documents in the Gallica digital library by document type.
        
        Args:
            doc_type: The document type to search for (e.g., monographie, periodique, image, manuscrit, carte, musique, etc.)
            max_results: Maximum number of results to return (1-50)
            start_record: Starting record for pagination
            
        Returns:
            Dictionary containing search results and metadata
        """
        query = f'dc.type all "{doc_type}"'
        
        return self.gallica_api.search(query, start_record, max_results)
    
    def advanced_search(
        self,
        query: str,
        max_results: int = DEFAULT_MAX_RECORDS,
        start_record: int = DEFAULT_START_RECORD
    ) -> Dict[str, Any]:
        """
        Perform an advanced search using custom CQL query syntax.
        
        This method allows for complex queries using the CQL (Contextual Query Language) syntax.
        Examples:
        - Search for books by Victor Hugo: dc.creator all "Victor Hugo" and dc.type all "monographie"
        - Search for maps about Paris: dc.subject all "Paris" and dc.type all "carte"
        - Search for documents in English: dc.language all "eng"
        
        Args:
            query: Custom CQL query string
            max_results: Maximum number of results to return (1-50)
            start_record: Starting record for pagination
            
        Returns:
            Dictionary containing search results and metadata
        """
        return self.gallica_api.search(query, start_record, max_results)
    
    def natural_language_search(
        self,
        query: str,
        max_results: int = DEFAULT_MAX_RECORDS,
        start_record: int = DEFAULT_START_RECORD
    ) -> Dict[str, Any]:
        """
        Search the Gallica digital library using natural language.
        
        This is a simplified search that uses the 'gallica all' operator to search across all fields.
        It's the most user-friendly way to search but may not be as precise as the other search methods.
        
        Args:
            query: Natural language search query
            max_results: Maximum number of results to return (1-50)
            start_record: Starting record for pagination
            
        Returns:
            Dictionary containing search results and metadata
        """
        # Format the query for the Gallica API
        formatted_query = f'gallica all "{query}"'
        
        return self.gallica_api.search(formatted_query, start_record, max_results)
