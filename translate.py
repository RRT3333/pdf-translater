#!/usr/bin/env python3
"""PDF 번역 CLI 프로그램"""

import os
import sys
import click
from dotenv import load_dotenv
from pathlib import Path
from typing import List

from translator import TranslationClient, extract_text_from_pdf, create_translated_pdf
from translator.utils import get_pdf_files, format_file_size

# .env 파일 로드
load_dotenv()


def validate_credentials():
    """Google Cloud 인증 정보 확인"""
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if not credentials_path:
        click.echo("❌ 오류: GOOGLE_APPLICATION_CREDENTIALS 환경 변수가 설정되지 않았습니다.", err=True)
        click.echo("💡 .env 파일에 다음을 추가하세요:", err=True)
        click.echo("   GOOGLE_APPLICATION_CREDENTIALS=./credentials.json", err=True)
        sys.exit(1)
    
    if not os.path.exists(credentials_path):
        click.echo(f"❌ 오류: 인증 파일을 찾을 수 없습니다: {credentials_path}", err=True)
        click.echo("💡 Google Cloud Console에서 서비스 계정 키를 다운로드하세요.", err=True)
        sys.exit(1)


def translate_single_file(
    input_path: str,
    output_dir: str,
    source_lang: str,
    target_lang: str,
    client: TranslationClient
):
    """단일 PDF 파일 번역"""
    try:
        filename = os.path.basename(input_path)
        click.echo(f"\n📄 {filename}")
        
        # PDF에서 텍스트 추출
        click.echo("   📖 텍스트 추출 중...", nl=False)
        pages_text = extract_text_from_pdf(input_path)
        click.echo(f" ✓ ({len(pages_text)} 페이지)")
        
        # 각 페이지 번역
        translated_pages = []
        with click.progressbar(
            pages_text, 
            label="   🌐 번역 중",
            show_pos=True,
            item_show_func=lambda x: f"페이지 {x[0]}/{len(pages_text)}" if x else ""
        ) as bar:
            for page_num, text in bar:
                if text.strip():
                    translated_text = client.translate_text(
                        text, 
                        target_language=target_lang,
                        source_language=source_lang
                    )
                    translated_pages.append(translated_text)
                else:
                    translated_pages.append("")
        
        # 출력 파일명 생성
        name_without_ext = os.path.splitext(filename)[0]
        output_filename = f"{name_without_ext}_{target_lang}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        # 번역된 PDF 생성
        click.echo("   💾 PDF 생성 중...", nl=False)
        create_translated_pdf(input_path, translated_pages, output_path)
        
        file_size = format_file_size(os.path.getsize(output_path))
        click.echo(f" ✓ ({file_size})")
        click.echo(f"   → {output_path}")
        
        return True, len(pages_text)
        
    except Exception as e:
        click.echo(f"\n❌ 오류: {str(e)}", err=True)
        return False, 0


@click.command()
@click.option(
    '--input', '-i',
    required=True,
    type=click.Path(exists=True),
    help='입력 PDF 파일 또는 폴더 경로'
)
@click.option(
    '--output', '-o',
    default='./output',
    type=click.Path(),
    help='출력 폴더 경로 (기본값: ./output)'
)
@click.option(
    '--source', '-s',
    default='ja',
    help='출발어 코드 (기본값: ja)'
)
@click.option(
    '--target', '-t',
    default='ko',
    help='도착어 코드 (기본값: ko)'
)
@click.option(
    '--batch', '-b',
    is_flag=True,
    help='폴더 일괄 처리 모드'
)
def main(input: str, output: str, source: str, target: str, batch: bool):
    """PDF 번역 CLI 프로그램
    
    일본어 PDF 문서를 한국어로 번역합니다.
    
    예시:
    
        # 단일 파일 번역
        python translate.py -i ./document.pdf -o ./output/
        
        # 폴더 일괄 번역
        python translate.py -i ./docs/ -o ./output/ --batch
        
        # 언어 지정
        python translate.py -i ./docs/ -s en -t ko --batch
    """
    # 인증 정보 확인
    validate_credentials()
    
    # 출력 디렉토리 생성
    os.makedirs(output, exist_ok=True)
    
    # Translation 클라이언트 초기화
    try:
        client = TranslationClient()
    except Exception as e:
        click.echo(f"❌ 오류: Translation API 클라이언트 초기화 실패: {str(e)}", err=True)
        sys.exit(1)
    
    # 입력 파일 목록 가져오기
    if batch or os.path.isdir(input):
        if not os.path.isdir(input):
            click.echo("❌ 오류: --batch 옵션은 폴더 경로와 함께 사용해야 합니다.", err=True)
            sys.exit(1)
        pdf_files = get_pdf_files(input)
        if not pdf_files:
            click.echo(f"❌ 오류: {input} 폴더에 PDF 파일이 없습니다.", err=True)
            sys.exit(1)
    else:
        if not input.lower().endswith('.pdf'):
            click.echo("❌ 오류: PDF 파일만 지원합니다.", err=True)
            sys.exit(1)
        pdf_files = [input]
    
    # 언어 이름 매핑
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
    
    # 시작 메시지
    click.echo("\n" + "="*60)
    click.echo("🌏 PDF Translator")
    click.echo("="*60)
    click.echo(f"📁 입력: {input} ({len(pdf_files)}개 파일)")
    click.echo(f"📂 출력: {output}")
    click.echo(f"🌐 번역: {source_name} → {target_name}")
    click.echo("="*60)
    
    # 파일 번역
    total_pages = 0
    success_count = 0
    
    for idx, pdf_file in enumerate(pdf_files, 1):
        click.echo(f"\n[{idx}/{len(pdf_files)}]", nl=False)
        success, pages = translate_single_file(
            pdf_file, output, source, target, client
        )
        if success:
            success_count += 1
            total_pages += pages
    
    # 완료 메시지
    click.echo("\n" + "="*60)
    if success_count == len(pdf_files):
        click.echo(f"✅ 완료! 총 {success_count}개 파일 | {total_pages} 페이지")
    else:
        click.echo(f"⚠️  완료: {success_count}/{len(pdf_files)}개 파일 성공")
    
    # 예상 비용 (참고용)
    estimated_cost = total_pages * 0.08  # 페이지당 약 $0.08 (대략적인 추정)
    click.echo(f"💰 예상 비용: ${estimated_cost:.2f} (참고용)")
    click.echo("="*60 + "\n")


if __name__ == '__main__':
    main()
