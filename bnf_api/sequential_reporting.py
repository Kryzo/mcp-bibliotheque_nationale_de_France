"""
BnF Sequential Reporting Tool
----------------------------
This module provides a tool for generating structured reports based on research
from the Gallica BnF digital library. It uses a sequential approach to gather sources,
analyze them, and generate a comprehensive report with proper citations.
"""

import json
import sys
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import textwrap

from .api import GallicaAPI
from .search import SearchAPI

# Set up logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_PAGE_COUNT = 4
DEFAULT_SOURCE_COUNT = 10


@dataclass
class ReportSection:
    """
    Represents a section of the sequential report.
    """
    section_number: int
    total_sections: int
    content: str
    title: str
    is_bibliography: bool = False
    sources_used: List[int] = None
    next_section_needed: bool = True


class SequentialReportingServer:
    """
    Server for generating sequential reports based on BnF research.
    """
    
    def __init__(self, gallica_api: GallicaAPI, search_api: SearchAPI):
        """
        Initialize the Sequential Reporting Server.
        
        Args:
            gallica_api: An initialized GallicaAPI instance
            search_api: An initialized SearchAPI instance
        """
        self.gallica_api = gallica_api
        self.search_api = search_api
        self.topic = None
        self.page_count = DEFAULT_PAGE_COUNT
        self.source_count = DEFAULT_SOURCE_COUNT
        self.sources = []
        self.report_sections = []
        self.plan = None
        self._current_step = 0
        self.include_graphics = False
        self.graphics = []
        
    def validate_section_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the input data for a section.
        
        Args:
            input_data: The input data for the section
            
        Returns:
            Validated input data
        """
        validated_data = {}
        
        # Handle initialization with topic
        if 'topic' in input_data:
            validated_data['topic'] = str(input_data['topic'])
            if 'page_count' in input_data:
                try:
                    validated_data['page_count'] = int(input_data['page_count'])
                except (ValueError, TypeError):
                    validated_data['page_count'] = DEFAULT_PAGE_COUNT
            if 'source_count' in input_data:
                try:
                    validated_data['source_count'] = int(input_data['source_count'])
                except (ValueError, TypeError):
                    validated_data['source_count'] = DEFAULT_SOURCE_COUNT
            if 'include_graphics' in input_data:
                validated_data['include_graphics'] = bool(input_data['include_graphics'])
            return validated_data
            
        # Handle search_sources flag
        if 'search_sources' in input_data and input_data['search_sources']:
            validated_data['search_sources'] = True
            return validated_data
        
        # Check if required fields are present for section data
        required_fields = ['section_number', 'total_sections']
        for field in required_fields:
            if field not in input_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Convert section_number and total_sections to integers if they're strings
        section_number = input_data['section_number']
        if isinstance(section_number, str) and section_number.isdigit():
            section_number = int(section_number)
        elif not isinstance(section_number, int):
            raise ValueError(f"Invalid sectionNumber: must be a number")
            
        total_sections = input_data['total_sections']
        if isinstance(total_sections, str) and total_sections.isdigit():
            total_sections = int(total_sections)
        elif not isinstance(total_sections, int):
            raise ValueError(f"Invalid totalSections: must be a number")
        
        # Get title
        title = input_data.get('title', f"Section {section_number}")
        
        # Get content (empty string if not provided)
        content = input_data.get('content', '')
        if content is None:
            content = ''
        if not isinstance(content, str):
            raise ValueError(f"Invalid content: must be a string")
        
        # Get is_bibliography flag
        is_bibliography = input_data.get('is_bibliography', False)
        
        # Get sources_used (empty list if not provided)
        sources_used = input_data.get('sources_used', [])
        if sources_used is None:
            sources_used = []
        
        # Get next_section_needed flag
        next_section_needed = input_data.get('next_section_needed', True)
        
        # Create and return ReportSection
        return {
            'section_number': section_number,
            'total_sections': total_sections,
            'title': title,
            'content': content,
            'is_bibliography': is_bibliography,
            'sources_used': sources_used,
            'next_section_needed': next_section_needed
        }
    
    def search_sources(self, topic: str, source_count: int = DEFAULT_SOURCE_COUNT) -> List[Dict[str, Any]]:
        """
        Search for sources on the given topic.
        
        Args:
            topic: The topic to search for
            source_count: The number of sources to retrieve
            
        Returns:
            List of sources as dictionaries
        """
        try:
            # Try natural language search first
            results = self.search_api.natural_language_search(topic, max_results=source_count)
            
            # If not enough results, try subject search
            if len(results.get('records', [])) < source_count:
                subject_results = self.search_api.search_by_subject(topic, max_results=source_count - len(results.get('records', [])))
                # Combine results
                all_records = results.get('records', []) + subject_results.get('records', [])
                results['records'] = all_records
            
            # Format the results
            sources = []
            for i, result in enumerate(results.get('records', [])[:source_count], 1):
                source = {
                    'id': i,
                    'title': result.get('title', 'Unknown Title'),
                    'creator': result.get('creator', 'Unknown Author'),
                    'date': result.get('date', 'Unknown Date'),
                    'type': result.get('type', 'Unknown Type'),
                    'language': result.get('language', 'Unknown Language'),
                    'url': result.get('url', ''),
                    'citation': self._format_citation(result),
                    'thumbnail': result.get('thumbnail', '')
                }
                sources.append(source)
            
            return sources
        except Exception as e:
            print(f"Error searching for sources: {e}")
            return []
    
    def search_graphics(self, topic: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Search for graphics (images, maps) related to the topic.
        
        Args:
            topic: The topic to search for
            count: The number of graphics to retrieve
            
        Returns:
            List of graphics as dictionaries
        """
        try:
            # Break down the topic into keywords for better search results
            keywords = topic.split()
            main_keyword = keywords[0] if keywords else topic
            
            # Search for images with broader terms
            image_query = f'gallica all "{main_keyword}" and dc.type all "image"'
            image_results = self.search_api.advanced_search(image_query, max_results=count)
            
            # If no results, try with the full topic
            if not image_results.get('records', []):
                image_query = f'gallica all "{topic}" and dc.type all "image"'
                image_results = self.search_api.advanced_search(image_query, max_results=count)
            
            # Search for maps with broader terms
            map_query = f'gallica all "{main_keyword}" and dc.type all "carte"'
            map_results = self.search_api.advanced_search(map_query, max_results=count)
            
            # If no results, try with the full topic
            if not map_results.get('records', []):
                map_query = f'gallica all "{topic}" and dc.type all "carte"'
                map_results = self.search_api.advanced_search(map_query, max_results=count)
            
            # If still no results, try a more general search for any visual material
            if not image_results.get('records', []) and not map_results.get('records', []):
                general_query = f'gallica all "{main_keyword}" and (dc.type all "image" or dc.type all "carte" or dc.type all "estampe")'
                general_results = self.search_api.advanced_search(general_query, max_results=count)
                image_results = general_results
            
            # Combine and format results
            graphics = []
            
            # Process image results
            for i, result in enumerate(image_results.get('records', []), 1):
                # Extract URL from gallica_url if available (without /thumbnail suffix)
                url = result.get('gallica_url', '')
                thumbnail = ''
                if url:
                    # Remove /thumbnail suffix if it exists
                    url = url.replace('/thumbnail', '')
                    ark_id = url.split('ark:')[1] if 'ark:' in url else ''
                    if ark_id:
                        thumbnail = f"https://gallica.bnf.fr/ark:{ark_id}/thumbnail"
                
                graphic = {
                    'id': i,
                    'title': result.get('title', 'Untitled Image'),
                    'description': f"Image related to {topic}: {result.get('title', 'Untitled Image')}",
                    'type': 'image',
                    'url': url,
                    'thumbnail': thumbnail
                }
                graphics.append(graphic)
            
            # Process map results
            for i, result in enumerate(map_results.get('records', []), len(graphics) + 1):
                # Extract URL from gallica_url if available (without /thumbnail suffix)
                url = result.get('gallica_url', '')
                thumbnail = ''
                if url:
                    # Remove /thumbnail suffix if it exists
                    url = url.replace('/thumbnail', '')
                    ark_id = url.split('ark:')[1] if 'ark:' in url else ''
                    if ark_id:
                        thumbnail = f"https://gallica.bnf.fr/ark:{ark_id}/thumbnail"
                
                graphic = {
                    'id': i,
                    'title': result.get('title', 'Untitled Map'),
                    'description': f"Map related to {topic}: {result.get('title', 'Untitled Map')}",
                    'type': 'map',
                    'url': url,
                    'thumbnail': thumbnail
                }
                graphics.append(graphic)
            
            # If we still have no graphics, create some placeholder graphics with generic URLs
            if not graphics:
                # Create some placeholder graphics
                graphics = [
                    {
                        'id': 1,
                        'title': f"Illustration related to {topic}",
                        'description': f"Illustration related to {topic}",
                        'type': 'image',
                        'url': 'https://gallica.bnf.fr/',
                        'thumbnail': 'https://gallica.bnf.fr/themes/gallica2015/images/logo-gallica.png'
                    },
                    {
                        'id': 2,
                        'title': f"Map related to {topic}",
                        'description': f"Map related to {topic}",
                        'type': 'map',
                        'url': 'https://gallica.bnf.fr/',
                        'thumbnail': 'https://gallica.bnf.fr/themes/gallica2015/images/logo-gallica.png'
                    }
                ]
            
            return graphics[:count]
        except Exception as e:
            print(f"Error searching for graphics: {e}")
            return []

    def process_section(self, input_data: Any) -> Dict[str, Any]:
        """
        Process a report section following a sequential approach.
        
        Args:
            input_data: The input data for the section
            
        Returns:
            Response data as a dictionary
        """
        try:
            # Validate the input data
            data = self.validate_section_data(input_data)
            
            # Initialize with topic
            if 'topic' in data:
                self.topic = data['topic']
                self.page_count = data.get('page_count', DEFAULT_PAGE_COUNT)
                self.source_count = data.get('source_count', DEFAULT_SOURCE_COUNT)
                self.include_graphics = data.get('include_graphics', False)
                self.sources = []
                self.graphics = []
                self.report_sections = []
                self._current_step = 0
                
                # Create a plan for the report
                self.plan = self.create_plan(self.topic, self.page_count)
                
                return {
                    'content': [{
                        'text': json.dumps({
                            'topic': self.topic,
                            'pageCount': self.page_count,
                            'sourceCount': self.source_count,
                            'includeGraphics': self.include_graphics,
                            'plan': self.plan,
                            'nextStep': 'Search for sources using natural_language_search or search_by_subject'
                        })
                    }]
                }
            
            # Search for sources
            if data.get('search_sources', False):
                if not self.topic:
                    return {'content': [{'text': 'Error: No topic specified. Please initialize with a topic first.'}]}
                
                self.sources = self.search_sources(self.topic, self.source_count)
                
                # If graphics are requested, search for them
                if self.include_graphics:
                    self.graphics = self.search_graphics(self.topic, count=5)
                
                self._current_step = 1
                
                return {
                    'content': [{
                        'text': json.dumps({
                            'sources': self.sources,
                            'graphics': self.graphics if self.include_graphics else [],
                            'nextStep': 'Create bibliography section'
                        })
                    }]
                }
            
            # Process section data for bibliography or content sections
            validated_input = self.validate_section_data(input_data)
            
            # Adjust total sections if needed
            if validated_input['section_number'] > validated_input['total_sections']:
                validated_input['total_sections'] = validated_input['section_number']
            
            # Add section to report
            self.report_sections.append(validated_input)
            
            # Format and display section
            formatted_section = self.format_section(validated_input)
            print(formatted_section, file=sys.stderr)
            
            # Update current step in plan
            if self.plan:
                self.plan["current_section"] = validated_input['section_number']
                if validated_input['section_number'] < len(self.plan["sections"]):
                    next_section_title = self.plan["sections"][validated_input['section_number']]["title"]
                    next_step = f"Create section {validated_input['section_number'] + 1}: {next_section_title}"
                else:
                    next_step = "Report complete"
            else:
                next_step = "Continue writing the report"
                if not validated_input['next_section_needed']:
                    next_step = "Report complete"
            
            # Calculate progress
            progress = (len(self.report_sections) / validated_input['total_sections']) * 100
            
            return {
                'content': [{
                    'text': json.dumps({
                        'sectionNumber': validated_input['section_number'],
                        'totalSections': validated_input['total_sections'],
                        'nextSectionNeeded': validated_input['next_section_needed'],
                        'progress': f"{progress:.1f}%",
                        'reportSectionsCount': len(self.report_sections),
                        'nextStep': next_step,
                        'sources': self.sources if validated_input['is_bibliography'] else None
                    })
                }]
            }
        
        except Exception as error:
            logger.error(f"Error processing report section: {error}")
            return {
                'content': [{
                    'text': json.dumps({
                        'error': str(error),
                        'status': 'failed'
                    })
                }],
                'isError': True
            }

    def format_section(self, section: Dict[str, Any]) -> str:
        """
        Format a report section for display.
        
        Args:
            section: The report section to format
            
        Returns:
            Formatted section as a string
        """
        # Get section information
        section_number = section.get('section_number', 0)
        total_sections = section.get('total_sections', 0)
        title = section.get('title', 'Untitled')
        is_bibliography = section.get('is_bibliography', False)
        
        # Create a box for the section
        width = 80
        icon = "\033[93m📚\033[0m" if is_bibliography else "\033[94m📄\033[0m"  # Yellow for bibliography, blue for content
        
        header = f" {icon} Section{section_number}/{total_sections}: {title} "
        
        box = "┌" + "─" * (width - 2) + "┐\n"
        box += "│" + header + " " * (width - len(header) - 2) + "│\n"
        box += "├" + "─" * (width - 2) + "┤\n"
        
        # Add content
        content = section.get('content', '')
        if content:
            # Wrap content to fit in the box
            wrapped_content = textwrap.wrap(content, width=width-4)
            for line in wrapped_content:
                box += "│ " + line + " " * (width - len(line) - 4) + " │\n"
        
        # Add graphics if available and this is not a bibliography
        if not is_bibliography and self.include_graphics and self.graphics:
            # Find graphics relevant to this section
            section_graphics = []
            for graphic in self.graphics:
                # Simple relevance check - could be improved
                if any(term in graphic['title'].lower() for term in title.lower().split()):
                    section_graphics.append(graphic)
            
            # Add up to 2 graphics for this section
            if section_graphics:
                box += "│ " + " " * (width - 4) + " │\n"
                box += "│ " + "Graphics:" + " " * (width - 13) + " │\n"
                for graphic in section_graphics[:2]:
                    desc = f"- {graphic['description']}"
                    wrapped_desc = textwrap.wrap(desc, width=width-4)
                    for line in wrapped_desc:
                        box += "│ " + line + " " * (width - len(line) - 4) + " │\n"
                    box += "│ " + f"  URL: {graphic['url']}" + " " * (width - len(f"  URL: {graphic['url']}") - 4) + " │\n"
        
        box += "└" + "─" * (width - 2) + "┘"
        
        return box

    def create_plan(self, topic: str, page_count: int = DEFAULT_PAGE_COUNT) -> Dict[str, Any]:
        """
        Create a sequential plan for the report based on the topic.
        
        Args:
            topic: The research topic
            page_count: Number of pages to generate
            
        Returns:
            A plan dictionary with sections and steps
        """
        # Calculate number of sections based on page count (1 page ≈ 2 sections + bibliography)
        total_sections = min(page_count * 2 + 1, 20)  # Cap at 20 sections
        
        # Create standard sections
        sections = [{"title": "Bibliography", "is_bibliography": True}]
        
        # Add introduction
        sections.append({"title": "Introduction", "is_bibliography": False})
        
        # Add content sections based on page count
        if page_count >= 2:
            sections.append({"title": "Historical Context", "is_bibliography": False})
        
        if page_count >= 3:
            sections.append({"title": "Main Analysis", "is_bibliography": False})
            sections.append({"title": "Key Findings", "is_bibliography": False})
        
        if page_count >= 4:
            sections.append({"title": "Detailed Examination", "is_bibliography": False})
            sections.append({"title": "Critical Perspectives", "is_bibliography": False})
        
        # Add more sections for longer reports
        remaining_sections = total_sections - len(sections)
        for i in range(remaining_sections):
            sections.append({"title": f"Additional Analysis {i+1}", "is_bibliography": False})
        
        # Always end with conclusion
        sections.append({"title": "Conclusion", "is_bibliography": False})
        
        return {
            "topic": topic,
            "total_sections": len(sections),
            "sections": sections,
            "current_section": 0,
            "steps": [
                "Initialize with topic",
                "Search for sources",
                "Create bibliography",
                "Write introduction",
                "Develop content sections",
                "Write conclusion"
            ],
            "current_step": 0,
            "next_step": "Search for sources"
        }

    def _format_citation(self, record: Dict[str, Any]) -> str:
        """
        Format a record as a citation.
        
        Args:
            record: The record to format
            
        Returns:
            Formatted citation as a string
        """
        creator = record.get('creator', 'Unknown Author')
        title = record.get('title', 'Unknown Title')
        publisher = record.get('publisher', 'Unknown Publisher')
        date = record.get('date', 'n.d.')
        url = record.get('gallica_url', record.get('identifier', 'No URL available'))
        
        # Format based on type - ensure doc_type is a string before calling lower()
        doc_type = record.get('type', '')
        if isinstance(doc_type, list):
            # If type is a list, join it into a string
            doc_type = ' '.join(str(t) for t in doc_type)
        doc_type = doc_type.lower()
        
        if 'monographie' in doc_type or 'book' in doc_type:
            return f"{creator}. ({date}). {title}. {publisher}. Retrieved from {url}"
        elif 'periodique' in doc_type or 'article' in doc_type:
            return f"{creator}. ({date}). {title}. Retrieved from {url}"
        else:
            return f"{creator}. ({date}). {title}. {publisher}. Retrieved from {url}"


# Tool definition
BNF_SEQUENTIAL_REPORTING_TOOL = {
    "name": "bnf_sequential_reporting",
    "description": """A tool for generating comprehensive research reports using the Gallica BnF digital library.
This tool helps create well-structured, properly cited reports on any topic by breaking the process into sequential steps.

When to use this tool:
- Creating research reports on historical, literary, or cultural topics
- Generating academic papers with proper citations
- Compiling information from multiple Gallica sources into a cohesive document
- Producing educational materials based on primary and secondary sources

Key features:
- Automatically searches for relevant sources in the Gallica digital library
- Creates properly formatted citations in a bibliography
- Generates reports with a specified number of pages (default: 4)
- Supports sequential writing of report sections
- Includes in-text citations in the format [1], [2], etc.
- Maintains context across multiple sections

How it works:
1. First, provide a topic and optional configuration parameters
2. The tool searches for relevant sources in the Gallica digital library
3. Start by creating the bibliography as the first section
4. Then write each section of the report sequentially
5. Include in-text citations to reference sources from the bibliography
6. Continue until the report is complete

Parameters explained:
- topic: The research topic for the report (only needed for initialization)
- pageCount: Number of pages to generate (default: 4)
- sourceCount: Number of sources to find (default: 10)
- sectionNumber: Current section number in sequence
- totalSections: Total number of sections in the report
- title: Title of the current section
- content: The content of the current section
- isBibliography: Whether this section is the bibliography
- sourcesUsed: List of source IDs used in this section
- nextSectionNeeded: Whether another section is needed
- includeGraphics: Whether to include graphics in the report (default: False)

You should:
1. Start by providing a topic to initialize the research
2. Create the bibliography first as section 1
3. Write each section sequentially, including in-text citations [1], [2], etc.
4. Ensure each section builds on previous ones to create a cohesive report
5. Include a conclusion in the final section
6. Set nextSectionNeeded to false when the report is complete""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "Research topic for the report (only needed for initialization)"
            },
            "pageCount": {
                "type": "integer",
                "description": "Number of pages to generate",
                "minimum": 1,
                "default": 4
            },
            "sourceCount": {
                "type": "integer",
                "description": "Number of sources to find",
                "minimum": 1,
                "default": 10
            },
            "sectionNumber": {
                "type": "integer",
                "description": "Current section number",
                "minimum": 1
            },
            "totalSections": {
                "type": "integer",
                "description": "Total sections in the report",
                "minimum": 1
            },
            "title": {
                "type": "string",
                "description": "Title of the current section"
            },
            "content": {
                "type": "string",
                "description": "Content of the current section"
            },
            "isBibliography": {
                "type": "boolean",
                "description": "Whether this section is the bibliography"
            },
            "sourcesUsed": {
                "type": "array",
                "items": {
                    "type": "integer"
                },
                "description": "List of source IDs used in this section"
            },
            "nextSectionNeeded": {
                "type": "boolean",
                "description": "Whether another section is needed"
            },
            "includeGraphics": {
                "type": "boolean",
                "description": "Whether to include graphics in the report",
                "default": False
            }
        },
        "required": ["sectionNumber", "totalSections", "title", "content", "nextSectionNeeded"]
    }
}
