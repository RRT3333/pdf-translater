#!/usr/bin/env python3
"""PDF 번역 CLI 프로그램 - Google Cloud Translation API v3 Document Translation"""

import os
import sys
import click
from dotenv import load_dotenv
from pathlib import Path
from typing import List
from datetime import datetime

from translator import TranslationClient, save_translated_document, UsageTracker
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
    
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        click.echo("❌ 오류: GOOGLE_CLOUD_PROJECT 환경 변수가 설정되지 않았습니다.", err=True)
        click.echo("💡 .env 파일에 다음을 추가하세요:", err=True)
        click.echo("   GOOGLE_CLOUD_PROJECT=your-project-id", err=True)
        sys.exit(1)


def translate_single_file(
    input_path: str,
    output_dir: str,
    source_lang: str,
    target_lang: str,
    client: TranslationClient,
    tracker: UsageTracker = None
):
    """단일 PDF 파일 번역 (Document Translation 사용)"""
    try:
        filename = os.path.basename(input_path)
        click.echo(f"\n📄 {filename}")
        
        file_size = os.path.getsize(input_path)
        click.echo(f"   📊 파일 크기: {format_file_size(file_size)}")
        
        # 파일 크기 제한 확인 (10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            click.echo(f"   ⚠️  경고: 파일이 10MB를 초과합니다. 처리 시간이 오래 걸릴 수 있습니다.", err=True)
        
        # PDF 문서 번역 (API v3 Document Translation)
        click.echo("   🌐 문서 번역 중...", nl=False)
        
        result = client.translate_document(
            file_path=input_path,
            target_language=target_lang,
            source_language=source_lang,
            mime_type="application/pdf"
        )
        
        click.echo(" ✓")
        
        # 출력 파일명 생성
        name_without_ext = os.path.splitext(filename)[0]
        output_filename = f"{name_without_ext}_{target_lang}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        # 번역된 PDF 저장
        click.echo("   💾 파일 저장 중...", nl=False)
        save_translated_document(result["document_content"], output_path)
        
        output_size = format_file_size(os.path.getsize(output_path))
        click.echo(f" ✓ ({output_size})")
        click.echo(f"   → {output_path}")
        
        # 사용 현황 추적
        if tracker:
            estimated_cost = tracker.calculate_cost(file_size)
            click.echo(f"   💰 예상 비용: ${estimated_cost:.2f}")
            tracker.add_translation(
                input_file=input_path,
                output_file=output_path,
                source_lang=source_lang,
                target_lang=target_lang,
                file_size_bytes=file_size
            )
        
        return True, 1, file_size  # 성공, 1개 파일, 파일 크기
        
    except Exception as e:
        click.echo(f"\n❌ 오류: {str(e)}", err=True)
        return False, 0, 0


@click.group(invoke_without_command=True)
@click.pass_context
@click.option(
    '--input', '-i',
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
    help='출발어 코드 (기본값: ja, 빈 문자열로 자동 감지 가능)'
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
def cli(ctx, input, output, source, target, batch):
    """PDF 번역 CLI 프로그램 (Google Cloud Translation API v3 Document Translation)
    
    PDF 문서를 통째로 번역합니다. 레이아웃과 포맷을 유지하며, 텍스트 추출 없이 문서 자체를 번역합니다.
    
    예시:
    
        # 단일 파일 번역
        python translate.py -i ./document.pdf -o ./output/
        
        # 폴더 일괄 번역
        python translate.py -i ./docs/ -o ./output/ --batch
        
        # 언어 지정
        python translate.py -i ./docs/ -s en -t ko --batch
        
        # 자동 언어 감지 (source를 빈 문자열로)
        python translate.py -i ./document.pdf -s "" -t ko
        
        # 사용 현황 조회
        python translate.py stats
        
        # 상세 사용 현황 조회
        python translate.py stats --detail
    """
    if ctx.invoked_subcommand is None:
        if not input:
            click.echo("❌ 오류: --input 옵션이 필요합니다.", err=True)
            click.echo("사용법: python translate.py --help", err=True)
            sys.exit(1)
        
        ctx.invoke(translate_command, input=input, output=output, source=source, target=target, batch=batch)


@cli.command(name='translate', hidden=True)
@click.option('--input', '-i', required=True, type=click.Path(exists=True))
@click.option('--output', '-o', default='./output', type=click.Path())
@click.option('--source', '-s', default='ja')
@click.option('--target', '-t', default='ko')
@click.option('--batch', '-b', is_flag=True)
def translate_command(input: str, output: str, source: str, target: str, batch: bool):
    """PDF 번역 CLI 프로그램 (Google Cloud Translation API v3 Document Translation)
    
    PDF 문서를 통째로 번역합니다. 레이아웃과 포맷을 유지하며, 텍스트 추출 없이 문서 자체를 번역합니다.
    
    예시:
    
        # 단일 파일 번역
        python translate.py -i ./document.pdf -o ./output/
        
        # 폴더 일괄 번역
        python translate.py -i ./docs/ -o ./output/ --batch
        
        # 언어 지정
        python translate.py -i ./docs/ -s en -t ko --batch
        
        # 자동 언어 감지 (source를 빈 문자열로)
        python translate.py -i ./document.pdf -s "" -t ko
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
    click.echo("🌏 PDF Translator (Document Translation API)")
    click.echo("="*60)
    click.echo(f"📁 입력: {input} ({len(pdf_files)}개 파일)")
    click.echo(f"📂 출력: {output}")
    click.echo(f"🌐 번역: {source_name} → {target_name}")
    click.echo("="*60)
    
    # 사용 현황 추적기 초기화
    tracker = UsageTracker()
    
    # 파일 번역
    total_files_processed = 0
    success_count = 0
    total_cost = 0.0
    
    for idx, pdf_file in enumerate(pdf_files, 1):
        click.echo(f"\n[{idx}/{len(pdf_files)}]", nl=False)
        success, files, file_size = translate_single_file(
            pdf_file, output, source, target, client, tracker
        )
        if success:
            success_count += 1
            total_files_processed += files
            total_cost += tracker.calculate_cost(file_size)
    
    # 완료 메시지
    click.echo("\n" + "="*60)
    if success_count == len(pdf_files):
        click.echo(f"✅ 완료! 총 {success_count}개 파일 번역 성공")
    else:
        click.echo(f"⚠️  완료: {success_count}/{len(pdf_files)}개 파일 성공")
    
    if total_cost > 0:
        click.echo(f"💰 이번 작업 예상 비용: ${total_cost:.2f}")
    
    # 누적 통계
    summary = tracker.get_summary()
    click.echo(f"📊 누적: {summary['total_files']}개 파일 | ${summary['total_cost_usd']:.2f}")
    click.echo("="*60 + "\n")


@cli.command()
@click.option(
    '--detail', '-d',
    is_flag=True,
    help='상세 내역 표시'
)
@click.option(
    '--month',
    type=int,
    help='특정 월의 통계 조회 (1-12)'
)
@click.option(
    '--year',
    type=int,
    help='특정 년도 지정 (기본값: 현재 년도)'
)
@click.option(
    '--clear',
    is_flag=True,
    help='사용 기록 초기화 (주의: 복구 불가)'
)
def stats(detail: bool, month: int, year: int, clear: bool):
    """API 사용 현황 및 비용 통계 조회
    
    예시:
    
        # 전체 요약 보기
        python translate.py stats
        
        # 상세 내역 보기 (최근 10건)
        python translate.py stats --detail
        
        # 이번 달 통계
        python translate.py stats --month 2
        
        # 특정 년월 통계
        python translate.py stats --month 2 --year 2026
        
        # 사용 기록 초기화
        python translate.py stats --clear
    """
    tracker = UsageTracker()
    
    # 기록 초기화
    if clear:
        click.confirm('⚠️  모든 사용 기록을 삭제하시겠습니까?', abort=True)
        tracker.clear_history()
        click.echo("✅ 사용 기록이 초기화되었습니다.")
        return
    
    # 월별 통계
    if month:
        if not year:
            year = datetime.now().year
        
        if not (1 <= month <= 12):
            click.echo("❌ 오류: 월은 1-12 사이의 값이어야 합니다.", err=True)
            sys.exit(1)
        
        monthly = tracker.get_monthly_summary(year, month)
        
        click.echo("\n" + "="*60)
        click.echo(f"📅 {year}년 {month}월 사용 현황")
        click.echo("="*60)
        click.echo(f"📄 번역 파일: {monthly['files']}개")
        click.echo(f"📊 총 크기: {monthly['size_mb']:.2f} MB")
        click.echo(f"💰 예상 비용: ${monthly['cost_usd']:.2f} USD")
        click.echo("="*60 + "\n")
        return
    
    # 전체 요약
    summary = tracker.get_summary()
    
    click.echo("\n" + "="*60)
    click.echo("📊 PDF Translator - 사용 현황")
    click.echo("="*60)
    click.echo(f"📄 총 번역 파일: {summary['total_files']}개")
    click.echo(f"📦 총 처리 용량: {summary['total_size_mb']:.2f} MB")
    click.echo(f"💰 누적 예상 비용: ${summary['total_cost_usd']:.2f} USD")
    click.echo("="*60)
    
    # 상세 내역
    if detail:
        translations = tracker.get_recent_translations(limit=10)
        
        if not translations:
            click.echo("\n📭 번역 기록이 없습니다.\n")
            return
        
        click.echo(f"\n📋 최근 번역 기록 (최대 10건):\n")
        
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
        click.echo("\n💡 상세 내역을 보려면: python translate.py stats --detail\n")


if __name__ == '__main__':
    cli()
