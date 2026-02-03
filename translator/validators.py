"""Validation functions for inputs and credentials"""

import os
import sys
import click
from pathlib import Path
from typing import Optional, Tuple

from .config import MAX_FILE_SIZE_BYTES, SUPPORTED_MIME_TYPES


def validate_credentials() -> Tuple[str, str]:
    """
    Validate Google Cloud credentials and return project info
    
    Returns:
        Tuple of (credentials_path, project_id)
        
    Raises:
        SystemExit if validation fails
    """
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if not credentials_path:
        click.echo("❌ Error: GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.", err=True)
        click.echo("💡 Add the following to your .env file:", err=True)
        click.echo("   GOOGLE_APPLICATION_CREDENTIALS=./credentials.json", err=True)
        sys.exit(1)
    
    if not os.path.exists(credentials_path):
        click.echo(f"❌ Error: Credential file not found: {credentials_path}", err=True)
        click.echo("💡 Download the service account key from Google Cloud Console.", err=True)
        sys.exit(1)
    
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        click.echo("❌ Error: GOOGLE_CLOUD_PROJECT environment variable is not set.", err=True)
        click.echo("💡 Add the following to your .env file:", err=True)
        click.echo("   GOOGLE_CLOUD_PROJECT=your-project-id", err=True)
        sys.exit(1)
    
    return credentials_path, project_id


def validate_file_path(file_path: str) -> None:
    """
    Validate that file exists and is a supported type
    
    Args:
        file_path: Path to file to validate
        
    Raises:
        click.ClickException if validation fails
    """
    if not os.path.exists(file_path):
        raise click.ClickException(f"File not found: {file_path}")
    
    ext = Path(file_path).suffix.lower()
    if ext not in SUPPORTED_MIME_TYPES:
        supported = ', '.join(SUPPORTED_MIME_TYPES.keys())
        raise click.ClickException(f"Unsupported file type: {ext}. Supported types: {supported}")


def check_file_size(file_path: str) -> Tuple[int, bool]:
    """
    Check file size and return size info
    
    Args:
        file_path: Path to file to check
        
    Returns:
        Tuple of (file_size_bytes, exceeds_limit)
    """
    file_size = os.path.getsize(file_path)
    exceeds_limit = file_size > MAX_FILE_SIZE_BYTES
    
    return file_size, exceeds_limit


def validate_language_code(lang_code: str, allow_empty: bool = False) -> bool:
    """
    Validate language code format
    
    Args:
        lang_code: Language code to validate
        allow_empty: Whether to allow empty string (for auto-detection)
        
    Returns:
        True if valid, False otherwise
    """
    if allow_empty and lang_code == "":
        return True
    
    # Basic validation: 2-3 lowercase letters
    return bool(lang_code and len(lang_code) in (2, 3) and lang_code.islower())


def validate_month(month: int) -> None:
    """
    Validate month value
    
    Args:
        month: Month number (1-12)
        
    Raises:
        click.ClickException if invalid
    """
    if not (1 <= month <= 12):
        raise click.ClickException("Month must be between 1 and 12.")
