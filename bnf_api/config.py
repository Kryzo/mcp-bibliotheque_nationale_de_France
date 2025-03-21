"""
Configuration constants for the Gallica BnF API.
"""

# Default API parameters
DEFAULT_MAX_RECORDS = 10
DEFAULT_START_RECORD = 1

# API URL
BNF_SRU_URL = "https://gallica.bnf.fr/SRU"

# Common document types in Gallica
DOCUMENT_TYPES = {
    "monographie": "Books/Monographs",
    "periodique": "Periodicals/Newspapers",
    "image": "Images",
    "manuscrit": "Manuscripts",
    "carte": "Maps",
    "musique": "Music scores",
    "objet": "Objects",
    "video": "Videos",
    "son": "Audio recordings"
}
