# PDF Translator - Skills & Patterns

이 문서는 PDF Translator 프로젝트에서 사용하는 특수 패턴, 기법, 노하우를 정리합니다.

---

## 1. Google Cloud Translation API 패턴

### Document Translation 기본 패턴

```python
from google.cloud import translate_v3 as translate

class TranslationClient:
    def __init__(self, project_id: str):
        self.client = translate.TranslationServiceClient()
        self.location = "us-central1"
        self.parent = f"projects/{project_id}/locations/{self.location}"
    
    def translate_document(self, file_path: str, target: str, source: str = None):
        # 파일 읽기
        with open(file_path, "rb") as f:
            document_content = f.read()
        
        # Document Input Config
        document_input_config = {
            "content": document_content,
            "mime_type": "application/pdf",
        }
        
        # Request 구성
        request = {
            "parent": self.parent,
            "target_language_code": target,
            "document_input_config": document_input_config,
        }
        
        # source_language는 선택적 (자동 감지 가능)
        if source:
            request["source_language_code"] = source
        
        # API 호출
        response = self.client.translate_document(request=request)
        
        return response.document_translation.byte_stream_outputs[0]
```

**핵심 포인트**:
- `document_input_config`: 파일 내용 + MIME 타입
- `source_language_code`: 선택적 (생략 시 자동 감지)
- `byte_stream_outputs[0]`: 번역된 바이너리 데이터

---

## 2. Click CLI 고급 패턴

### Multi-Command CLI

```python
@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx, **kwargs):
    """메인 진입점"""
    if ctx.invoked_subcommand is None:
        # 서브커맨드 없으면 기본 동작
        ctx.invoke(translate_command, **kwargs)

@cli.command(name='translate', hidden=True)
def translate_command(**kwargs):
    """실제 번역 로직"""
    ...

@cli.command()
def stats(**kwargs):
    """통계 조회 로직"""
    ...
```

**장점**:
- 기본 동작 유지: `python translate.py -i file.pdf`
- 서브커맨드 확장: `python translate.py stats`
- `hidden=True`: 내부 명령어 숨김

### Context 전달 패턴

```python
@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    ctx.obj['tracker'] = UsageTracker()

@cli.command()
@click.pass_context
def stats(ctx):
    tracker = ctx.obj['tracker']
    summary = tracker.get_summary()
```

---

## 3. 사용 현황 추적 패턴

### JSON 기반 영속성

```python
class UsageTracker:
    def __init__(self, usage_file: str = "usage_history.json"):
        self.usage_file = usage_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        if os.path.exists(self.usage_file):
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._get_default_data()
    
    def _save_data(self):
        with open(self.usage_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def add_translation(self, **kwargs):
        # 데이터 추가
        self.data['translations'].append(record)
        self.data['total_cost_usd'] = round(total + cost, 2)
        # 즉시 저장
        self._save_data()
```

**핵심 패턴**:
- 초기화 시 자동 로드
- 데이터 수정 후 즉시 저장 (데이터 손실 방지)
- `ensure_ascii=False`: 한글 정상 표시

### 비용 계산 휴리스틱

```python
def calculate_cost(self, file_size_bytes: int) -> float:
    """
    파일 크기 → 페이지 수 → 비용 추정
    """
    file_size_mb = file_size_bytes / (1024 * 1024)
    estimated_pages = max(1, int(file_size_mb * 10))  # 1MB ≈ 10페이지
    cost = estimated_pages * 0.06  # 평균 페이지당 비용
    return round(cost, 2)
```

**휴리스틱 근거**:
- 일반적인 PDF: 1MB ≈ 10페이지
- Document Translation: $0.075/페이지 (최초 500페이지)
- $0.045/페이지 (초과분)
- 평균 $0.06/페이지로 단순화

---

## 4. 에러 처리 패턴

### 인증 검증

```python
def validate_credentials():
    """GCP 인증 정보 사전 검증"""
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
```

**패턴**:
1. 조건 검사
2. 사용자 친화적 에러 메시지
3. 해결 방법 제시
4. 즉시 종료 (`sys.exit(1)`)

### Try-Except 계층화

```python
def translate_single_file(...):
    try:
        # 파일 크기 확인
        file_size = os.path.getsize(input_path)
        
        # API 호출
        result = client.translate_document(...)
        
        # 파일 저장
        save_translated_document(result["document_content"], output_path)
        
        return True, 1, file_size
        
    except FileNotFoundError as e:
        click.echo(f"❌ 오류: 파일을 찾을 수 없습니다: {input_path}", err=True)
        return False, 0, 0
    except PermissionError as e:
        click.echo(f"❌ 오류: 파일 접근 권한이 없습니다.", err=True)
        return False, 0, 0
    except Exception as e:
        click.echo(f"❌ 오류: {str(e)}", err=True)
        return False, 0, 0
```

**장점**:
- 구체적인 예외부터 처리
- 각 상황별 맞춤 메시지
- 일관된 반환값 (성공 여부, 파일 수, 크기)

---

## 5. 파일 처리 패턴

### 안전한 파일 저장

```python
def save_translated_document(document_content: bytes, output_path: str):
    """
    디렉토리 자동 생성 + 안전한 저장
    """
    try:
        # 디렉토리 생성 (존재하면 무시)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 파일 저장
        with open(output_path, 'wb') as f:
            f.write(document_content)
            
    except Exception as e:
        raise Exception(f"문서 저장 오류: {str(e)}")
```

**핵심**:
- `os.makedirs(..., exist_ok=True)`: 디렉토리 자동 생성
- `os.path.dirname()`: 경로에서 디렉토리 추출
- 바이너리 모드 (`'wb'`)

### 파일 목록 가져오기

```python
def get_pdf_files(directory: str) -> List[str]:
    """확장자 대소문자 무시"""
    pdf_files = []
    
    for file in os.listdir(directory):
        if file.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(directory, file))
    
    return sorted(pdf_files)
```

**패턴**:
- `.lower()`: 대소문자 무시 (`.PDF`, `.Pdf` 모두 인식)
- `os.path.join()`: 크로스 플랫폼 경로 생성
- `sorted()`: 파일명 알파벳 순 정렬

---

## 6. 사용자 경험 패턴

### 이모지 사용 규칙

```python
# 상태 표시
"✅" - 성공
"❌" - 에러
"⚠️" - 경고
"💡" - 팁/힌트

# 작업 유형
"📄" - 파일
"📁" - 입력
"📂" - 출력
"📊" - 통계/크기
"🌐" - 번역/언어
"💾" - 저장
"💰" - 비용
"🕐" - 시간
"📅" - 날짜
"📋" - 목록
"📭" - 비어있음
```

### 진행 상황 표시

```python
click.echo("   🌐 문서 번역 중...", nl=False)
# ... 작업 수행 ...
click.echo(" ✓")
```

**패턴**:
- `nl=False`: 줄바꿈 없이 출력
- 작업 완료 후 같은 줄에 체크마크

### 구분선 사용

```python
click.echo("\n" + "="*60)
click.echo("🌏 PDF Translator")
click.echo("="*60)
```

---

## 7. 날짜/시간 처리

### ISO-8601 형식

```python
from datetime import datetime

# 저장 시
timestamp = datetime.now().isoformat()
# "2026-02-03T14:30:00.123456"

# 로드 시
dt = datetime.fromisoformat(record['timestamp'])
date_str = dt.strftime('%Y-%m-%d %H:%M:%S')
# "2026-02-03 14:30:00"
```

**장점**:
- ISO-8601: 국제 표준
- `isoformat()`: 파싱 가능한 문자열
- `fromisoformat()`: 역변환

### 월별 통계 필터링

```python
def get_monthly_summary(self, year: int, month: int) -> Dict:
    monthly_data = {"year": year, "month": month, "files": 0, "cost_usd": 0.0}
    
    for record in self.data["translations"]:
        timestamp = datetime.fromisoformat(record["timestamp"])
        if timestamp.year == year and timestamp.month == month:
            monthly_data["files"] += 1
            monthly_data["cost_usd"] += record["estimated_cost_usd"]
    
    return monthly_data
```

---

## 8. 환경 변수 패턴

### dotenv 초기화

```python
from dotenv import load_dotenv

# 프로그램 시작 시 한 번만
load_dotenv()

# 이후 os.getenv() 사용
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
```

**위치**: 
- CLI 진입점 (`translate.py`) 최상단
- 모듈 import 전에 실행

### 환경 변수 검증

```python
def validate_env_vars():
    """필수 환경 변수 일괄 검증"""
    required = [
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GOOGLE_CLOUD_PROJECT"
    ]
    
    missing = [var for var in required if not os.getenv(var)]
    
    if missing:
        click.echo(f"❌ 오류: 다음 환경 변수가 설정되지 않았습니다:", err=True)
        for var in missing:
            click.echo(f"   - {var}", err=True)
        sys.exit(1)
```

---

## 9. 데이터 포맷팅 패턴

### 파일 크기

```python
def format_file_size(size_bytes: int) -> str:
    """B → KB → MB → GB 자동 변환"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
```

**사용**:
```python
>>> format_file_size(2048)
'2.0 KB'
>>> format_file_size(2 * 1024 * 1024)
'2.0 MB'
```

### 비용 포맷팅

```python
# 항상 소수점 2자리
cost = round(estimated_cost, 2)
click.echo(f"💰 예상 비용: ${cost:.2f}")
```

---

## 10. 배치 처리 패턴

### 파일 루프

```python
success_count = 0
total_cost = 0.0

for idx, pdf_file in enumerate(pdf_files, 1):
    click.echo(f"\n[{idx}/{len(pdf_files)}]", nl=False)
    
    success, files, file_size = translate_single_file(
        pdf_file, output, source, target, client, tracker
    )
    
    if success:
        success_count += 1
        total_cost += tracker.calculate_cost(file_size)

# 결과 요약
click.echo(f"\n✅ 완료: {success_count}/{len(pdf_files)}개 성공")
click.echo(f"💰 총 비용: ${total_cost:.2f}")
```

**패턴**:
- `enumerate(..., 1)`: 1부터 시작하는 인덱스
- 각 파일 성공/실패 추적
- 누적 통계 계산

---

## 11. Git 패턴

### .gitignore 템플릿

```gitignore
# 환경 설정
.env
credentials.json

# 사용 기록
usage_history.json

# Python
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# 출력 파일
output/
```

---

## 12. 확장 패턴

### 새 명령어 추가

```python
@cli.command()
@click.option('--option', help='설명')
def new_command(option):
    """새 명령어 설명"""
    click.echo("새 기능 실행")

# 사용: python translate.py new-command --option value
```

### 새 옵션 추가

```python
@cli.command()
@click.option('--format', type=click.Choice(['pdf', 'docx']), default='pdf')
def translate(format):
    if format == 'docx':
        # DOCX 처리 로직
        ...
```

### 언어 지원 확장

```python
LANGUAGE_NAMES = {
    'ja': '日本語',
    'ko': '한국어',
    'en': 'English',
    'zh': '中文',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'ru': 'Русский',
    'ar': 'العربية',
    # ... 더 추가
}

def get_language_name(code: str) -> str:
    return LANGUAGE_NAMES.get(code, code.upper())
```

---

## 13. 디버깅 패턴

### 환경 정보 출력

```python
@cli.command()
def info():
    """환경 설정 정보 출력"""
    click.echo("=== 환경 정보 ===")
    click.echo(f"Python: {sys.version}")
    click.echo(f"프로젝트 ID: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
    click.echo(f"인증 파일: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
```

### 상세 로그 옵션

```python
@cli.command()
@click.option('--verbose', '-v', is_flag=True, help='상세 출력')
def translate(verbose):
    if verbose:
        click.echo(f"[DEBUG] 요청: {request}")
        click.echo(f"[DEBUG] 응답: {response}")
```

---

## 14. 테스트 패턴 (향후)

### Mock API 응답

```python
from unittest.mock import Mock, patch

@patch('translator.client.translate.TranslationServiceClient')
def test_translate_document(mock_client):
    # Mock 응답 설정
    mock_response = Mock()
    mock_response.document_translation.byte_stream_outputs = [b"translated"]
    mock_client.return_value.translate_document.return_value = mock_response
    
    # 테스트
    client = TranslationClient(project_id="test")
    result = client.translate_document("test.pdf", "ko", "ja")
    
    assert result == b"translated"
```

---

## 15. 성능 최적화 패턴

### 파일 크기 체크

```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

if file_size > MAX_FILE_SIZE:
    click.echo("⚠️  경고: 파일이 10MB를 초과합니다.", err=True)
    if not click.confirm('계속 진행하시겠습니까?'):
        return False, 0, 0
```

### 병렬 처리 (향후)

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(translate_single_file, file, ...)
        for file in pdf_files
    ]
    
    for future in futures:
        result = future.result()
```

---

이 패턴들을 참고하여 일관된 코드를 작성하세요!
