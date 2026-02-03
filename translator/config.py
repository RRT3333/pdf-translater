"""Configuration constants and settings"""

from typing import Dict


# API Configuration
DEFAULT_LOCATION = "us-central1"
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Cost Estimation
COST_PER_PAGE_FIRST_500 = 0.075  # USD per page (first 500 pages/month)
COST_PER_PAGE_OVER_500 = 0.045   # USD per page (over 500 pages)
AVERAGE_COST_PER_PAGE = 0.06     # Simplified average for estimation
PAGES_PER_MB = 10                 # Rough estimate: 1MB ≈ 10 pages

# Language Names Mapping
LANGUAGE_NAMES: Dict[str, str] = {
    'ja': '日本語',
    'ko': '한국어',
    'en': 'English',
    'zh': '中文',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'it': 'Italiano',
    'pt': 'Português',
    'ru': 'Русский',
    'ar': 'العربية',
    'hi': 'हिन्दी',
}

# Default Settings
DEFAULT_SOURCE_LANG = 'ja'
DEFAULT_TARGET_LANG = 'ko'
DEFAULT_OUTPUT_DIR = './output'

# File Settings
USAGE_HISTORY_FILE = "usage_history.json"
SUPPORTED_MIME_TYPES = {
    '.pdf': 'application/pdf',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
}
