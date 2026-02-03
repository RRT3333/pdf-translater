#!/usr/bin/env python3
"""PDF Translation CLI Program - Google Cloud Translation API v3 Document Translation"""

import os
import sys
import click
from dotenv import load_dotenv
from pathlib import Path
from typing import List
from datetime import datetime

from translator import TranslationClient, save_translated_document, UsageTracker
from translator.utils import get_pdf_files, get_pdf_files_recursive, get_output_path_with_structure, format_file_size

# Load .env file
load_dotenv()


def validate_credentials():
    """Validate Google Cloud credentials"""
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


def translate_single_file(
    input_path: str,
    output_path: str,
    source_lang: str,
    target_lang: str,
    client: TranslationClient,
    tracker: UsageTracker = None,
    show_relative_path: str = None
):
    """Translate a single PDF file (using Document Translation)"""
    try:
        filename = os.path.basename(input_path)
        display_path = show_relative_path if show_relative_path else filename
        click.echo(f"\n📄 {display_path}")
        
        file_size = os.path.getsize(input_path)
        click.echo(f"   📊 File size: {format_file_size(file_size)}")
        
        # Check file size limit (10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            click.echo(f"   ⚠️  Warning: File exceeds 10MB. Processing may take longer.", err=True)
        
        # Translate PDF document (API v3 Document Translation)
        click.echo("   🌐 Translating document...", nl=False)
        
        result = client.translate_document(
            file_path=input_path,
            target_language=target_lang,
            source_language=source_lang,
            mime_type="application/pdf"
        )
        
        click.echo(" ✓")
        
        # Save translated PDF
        click.echo("   💾 Saving file...", nl=False)
        save_translated_document(result["document_content"], output_path)
        
        output_size = format_file_size(os.path.getsize(output_path))
        click.echo(f" ✓ ({output_size})")
        click.echo(f"   → {output_path}")
        
        # Track usage
        if tracker:
            estimated_cost = tracker.calculate_cost(file_size)
            click.echo(f"   💰 Estimated cost: ${estimated_cost:.2f}")
            tracker.add_translation(
                input_file=input_path,
                output_file=output_path,
                source_lang=source_lang,
                target_lang=target_lang,
                file_size_bytes=file_size
            )
        
        return True, 1, file_size  # success, 1 file, file size
        
    except Exception as e:
        click.echo(f"\n❌ Error: {str(e)}", err=True)
        return False, 0, 0


@click.group(invoke_without_command=True)
@click.pass_context
@click.option(
    '--input', '-i',
    type=click.Path(exists=True),
    help='Input PDF file or folder path'
)
@click.option(
    '--output', '-o',
    default='./output',
    type=click.Path(),
    help='Output folder path (default: ./output)'
)
@click.option(
    '--source', '-s',
    default='ja',
    help='Source language code (default: ja, empty string for auto-detection)'
)
@click.option(
    '--target', '-t',
    default='ko',
    help='Target language code (default: ko)'
)
@click.option(
    '--batch', '-b',
    is_flag=True,
    help='Batch processing mode for folders'
)
@click.option(
    '--recursive', '-r',
    is_flag=True,
    help='Recursive processing including subfolders (preserves folder structure)'
)
def cli(ctx, input, output, source, target, batch, recursive):
    """PDF Translation CLI Program (Google Cloud Translation API v3 Document Translation)
    
    Translates entire PDF documents while preserving layout and format, without text extraction.
    
    Examples:
    
        # Translate a single file
        python translate.py -i ./document.pdf -o ./output/
        
        # Batch translate folder
        python translate.py -i ./docs/ -o ./output/ --batch
        
        # Recursive translation including subfolders (preserves folder structure)
        python translate.py -i ./docs/ -o ./output/ --recursive
        
        # Specify languages
        python translate.py -i ./docs/ -s en -t ko --batch
        
        # Auto language detection (empty string for source)
        python translate.py -i ./document.pdf -s "" -t ko
        
        # View usage statistics
        python translate.py stats
        
        # View detailed usage statistics
        python translate.py stats --detail
    """
    if ctx.invoked_subcommand is None:
        if not input:
            click.echo("❌ Error: --input option is required.", err=True)
            click.echo("Usage: python translate.py --help", err=True)
            sys.exit(1)
        
        ctx.invoke(translate_command, input=input, output=output, source=source, target=target, batch=batch, recursive=recursive)


@cli.command(name='translate', hidden=True)
@click.option('--input', '-i', required=True, type=click.Path(exists=True))
@click.option('--output', '-o', default='./output', type=click.Path())
@click.option('--source', '-s', default='ja')
@click.option('--target', '-t', default='ko')
@click.option('--batch', '-b', is_flag=True)
@click.option('--recursive', '-r', is_flag=True)
def translate_command(input: str, output: str, source: str, target: str, batch: bool, recursive: bool):
    """PDF Translation CLI Program (Google Cloud Translation API v3 Document Translation)
    
    Translates entire PDF documents while preserving layout and format, without text extraction.
    
    Examples:
    
        # Translate a single file
        python translate.py -i ./document.pdf -o ./output/
        
        # Batch translate folder
        python translate.py -i ./docs/ -o ./output/ --batch
        
        # Specify languages
        python translate.py -i ./docs/ -s en -t ko --batch
        
        # Auto language detection (empty string for source)
        python translate.py -i ./document.pdf -s "" -t ko
    """
    # Validate credentials
    validate_credentials()
    
    # Create output directory
    os.makedirs(output, exist_ok=True)
    
    # Initialize Translation client
    try:
        client = TranslationClient()
    except Exception as e:
        click.echo(f"❌ Error: Failed to initialize Translation API client: {str(e)}", err=True)
        sys.exit(1)
    
    # Get input file list
    if recursive:
        # Recursive mode: includes subfolders, preserves folder structure
        if not os.path.isdir(input):
            click.echo("❌ Error: --recursive option must be used with a folder path.", err=True)
            sys.exit(1)
        
        pdf_files_with_rel = get_pdf_files_recursive(input)
        if not pdf_files_with_rel:
            click.echo(f"❌ Error: No PDF files found in {input} folder.", err=True)
            sys.exit(1)
        
        pdf_files = [abs_path for abs_path, rel_path in pdf_files_with_rel]
        is_recursive_mode = True
        input_base_dir = input
        
    elif batch or os.path.isdir(input):
        # Batch mode: current folder only
        if not os.path.isdir(input):
            click.echo("❌ Error: --batch option must be used with a folder path.", err=True)
            sys.exit(1)
        pdf_files = get_pdf_files(input)
        if not pdf_files:
            click.echo(f"❌ Error: No PDF files found in {input} folder.", err=True)
            sys.exit(1)
        is_recursive_mode = False
        input_base_dir = None
        
    else:
        # Single file mode
        if not input.lower().endswith('.pdf'):
            click.echo("❌ Error: Only PDF files are supported.", err=True)
            sys.exit(1)
        pdf_files = [input]
        is_recursive_mode = False
        input_base_dir = None
    
    # Language name mapping
    lang_names = {
        'ja': '日本語',
        'ko': '한국어',
        'en': 'English',
        'zh': '中文',
        'es': 'Español',
        'fr': 'Français',
        'de': 'Deutsch'
    }
    
    source_name = lang_names.get(source, source.upper())
    target_name = lang_names.get(target, target.upper())
    
    # Start message
    click.echo("\n" + "="*60)
    click.echo("🌏 PDF Translator (Document Translation API)")
    click.echo("="*60)
    click.echo(f"📁 Input: {input} ({len(pdf_files)} files)")
    click.echo(f"📂 Output: {output}")
    if is_recursive_mode:
        click.echo("🔄 Mode: Recursive (preserves folder structure)")
    click.echo(f"🌐 Translation: {source_name} → {target_name}")
    click.echo("="*60)
    
    # Initialize usage tracker
    tracker = UsageTracker()
    
    # Translate files
    total_files_processed = 0
    success_count = 0
    total_cost = 0.0
    
    for idx, pdf_file in enumerate(pdf_files, 1):
        click.echo(f"\n[{idx}/{len(pdf_files)}]", nl=False)
        
        # Determine output path
        if is_recursive_mode:
            # Recursive mode: preserve folder structure
            output_path = get_output_path_with_structure(
                pdf_file, input_base_dir, output, target
            )
            rel_path = os.path.relpath(pdf_file, input_base_dir)
        else:
            # Normal mode: save directly to output folder
            filename = os.path.basename(pdf_file)
            name_without_ext = os.path.splitext(filename)[0]
            output_filename = f"{name_without_ext}_{target}.pdf"
            output_path = os.path.join(output, output_filename)
            rel_path = None
        
        success, files, file_size = translate_single_file(
            pdf_file, output_path, source, target, client, tracker, rel_path
        )
        if success:
            success_count += 1
            total_files_processed += files
            total_cost += tracker.calculate_cost(file_size)
    
    # Completion message
    click.echo("\n" + "="*60)
    if success_count == len(pdf_files):
        click.echo(f"✅ Complete! Successfully translated {success_count} files")
    else:
        click.echo(f"⚠️  Complete: {success_count}/{len(pdf_files)} files succeeded")
    
    if total_cost > 0:
        click.echo(f"💰 Estimated cost for this operation: ${total_cost:.2f}")
    
    # Cumulative statistics
    summary = tracker.get_summary()
    click.echo(f"📊 Cumulative: {summary['total_files']} files | ${summary['total_cost_usd']:.2f}")
    click.echo("="*60 + "\n")


@cli.command()
@click.option(
    '--detail', '-d',
    is_flag=True,
    help='Show detailed history'
)
@click.option(
    '--month',
    type=int,
    help='View statistics for a specific month (1-12)'
)
@click.option(
    '--year',
    type=int,
    help='Specify year (default: current year)'
)
@click.option(
    '--clear',
    is_flag=True,
    help='Clear usage history (warning: irreversible)'
)
def stats(detail: bool, month: int, year: int, clear: bool):
    """View API usage statistics and cost
    
    Examples:
    
        # View summary
        python translate.py stats
        
        # View detailed history (last 10 records)
        python translate.py stats --detail
        
        # This month's statistics
        python translate.py stats --month 2
        
        # Specific year-month statistics
        python translate.py stats --month 2 --year 2026
        
        # Clear usage history
        python translate.py stats --clear
    """
    tracker = UsageTracker()
    
    # Clear history
    if clear:
        click.confirm('⚠️  Are you sure you want to delete all usage history?', abort=True)
        tracker.clear_history()
        click.echo("✅ Usage history has been cleared.")
        return
    
    # Monthly statistics
    if month:
        if not year:
            year = datetime.now().year
        
        if not (1 <= month <= 12):
            click.echo("❌ Error: Month must be between 1 and 12.", err=True)
            sys.exit(1)
        
        monthly = tracker.get_monthly_summary(year, month)
        
        click.echo("\n" + "="*60)
        click.echo(f"📅 Usage Statistics for {year}-{month:02d}")
        click.echo("="*60)
        click.echo(f"📄 Files translated: {monthly['files']}")
        click.echo(f"📊 Total size: {monthly['size_mb']:.2f} MB")
        click.echo(f"💰 Estimated cost: ${monthly['cost_usd']:.2f} USD")
        click.echo("="*60 + "\n")
        return
    
    # Overall summary
    summary = tracker.get_summary()
    
    click.echo("\n" + "="*60)
    click.echo("📊 PDF Translator - Usage Statistics")
    click.echo("="*60)
    click.echo(f"📄 Total files translated: {summary['total_files']}")
    click.echo(f"📦 Total data processed: {summary['total_size_mb']:.2f} MB")
    click.echo(f"💰 Cumulative estimated cost: ${summary['total_cost_usd']:.2f} USD")
    click.echo("="*60)
    
    # Detailed history
    if detail:
        translations = tracker.get_recent_translations(limit=10)
        
        if not translations:
            click.echo("\n📭 No translation history found.\n")
            return
        
        click.echo(f"\n📋 Recent Translation History (max 10 records):\n")
        
        for i, record in enumerate(reversed(translations), 1):
            timestamp = datetime.fromisoformat(record['timestamp'])
            date_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            
            click.echo(f"{i}. {record['input_file']}")
            click.echo(f"   🕐 {date_str}")
            click.echo(f"   🌐 {record['source_lang']} → {record['target_lang']}")
            click.echo(f"   📊 {record['file_size_mb']:.2f} MB | 💰 ${record['estimated_cost_usd']:.2f}")
            click.echo(f"   → {record['output_file']}")
            click.echo()
    else:
        click.echo("\n💡 For detailed history: python translate.py stats --detail\n")


if __name__ == '__main__':
    cli()
