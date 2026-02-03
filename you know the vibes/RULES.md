# PDF Translator - Development Rules

이 문서는 PDF Translator 프로젝트의 코딩 규칙, 스타일 가이드, 베스트 프랙티스를 정의합니다.

---

## 일반 원칙

### 코드 스타일

- **PEP 8** 준수
- **타입 힌팅** 필수 (Python 3.10+ annotations)
- **Docstring** 모든 함수/클래스에 작성 (Google Style)
- **변수명**: snake_case (함수, 변수)
- **클래스명**: PascalCase
- **상수**: UPPER_SNAKE_CASE
- **들여쓰기**: 스페이스 4칸

### 파일 구조

```python
# 1. Shebang (CLI 파일만)
#!/usr/bin/env python3

# 2. Docstring
"""모듈 설명"""

# 3. Imports
import os  # 표준 라이브러리
import sys

from google.cloud import translate_v3  # 서드파티
from typing import Dict, List

from translator import utils  # 로컬 모듈

# 4. 상수
DEFAULT_SOURCE = "ja"
DEFAULT_TARGET = "ko"

# 5. 클래스/함수
class MyClass:
    ...

# 6. Main 실행부
if __name__ == '__main__':
    main()
```

---

## Python 버전 및 의존성

### Python 버전
- **최소**: Python 3.10
- **권장**: Python 3.11+
- **이유**: Type hints (Union types with `|`), Pattern matching 지원

### 필수 라이브러리
```
google-cloud-translate>=3.15.0  # v3 API 필수
click>=8.0.0                     # CLI 프레임워크
python-dotenv>=1.0.0            # 환경 변수 관리
```

### 금지 라이브러리
- ❌ `PyPDF2` - 사용하지 않음 (Document Translation 직접 사용)
- ❌ `reportlab` - PDF 생성 불필요
- ❌ `translate_v2` - 구버전 API

---

## 코딩 규칙

### 1. 타입 힌팅

**필수**: 모든 함수 매개변수 및 반환값에 타입 힌트

```python
# ✅ Good
def translate_document(
    file_path: str,
    target_language: str = "ko",
    source_language: str = "ja"
) -> Dict[str, Any]:
    ...

# ❌ Bad
def translate_document(file_path, target_language="ko"):
    ...
```

**복잡한 타입**:
```python
from typing import Dict, List, Optional, Union

def get_translations() -> List[Dict[str, Union[str, float]]]:
    ...
```

### 2. Docstring

**Google Style 사용**:

```python
def calculate_cost(file_size_bytes: int) -> float:
    """
    파일 크기 기반 비용 계산
    
    Document Translation API 비용 구조를 기반으로 예상 비용을 계산합니다.
    1MB ≈ 10페이지로 추정하며, 평균 페이지당 $0.06를 적용합니다.
    
    Args:
        file_size_bytes: 파일 크기 (바이트 단위)
        
    Returns:
        예상 비용 (USD)
        
    Raises:
        ValueError: file_size_bytes가 음수인 경우
        
    Examples:
        >>> calculate_cost(2 * 1024 * 1024)  # 2MB
        1.2
    """
    ...
```

### 3. 에러 처리

**구체적인 예외 처리**:

```python
# ✅ Good
try:
    with open(file_path, 'rb') as f:
        content = f.read()
except FileNotFoundError:
    raise Exception(f"파일을 찾을 수 없습니다: {file_path}")
except PermissionError:
    raise Exception(f"파일 접근 권한이 없습니다: {file_path}")
except Exception as e:
    raise Exception(f"파일 읽기 오류: {str(e)}")

# ❌ Bad
try:
    content = open(file_path).read()
except:
    pass
```

**사용자 친화적 메시지**:
```python
# ✅ Good
raise Exception("번역 중 오류 발생: API 할당량을 확인하세요.")

# ❌ Bad
raise Exception("Translation failed: quota exceeded")
```

### 4. 환경 변수

**반드시 `.env` 사용**:

```python
from dotenv import load_dotenv
import os

# ✅ 프로그램 시작 시 로드
load_dotenv()

# ✅ 기본값 제공
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
if not project_id:
    raise ValueError("GOOGLE_CLOUD_PROJECT 환경 변수가 설정되지 않았습니다.")
```

**절대 하드코딩 금지**:
```python
# ❌ Bad
PROJECT_ID = "my-project-12345"
CREDENTIALS_PATH = "C:/Users/myuser/creds.json"
```

---

## API 사용 규칙

### Google Cloud Translation API

**항상 v3 사용**:
```python
# ✅ Good
from google.cloud import translate_v3 as translate
client = translate.TranslationServiceClient()

# ❌ Bad - v2 사용 금지
from google.cloud import translate_v2
```

**Location 명시**:
```python
# ✅ us-central1 또는 global 사용
self.location = "us-central1"
self.parent = f"projects/{self.project_id}/locations/{self.location}"
```

**에러 처리**:
```python
from google.api_core import exceptions

try:
    response = self.client.translate_document(request=request)
except exceptions.PermissionDenied:
    raise Exception("API 권한이 없습니다. 서비스 계정 역할을 확인하세요.")
except exceptions.ResourceExhausted:
    raise Exception("API 할당량을 초과했습니다.")
except Exception as e:
    raise Exception(f"문서 번역 중 오류 발생: {str(e)}")
```

---

## CLI 규칙 (Click)

### 명령어 구조

```python
# ✅ Group 사용으로 확장 가능
@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        # 기본 동작
        ...

@cli.command()
def stats():
    """통계 조회"""
    ...
```

### 옵션 정의

```python
@click.option(
    '--input', '-i',              # 긴 이름, 짧은 이름
    required=True,                # 필수 여부
    type=click.Path(exists=True), # 타입 및 검증
    help='입력 파일 경로'          # 도움말 (한글)
)
```

### 사용자 출력

**이모지 사용으로 가독성 향상**:
```python
click.echo("✅ 완료!")
click.echo("❌ 오류: 파일이 없습니다.")
click.echo("💰 예상 비용: $1.26")
click.echo("📊 통계")
```

**진행 상황 표시**:
```python
with click.progressbar(items, label='처리 중') as bar:
    for item in bar:
        process(item)
```

---

## 파일 처리 규칙

### 경로 처리

**항상 `os.path` 사용** (Windows 호환성):

```python
# ✅ Good
output_path = os.path.join(output_dir, filename)
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# ❌ Bad - UNIX만 지원
output_path = f"{output_dir}/{filename}"
```

### 파일 I/O

**컨텍스트 매니저 필수**:

```python
# ✅ Good
with open(file_path, 'rb') as f:
    content = f.read()

# ❌ Bad
f = open(file_path, 'rb')
content = f.read()
f.close()
```

**JSON 처리**:
```python
import json

# ✅ 인코딩 명시
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
```

---

## 데이터 관리

### Usage History

**JSON 구조 엄격히 준수**:

```python
{
  "total_files": int,        # 누적 파일 수
  "total_cost_usd": float,   # 누적 비용 (소수점 2자리)
  "total_size_mb": float,    # 누적 용량 (소수점 2자리)
  "translations": [          # 번역 기록 배열
    {
      "timestamp": str,      # ISO-8601 형식
      "input_file": str,     # 파일명만 (경로 제외)
      "output_file": str,
      "source_lang": str,
      "target_lang": str,
      "file_size_mb": float,
      "estimated_cost_usd": float
    }
  ]
}
```

**데이터 검증**:
```python
# ✅ 저장 전 round 처리
self.data["total_cost_usd"] = round(total_cost, 2)
self.data["total_size_mb"] = round(total_size, 2)
```

---

## 보안 규칙

### 민감 정보

**절대 Git 커밋 금지**:
- `.env` - 환경 변수
- `credentials.json` - GCP 키
- `usage_history.json` - 개인 사용 기록

**.gitignore 필수 항목**:
```
.env
credentials.json
usage_history.json
venv/
__pycache__/
*.pyc
```

### API 키

**환경 변수로만 관리**:
```python
# ✅ Good
credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# ❌ Bad
credentials = "./my-secret-key.json"
```

---

## 테스트 규칙

### 테스트 작성 (향후)

```python
# tests/test_client.py
import pytest
from translator import TranslationClient

def test_client_initialization():
    client = TranslationClient(project_id="test-project")
    assert client.project_id == "test-project"

def test_invalid_project_id():
    with pytest.raises(ValueError):
        client = TranslationClient(project_id=None)
```

### Mock 사용

```python
from unittest.mock import Mock, patch

@patch('translator.client.translate.TranslationServiceClient')
def test_translate_document(mock_client):
    mock_client.return_value.translate_document.return_value = Mock(
        document_translation=Mock(byte_stream_outputs=[b"translated"])
    )
    # 테스트 로직
```

---

## 로깅 규칙 (향후)

### 로깅 레벨

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.debug("디버그 정보")
logger.info("일반 정보")
logger.warning("경고")
logger.error("에러")
```

### 로그 vs 출력

- **사용자 출력**: `click.echo()` 사용
- **디버그 로그**: `logger.debug()` 사용
- **에러 로그**: `logger.error()` + `click.echo(..., err=True)`

---

## 성능 규칙

### API 호출 최적화

```python
# ✅ 파일 크기 체크
if file_size > 10 * 1024 * 1024:
    click.echo("⚠️  경고: 10MB 초과")

# ✅ 재시도 로직 (향후)
from google.api_core import retry
@retry.Retry()
def translate_with_retry():
    ...
```

### 메모리 관리

```python
# ✅ 큰 파일 처리 시 스트리밍
with open(file_path, 'rb') as f:
    chunk_size = 1024 * 1024  # 1MB chunks
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        process(chunk)
```

---

## 버전 관리

### 시맨틱 버저닝

- **MAJOR**: API 변경 (호환성 깨짐)
- **MINOR**: 기능 추가 (하위 호환)
- **PATCH**: 버그 수정

### 버전 표기

```python
# translator/__init__.py
__version__ = "2.0.0"
```

---

## 금지 사항

1. ❌ **하드코딩**: API 키, 경로, 프로젝트 ID 등
2. ❌ **전역 변수**: 가능한 한 사용 금지
3. ❌ **Magic Number**: 상수로 정의
4. ❌ **Bare except**: `except Exception as e` 사용
5. ❌ **mutable 기본값**: `def func(items=[])` 금지
6. ❌ **print()**: CLI는 `click.echo()` 사용
7. ❌ **상대 경로**: 절대 경로 또는 `os.path.join()` 사용
8. ❌ **한글 변수명**: 주석과 문자열만 한글 허용

---

## 코드 리뷰 체크리스트

- [ ] 타입 힌트 모두 작성
- [ ] Docstring 작성 (Google Style)
- [ ] 에러 처리 적절
- [ ] 사용자 메시지 한글 + 이모지
- [ ] 환경 변수로 설정 관리
- [ ] 파일 I/O 컨텍스트 매니저 사용
- [ ] 경로 처리 `os.path` 사용
- [ ] PEP 8 준수
- [ ] .gitignore 민감 정보 제외
- [ ] 매직 넘버 없음

---

## 참고 자료

- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Google Cloud Translation API v3 Docs](https://cloud.google.com/translate/docs/reference/rest/v3)
- [Click Documentation](https://click.palletsprojects.com/)
