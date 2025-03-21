"""
Gallica BnF API Client
---------------------
Client for the Gallica BnF SRU API.
Provides methods to search for documents and retrieve metadata.
"""

import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any, List, Optional

# Set up logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_MAX_RECORDS = 10
DEFAULT_START_RECORD = 1
BNF_SRU_URL = "https://gallica.bnf.fr/SRU"


class GallicaAPI:
    """
    Client for the Gallica BnF SRU API.
    Provides methods to search for documents and retrieve metadata.
    """
    
    def __init__(self):
        """Initialize the Gallica API client."""
        self.base_url = BNF_SRU_URL
        logger.info("Gallica API client initialized")
    
    def search(self, 
               query: str, 
               start_record: int = DEFAULT_START_RECORD,
               max_records: int = DEFAULT_MAX_RECORDS) -> Dict[str, Any]:
        """
        Search for documents in the Gallica digital library.
        
        Args:
            query: Search query in CQL format
            start_record: Starting record number for pagination
            max_records: Maximum number of records to return
            
        Returns:
            Dictionary containing search results and metadata
        """
        params = {
            'version': '1.2',
            'operation': 'searchRetrieve',
            'query': query,
            'startRecord': start_record,
            'maximumRecords': max_records
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            # Parse the XML response
            root = ET.fromstring(response.text)
            
            # Define namespaces used in the XML
            namespaces = {
                'srw': 'http://www.loc.gov/zing/srw/',
                'dc': 'http://purl.org/dc/elements/1.1/',
                'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/'
            }
            
            # Get the number of records found
            num_records = root.find('.//srw:numberOfRecords', namespaces).text
            
            # Create a dictionary to store the results
            results = {
                "metadata": {
                    "query": query,
                    "total_records": num_records,
                    "records_returned": len(root.findall('.//srw:record', namespaces)),
                    "date_retrieved": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "records": []
            }
            
            # Process each record
            for record in root.findall('.//srw:record', namespaces):
                # Get the record data element that contains Dublin Core metadata
                record_data = record.find('.//srw:recordData/oai_dc:dc', namespaces)
                
                if record_data is not None:
                    # Create a dictionary for this record
                    record_dict = {}
                    
                    # Define the Dublin Core fields we want to extract
                    dc_fields = [
                        'title', 'creator', 'contributor', 'publisher', 'date',
                        'description', 'type', 'format', 'identifier', 'source',
                        'language', 'relation', 'coverage', 'rights', 'subject'
                    ]
                    
                    # Extract each field
                    for field in dc_fields:
                        elements = record_data.findall(f'./dc:{field}', namespaces)
                        if elements:
                            # If there are multiple values, store them as a list
                            if len(elements) > 1:
                                record_dict[field] = [elem.text.strip() for elem in elements if elem.text and elem.text.strip()]
                            # If there's only one value, store it as a string
                            else:
                                text = elements[0].text
                                if text and text.strip():
                                    record_dict[field] = text.strip()
                    
                    # Extract Gallica URL from identifiers
                    if 'identifier' in record_dict:
                        identifiers = record_dict['identifier']
                        if isinstance(identifiers, list):
                            for identifier in identifiers:
                                if 'gallica.bnf.fr/ark:' in identifier:
                                    record_dict['gallica_url'] = identifier
                                    break
                        elif 'gallica.bnf.fr/ark:' in identifiers:
                            record_dict['gallica_url'] = identifiers
                    
                    # Add the record to our results
                    results['records'].append(record_dict)
            
            return results
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error during Gallica API request: {e}")
            return {
                "error": str(e),
                "query": query,
                "parameters": params
            }
        except ET.ParseError as e:
            logger.error(f"Error parsing XML response: {e}")
            return {
                "error": f"XML parsing error: {str(e)}",
                "query": query
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "error": str(e),
                "query": query
            }
