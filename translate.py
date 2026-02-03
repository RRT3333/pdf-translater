#!/usr/bin/env python3
"""PDF Translation CLI Program - Google Cloud Translation API v3 Document Translation"""

import os
import sys
import click
from dotenv import load_dotenv
from datetime import datetime

from translator import (
    TranslationClient,
    TranslationService,
    UsageTracker,
    validate_credentials,
    LANGUAGE_NAMES,
    DEFAULT_SOURCE_LANG,
    DEFAULT_TARGET_LANG,
    DEFAULT_OUTPUT_DIR,
)
from translator.utils import get_pdf_files, get_pdf_files_recursive
from translator.validators import validate_month

# Load .env file
load_dotenv()


@click.group(invoke_without_command=True)
@click.pass_context
@click.option(
    '--input', '-i',
    type=click.Path(exists=True),
    help='Input PDF file or folder path'
)
@click.option(
    '--output', '-o',
    default=DEFAULT_OUTPUT_DIR,
    type=click.Path(),
    help=f'Output folder path (default: {DEFAULT_OUTPUT_DIR})'
)
@click.option(
    '--source', '-s',
    default=DEFAULT_SOURCE_LANG,
    help=f'Source language code (default: {DEFAULT_SOURCE_LANG}, empty string for auto-detection)'
)
@click.option(
    '--target', '-t',
    default=DEFAULT_TARGET_LANG,
    help=f'Target language code (default: {DEFAULT_TARGET_LANG})'
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
@click.option('--output', '-o', default=DEFAULT_OUTPUT_DIR, type=click.Path())
@click.option('--source', '-s', default=DEFAULT_SOURCE_LANG)
@click.option('--target', '-t', default=DEFAULT_TARGET_LANG)
@click.option('--batch', '-b', is_flag=True)
@click.option('--recursive', '-r', is_flag=True)
def translate_command(input: str, output: str, source: str, target: str, batch: bool, recursive: bool):
    """Execute the translation command"""
    
    # Validate credentials
    validate_credentials()
    
    # Create output directory
    os.makedirs(output, exist_ok=True)
    
    # Initialize clients
    try:
        client = TranslationClient()
        tracker = UsageTracker()
        service = TranslationService(client, tracker)
    except Exception as e:
        click.echo(f"❌ Error: Failed to initialize: {str(e)}", err=True)
        sys.exit(1)
    
    # Determine input files and mode
    pdf_files, is_recursive_mode, input_base_dir = _get_input_files(input, batch, recursive)
    
    # Get language display names
    source_name = LANGUAGE_NAMES.get(source, source.upper())
    target_name = LANGUAGE_NAMES.get(target, target.upper())
    
    # Display start message
    _print_header(input, output, pdf_files, source_name, target_name, is_recursive_mode)
    
    # Process files
    success_count, total_cost = _process_files(
        service, pdf_files, output, source, target,
        is_recursive_mode, input_base_dir
    )
    
    # Display completion message
    _print_footer(success_count, len(pdf_files), total_cost, tracker)


def _get_input_files(input: str, batch: bool, recursive: bool):
    """Get list of files to process based on input mode"""
    
    if recursive:
        if not os.path.isdir(input):
            click.echo("❌ Error: --recursive option must be used with a folder path.", err=True)
            sys.exit(1)
        
        pdf_files_with_rel = get_pdf_files_recursive(input)
        if not pdf_files_with_rel:
            click.echo(f"❌ Error: No PDF files found in {input} folder.", err=True)
            sys.exit(1)
        
        pdf_files = [abs_path for abs_path, rel_path in pdf_files_with_rel]
        return pdf_files, True, input
        
    elif batch or os.path.isdir(input):
        if not os.path.isdir(input):
            click.echo("❌ Error: --batch option must be used with a folder path.", err=True)
            sys.exit(1)
        
        pdf_files = get_pdf_files(input)
        if not pdf_files:
            click.echo(f"❌ Error: No PDF files found in {input} folder.", err=True)
            sys.exit(1)
        
        return pdf_files, False, None
        
    else:
        if not input.lower().endswith('.pdf'):
            click.echo("❌ Error: Only PDF files are supported.", err=True)
            sys.exit(1)
        
        return [input], False, None


def _print_header(input: str, output: str, pdf_files: list, source_name: str, target_name: str, is_recursive: bool):
    """Print translation job header"""
    click.echo("\n" + "="*60)
    click.echo("🌏 PDF Translator (Document Translation API)")
    click.echo("="*60)
    click.echo(f"📁 Input: {input} ({len(pdf_files)} files)")
    click.echo(f"📂 Output: {output}")
    if is_recursive:
        click.echo("🔄 Mode: Recursive (preserves folder structure)")
    click.echo(f"🌐 Translation: {source_name} → {target_name}")
    click.echo("="*60)


def _process_files(service, pdf_files: list, output: str, source: str, target: str, is_recursive: bool, input_base_dir: str):
    """Process all files for translation"""
    success_count = 0
    total_cost = 0.0
    
    for idx, pdf_file in enumerate(pdf_files, 1):
        click.echo(f"\n[{idx}/{len(pdf_files)}]", nl=False)
        
        # Generate output path
        output_path = service.get_output_path(
            pdf_file, output, target,
            preserve_structure=is_recursive,
            input_base_dir=input_base_dir
        )
        
        # Get relative path for display
        rel_path = None
        if is_recursive and input_base_dir:
            rel_path = os.path.relpath(pdf_file, input_base_dir)
        
        # Translate file
        success, files, file_size = service.translate_file(
            pdf_file, output_path, source, target, rel_path
        )
        
        if success:
            success_count += 1
            total_cost += service.tracker.calculate_cost(file_size)
    
    return success_count, total_cost


def _print_footer(success_count: int, total_files: int, total_cost: float, tracker: UsageTracker):
    """Print translation job footer"""
    click.echo("\n" + "="*60)
    
    if success_count == total_files:
        click.echo(f"✅ Complete! Successfully translated {success_count} files")
    else:
        click.echo(f"⚠️  Complete: {success_count}/{total_files} files succeeded")
    
    if total_cost > 0:
        click.echo(f"💰 Estimated cost for this operation: ${total_cost:.2f}")
    
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
        _show_monthly_stats(tracker, month, year)
        return
    
    # Overall summary
    _show_summary(tracker, detail)


def _show_monthly_stats(tracker: UsageTracker, month: int, year: int):
    """Show monthly statistics"""
    if not year:
        year = datetime.now().year
    
    try:
        validate_month(month)
    except click.ClickException as e:
        click.echo(f"❌ Error: {e.message}", err=True)
        sys.exit(1)
    
    monthly = tracker.get_monthly_summary(year, month)
    
    click.echo("\n" + "="*60)
    click.echo(f"📅 Usage Statistics for {year}-{month:02d}")
    click.echo("="*60)
    click.echo(f"📄 Files translated: {monthly['files']}")
    click.echo(f"📊 Total size: {monthly['size_mb']:.2f} MB")
    click.echo(f"💰 Estimated cost: ${monthly['cost_usd']:.2f} USD")
    click.echo("="*60 + "\n")


def _show_summary(tracker: UsageTracker, detail: bool):
    """Show overall summary"""
    summary = tracker.get_summary()
    
    click.echo("\n" + "="*60)
    click.echo("📊 PDF Translator - Usage Statistics")
    click.echo("="*60)
    click.echo(f"📄 Total files translated: {summary['total_files']}")
    click.echo(f"📦 Total data processed: {summary['total_size_mb']:.2f} MB")
    click.echo(f"💰 Cumulative estimated cost: ${summary['total_cost_usd']:.2f} USD")
    click.echo("="*60)
    
    if detail:
        _show_detailed_history(tracker)
    else:
        click.echo("\n💡 For detailed history: python translate.py stats --detail\n")


def _show_detailed_history(tracker: UsageTracker):
    """Show detailed translation history"""
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


if __name__ == '__main__':
    cli()
