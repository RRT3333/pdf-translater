"""Translation service orchestration layer"""

import os
import click
from pathlib import Path
from typing import Dict, Optional, Tuple

from .client import TranslationClient
from .utils import save_translated_document, format_file_size
from .usage import UsageTracker
from .validators import validate_file_path, check_file_size
from .config import MAX_FILE_SIZE_MB


class TranslationService:
    """High-level translation service that orchestrates the translation process"""
    
    def __init__(self, client: TranslationClient, tracker: Optional[UsageTracker] = None):
        """
        Initialize translation service
        
        Args:
            client: Translation API client
            tracker: Usage tracker (optional)
        """
        self.client = client
        self.tracker = tracker or UsageTracker()
    
    def translate_file(
        self,
        input_path: str,
        output_path: str,
        source_lang: str,
        target_lang: str,
        show_relative_path: Optional[str] = None
    ) -> Tuple[bool, int, int]:
        """
        Translate a single PDF file
        
        Args:
            input_path: Path to input file
            output_path: Path to output file
            source_lang: Source language code
            target_lang: Target language code
            show_relative_path: Relative path to display (optional)
            
        Returns:
            Tuple of (success, file_count, file_size)
        """
        try:
            # Validate file
            validate_file_path(input_path)
            
            # Display file info
            filename = os.path.basename(input_path)
            display_path = show_relative_path if show_relative_path else filename
            click.echo(f"\n📄 {display_path}")
            
            # Check file size
            file_size, exceeds_limit = check_file_size(input_path)
            click.echo(f"   📊 File size: {format_file_size(file_size)}")
            
            if exceeds_limit:
                click.echo(
                    f"   ⚠️  Warning: File exceeds {MAX_FILE_SIZE_MB}MB. "
                    f"Processing may take longer.",
                    err=True
                )
            
            # Translate document
            click.echo("   🌐 Translating document...", nl=False)
            
            result = self.client.translate_document(
                file_path=input_path,
                target_language=target_lang,
                source_language=source_lang,
                mime_type="application/pdf"
            )
            
            click.echo(" ✓")
            
            # Save translated document
            click.echo("   💾 Saving file...", nl=False)
            save_translated_document(result["document_content"], output_path)
            
            output_size = format_file_size(os.path.getsize(output_path))
            click.echo(f" ✓ ({output_size})")
            click.echo(f"   → {output_path}")
            
            # Track usage
            estimated_cost = self.tracker.calculate_cost(file_size)
            click.echo(f"   💰 Estimated cost: ${estimated_cost:.2f}")
            
            self.tracker.add_translation(
                input_file=input_path,
                output_file=output_path,
                source_lang=source_lang,
                target_lang=target_lang,
                file_size_bytes=file_size
            )
            
            return True, 1, file_size
            
        except Exception as e:
            click.echo(f"\n❌ Error: {str(e)}", err=True)
            return False, 0, 0
    
    def get_output_path(
        self,
        input_path: str,
        output_dir: str,
        target_lang: str,
        preserve_structure: bool = False,
        input_base_dir: Optional[str] = None
    ) -> str:
        """
        Generate output file path
        
        Args:
            input_path: Input file path
            output_dir: Output directory
            target_lang: Target language code
            preserve_structure: Whether to preserve folder structure
            input_base_dir: Base directory for relative path calculation
            
        Returns:
            Output file path
        """
        if preserve_structure and input_base_dir:
            # Preserve folder structure
            rel_path = os.path.relpath(input_path, input_base_dir)
            rel_dir = os.path.dirname(rel_path)
            filename = os.path.basename(rel_path)
            
            # Add language code to filename
            name_without_ext = os.path.splitext(filename)[0]
            new_filename = f"{name_without_ext}_{target_lang}.pdf"
            
            # Create output path with structure
            output_path = os.path.join(output_dir, rel_dir, new_filename)
        else:
            # Save directly to output directory
            filename = os.path.basename(input_path)
            name_without_ext = os.path.splitext(filename)[0]
            new_filename = f"{name_without_ext}_{target_lang}.pdf"
            output_path = os.path.join(output_dir, new_filename)
        
        return output_path
