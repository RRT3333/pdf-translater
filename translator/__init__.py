"""PDF Translator - Google Cloud Translation API v3 Document Translation"""

__version__ = "2.0.0"

from .client import TranslationClient
from .utils import save_translated_document, get_pdf_files, format_file_size
from .usage import UsageTracker
from .service import TranslationService
from .validators import validate_credentials
from .config import (
    LANGUAGE_NAMES,
    DEFAULT_SOURCE_LANG,
    DEFAULT_TARGET_LANG,
    DEFAULT_OUTPUT_DIR,
)

__all__ = [
    "TranslationClient",
    "TranslationService",
    "UsageTracker",
    "save_translated_document",
    "get_pdf_files",
    "format_file_size",
    "validate_credentials",
    "LANGUAGE_NAMES",
    "DEFAULT_SOURCE_LANG",
    "DEFAULT_TARGET_LANG",
    "DEFAULT_OUTPUT_DIR",
]
