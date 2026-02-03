"""Utility functions"""

import os
from typing import List, Tuple


def save_translated_document(
    document_content: bytes,
    output_path: str
) -> None:
    """
    Save translated document to file
    
    Args:
        document_content: Binary data of translated document
        output_path: Output file path
    """
    try:
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save file
        with open(output_path, 'wb') as f:
            f.write(document_content)
            
    except Exception as e:
        raise Exception(f"Document save error: {str(e)}")


def get_pdf_files(directory: str) -> List[str]:
    """
    Get list of PDF files from directory (excluding subfolders)
    
    Args:
        directory: Directory path to search
        
    Returns:
        List of PDF file paths
    """
    pdf_files = []
    
    for file in os.listdir(directory):
        if file.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(directory, file))
    
    return sorted(pdf_files)


def get_pdf_files_recursive(directory: str) -> List[Tuple[str, str]]:
    """
    Recursively find PDF files in directory
    
    Args:
        directory: Root directory path to search
        
    Returns:
        List of (absolute_path, relative_path) tuples
    """
    pdf_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, directory)
                pdf_files.append((abs_path, rel_path))
    
    return sorted(pdf_files, key=lambda x: x[1])


def format_file_size(size_bytes: int) -> str:
    """
    Convert file size to human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
