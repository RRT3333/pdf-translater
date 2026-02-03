"""유틸리티 함수들"""

import os
from typing import List, Tuple
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
import io


def extract_text_from_pdf(pdf_path: str) -> List[Tuple[int, str]]:
    """
    PDF에서 텍스트 추출
    
    Args:
        pdf_path: PDF 파일 경로
        
    Returns:
        (페이지 번호, 텍스트) 튜플 리스트
    """
    try:
        reader = PdfReader(pdf_path)
        pages_text = []
        
        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            pages_text.append((page_num, text))
        
        return pages_text
    except Exception as e:
        raise Exception(f"PDF 텍스트 추출 오류: {str(e)}")


def create_translated_pdf(
    original_pdf_path: str,
    translated_texts: List[str],
    output_path: str,
    font_path: str = None
) -> None:
    """
    번역된 텍스트로 새 PDF 생성
    
    Args:
        original_pdf_path: 원본 PDF 경로
        translated_texts: 번역된 텍스트 리스트 (페이지별)
        output_path: 출력 PDF 경로
        font_path: 폰트 파일 경로 (옵션)
    """
    try:
        reader = PdfReader(original_pdf_path)
        writer = PdfWriter()
        
        for page_num, translated_text in enumerate(translated_texts):
            # 원본 페이지 크기 가져오기
            original_page = reader.pages[page_num]
            page_width = float(original_page.mediabox.width)
            page_height = float(original_page.mediabox.height)
            
            # 새 PDF 페이지 생성
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=(page_width, page_height))
            
            # 한글 폰트 설정 (시스템 기본 폰트 사용 또는 지정된 폰트)
            try:
                if font_path and os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('CustomFont', font_path))
                    can.setFont('CustomFont', 10)
                else:
                    # Windows 기본 한글 폰트 시도
                    windows_font = 'C:/Windows/Fonts/malgun.ttf'
                    if os.path.exists(windows_font):
                        pdfmetrics.registerFont(TTFont('Malgun', windows_font))
                        can.setFont('Malgun', 10)
                    else:
                        can.setFont('Helvetica', 10)
            except:
                can.setFont('Helvetica', 10)
            
            # 텍스트를 페이지에 추가
            y_position = page_height - 50
            line_height = 14
            max_width = page_width - 100
            
            # 텍스트를 줄 단위로 나누기
            lines = translated_text.split('\n')
            
            for line in lines:
                if y_position < 50:  # 페이지 하단에 도달하면 중단
                    break
                
                # 긴 줄을 자동으로 줄바꿈
                wrapped_lines = simpleSplit(line, 'Helvetica', 10, max_width)
                for wrapped_line in wrapped_lines:
                    if y_position < 50:
                        break
                    can.drawString(50, y_position, wrapped_line)
                    y_position -= line_height
            
            can.save()
            
            # 새 페이지를 Writer에 추가
            packet.seek(0)
            new_pdf = PdfReader(packet)
            
            # 원본 페이지에 번역 페이지 오버레이
            original_page.merge_page(new_pdf.pages[0])
            writer.add_page(original_page)
        
        # PDF 저장
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
            
    except Exception as e:
        raise Exception(f"PDF 생성 오류: {str(e)}")


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
