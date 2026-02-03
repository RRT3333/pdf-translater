"""유틸리티 함수들"""

import os
from typing import List


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
    디렉토리에서 PDF 파일 목록 가져오기
    
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
