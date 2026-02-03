"""유틸리티 함수들"""

import os
from typing import List, Tuple


def save_translated_document(
    document_content: bytes,
    output_path: str
) -> None:
    """
    번역된 문서를 파일로 저장
    
    Args:
        document_content: 번역된 문서의 바이너리 데이터
        output_path: 출력 파일 경로
    """
    try:
        # 출력 디렉토리 생성
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 파일 저장
        with open(output_path, 'wb') as f:
            f.write(document_content)
            
    except Exception as e:
        raise Exception(f"문서 저장 오류: {str(e)}")


def get_pdf_files(directory: str) -> List[str]:
    """
    디렉토리에서 PDF 파일 목록 가져오기 (하위 폴더 제외)
    
    Args:
        directory: 검색할 디렉토리 경로
        
    Returns:
        PDF 파일 경로 리스트
    """
    pdf_files = []
    
    for file in os.listdir(directory):
        if file.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(directory, file))
    
    return sorted(pdf_files)


def get_pdf_files_recursive(directory: str) -> List[Tuple[str, str]]:
    """
    디렉토리에서 재귀적으로 PDF 파일 찾기
    
    Args:
        directory: 검색할 루트 디렉토리 경로
        
    Returns:
        (절대경로, 상대경로) 튜플 리스트
    """
    pdf_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, directory)
                pdf_files.append((abs_path, rel_path))
    
    return sorted(pdf_files, key=lambda x: x[1])


def get_output_path_with_structure(
    input_path: str,
    input_base_dir: str,
    output_base_dir: str,
    target_lang: str
) -> str:
    """
    입력 파일의 폴더 구조를 유지하면서 출력 경로 생성
    
    Args:
        input_path: 입력 파일 절대 경로
        input_base_dir: 입력 기본 디렉토리
        output_base_dir: 출력 기본 디렉토리
        target_lang: 도착어 코드
        
    Returns:
        출력 파일 경로
    """
    # 상대 경로 추출
    rel_path = os.path.relpath(input_path, input_base_dir)
    
    # 파일명과 디렉토리 분리
    rel_dir = os.path.dirname(rel_path)
    filename = os.path.basename(rel_path)
    
    # 파일명에 언어 코드 추가
    name_without_ext = os.path.splitext(filename)[0]
    new_filename = f"{name_without_ext}_{target_lang}.pdf"
    
    # 출력 경로 생성
    if rel_dir:
        output_path = os.path.join(output_base_dir, rel_dir, new_filename)
    else:
        output_path = os.path.join(output_base_dir, new_filename)
    
    return output_path


def format_file_size(size_bytes: int) -> str:
    """
    파일 크기를 읽기 쉬운 형식으로 변환
    
    Args:
        size_bytes: 바이트 단위 크기
        
    Returns:
        포맷된 크기 문자열
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
