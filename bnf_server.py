#!/usr/bin/env python
"""
Gallica BnF API MCP Server
--------------------------
This server provides tools to search and retrieve information from the Gallica digital library
of the Bibliothèque nationale de France (BnF) using their SRU API.
It includes endpoints to search for documents by various criteria and retrieve detailed metadata.
"""

import argparse
import os
import sys
import logging
from typing import List, Dict, Any, Optional, Union

from mcp.server.fastmcp import FastMCP
from bnf_api import GallicaAPI, SearchAPI
from bnf_api.config import DEFAULT_MAX_RECORDS, DEFAULT_START_RECORD
from bnf_api.sequential_reporting import SequentialReportingServer, BNF_SEQUENTIAL_REPORTING_TOOL

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Namespace containing parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Gallica BnF API MCP Server")
    return parser.parse_args()


# Initialize MCP server
mcp = FastMCP("gallica-bnf-api")

# Global variables to hold the API clients
gallica_api: Optional[GallicaAPI] = None
search_api: Optional[SearchAPI] = None
sequential_reporting_server: Optional[SequentialReportingServer] = None


# ------------------ MCP TOOL ENDPOINTS ------------------ #

@mcp.tool()
def search_by_title(
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
    return search_api.search_by_title(title, exact_match, max_results, start_record)


@mcp.tool()
def search_by_author(
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
    return search_api.search_by_author(author, exact_match, max_results, start_record)


@mcp.tool()
def search_by_subject(
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
    return search_api.search_by_subject(subject, exact_match, max_results, start_record)


@mcp.tool()
def search_by_date(
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
    return search_api.search_by_date(date, max_results, start_record)


@mcp.tool()
def search_by_document_type(
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
    return search_api.search_by_document_type(doc_type, max_results, start_record)


@mcp.tool()
def advanced_search(
    query: str,
    max_results: int = DEFAULT_MAX_RECORDS,
    start_record: int = DEFAULT_START_RECORD
) -> Dict[str, Any]:
    """
    Perform an advanced search using custom CQL query syntax.
    
    This tool allows for complex queries using the CQL (Contextual Query Language) syntax.
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
    return search_api.advanced_search(query, max_results, start_record)


@mcp.tool()
def natural_language_search(
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
    return search_api.natural_language_search(query, max_results, start_record)


@mcp.tool()
def sequential_reporting(
    topic: Optional[str] = None,
    page_count: Optional[int] = None,
    source_count: Optional[int] = None,
    search_sources: Optional[bool] = None,
    section_number: Optional[int] = None,
    total_sections: Optional[int] = None,
    title: Optional[str] = None,
    content: Optional[str] = None,
    is_bibliography: Optional[bool] = None,
    sources_used: Optional[List[int]] = None,
    next_section_needed: Optional[bool] = None,
    include_graphics: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Generate a research report in a sequential, step-by-step manner using Gallica BnF sources.
    
    This tool follows a sequential approach to report generation:
    1. Initialize with a topic
    2. Search for sources
    3. Create bibliography
    4. Create content sections in order
    
    Parameters:
    - topic: Research topic (only needed for initialization)
    - page_count: Number of pages for the report (default: 4)
    - source_count: Number of sources to find (default: 10)
    - search_sources: Set to True to search for sources after initialization
    - section_number: Current section number (1-based)
    - total_sections: Total number of sections in the report
    - title: Title of the current section
    - content: Content for the current section
    - is_bibliography: Whether this section is the bibliography
    - sources_used: List of source IDs used in this section
    - next_section_needed: Whether another section is needed
    - include_graphics: Whether to include images and maps in the report
    
    Returns:
    - Report section data
    """
    # Initialize the API clients if needed
    if not hasattr(sequential_reporting, 'reporting_server'):
        gallica_api = GallicaAPI()
        search_api = SearchAPI(gallica_api)
        sequential_reporting.reporting_server = SequentialReportingServer(gallica_api, search_api)
    
    # Prepare input data
    input_data = {}
    
    # Handle initialization with topic
    if topic:
        input_data['topic'] = topic
        if page_count:
            input_data['page_count'] = page_count
        if source_count:
            input_data['source_count'] = source_count
        if include_graphics is not None:
            input_data['include_graphics'] = include_graphics
    
    # Handle search for sources
    if search_sources:
        input_data['search_sources'] = search_sources
    
    # Handle section data
    if section_number:
        input_data['section_number'] = section_number
        input_data['total_sections'] = total_sections
        input_data['title'] = title
        input_data['content'] = content
        input_data['is_bibliography'] = is_bibliography
        input_data['sources_used'] = sources_used
        input_data['next_section_needed'] = next_section_needed
    
    # Process the section
    return sequential_reporting.reporting_server.process_section(input_data)


# ------------------ MAIN EXECUTION ------------------ #

def main():
    """
    Main entry point for the Gallica BnF API MCP Server.
    Initializes the API client and starts the MCP server.
    """
    parse_arguments()
    
    # Initialize the API clients
    global gallica_api, search_api, sequential_reporting_server
    gallica_api = GallicaAPI()
    search_api = SearchAPI(gallica_api)
    sequential_reporting_server = SequentialReportingServer(gallica_api, search_api)
    
    # Start the MCP server
    logger.info("Starting Gallica BnF API MCP Server")
    mcp.run()


if __name__ == "__main__":
    main()
