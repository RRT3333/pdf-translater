"""PDF Translator - Google Cloud Translation API를 사용한 PDF 번역기"""

__version__ = "1.0.0"

from .client import TranslationClient
from .utils import extract_text_from_pdf, create_translated_pdf

__all__ = ["TranslationClient", "extract_text_from_pdf", "create_translated_pdf"]
