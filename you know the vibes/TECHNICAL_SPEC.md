# PDF Translator - Technical Specification

## 프로젝트 개요

Google Cloud Translation API v3 Document Translation을 사용한 PDF 문서 번역 CLI 도구

- **버전**: 2.0.0
- **Python**: 3.10+
- **주요 API**: Google Cloud Translation API v3 (Document Translation)

---

## 아키텍처

### 디렉토리 구조

```
translate/
├── translate.py              # CLI 진입점 (Click 기반)
├── translator/               # 핵심 비즈니스 로직 패키지
│   ├── __init__.py          # 패키지 초기화 및 exports
│   ├── client.py            # Google Cloud Translation API 클라이언트
│   ├── utils.py             # PDF 처리 유틸리티
│   └── usage.py             # 사용 현황 추적 및 비용 계산
├── .env                      # 환경 변수 (Git 제외)
├── .env.example             # 환경 변수 템플릿
├── credentials.json         # GCP 서비스 계정 키 (Git 제외)
├── usage_history.json       # API 사용 기록 (자동 생성)
├── requirements.txt         # Python 의존성
└── README.md                # 사용자 문서
```

---

## 핵심 컴포넌트

### 1. CLI Interface (`translate.py`)

**프레임워크**: Click

**명령어 구조**:
```
translate.py [OPTIONS] [COMMAND]
```

**주요 명령어**:
- `translate` (기본): PDF 파일/폴더 번역
- `stats`: 사용 현황 조회

**옵션**:
- `--input, -i`: 입력 파일/폴더 경로 (필수)
- `--output, -o`: 출력 폴더 경로 (기본값: ./output)
- `--source, -s`: 출발어 코드 (기본값: ja)
- `--target, -t`: 도착어 코드 (기본값: ko)
- `--batch, -b`: 폴더 일괄 처리 플래그

### 2. Translation Client (`translator/client.py`)

**클래스**: `TranslationClient`

**주요 메서드**:
```python
def __init__(self, project_id: str = None)
    # GCP 프로젝트 ID로 클라이언트 초기화
    # 환경 변수 GOOGLE_CLOUD_PROJECT 사용

def translate_document(
    file_path: str,
    target_language: str = "ko",
    source_language: str = "ja",
    mime_type: str = "application/pdf"
) -> Dict
    # PDF 문서를 통째로 번역
    # 반환값: {"document_content": bytes, "mime_type": str, "detected_language": str}
```

**API 사용**:
- `google.cloud.translate_v3.TranslationServiceClient`
- Location: `us-central1` (또는 `global`)
- Method: `translate_document()`

### 3. Utilities (`translator/utils.py`)

**주요 함수**:
```python
def save_translated_document(document_content: bytes, output_path: str) -> None
    # 번역된 PDF를 파일로 저장

def get_pdf_files(directory: str) -> List[str]
    # 디렉토리에서 PDF 파일 목록 가져오기

def format_file_size(size_bytes: int) -> str
    # 파일 크기를 사람이 읽기 쉬운 형식으로 변환 (B, KB, MB, GB)
```

### 4. Usage Tracker (`translator/usage.py`)

**클래스**: `UsageTracker`

**데이터 모델**:
```json
{
  "total_files": int,
  "total_cost_usd": float,
  "total_size_mb": float,
  "translations": [
    {
      "timestamp": "ISO-8601",
      "input_file": "filename.pdf",
      "output_file": "filename_ko.pdf",
      "source_lang": "ja",
      "target_lang": "ko",
      "file_size_mb": float,
      "estimated_cost_usd": float
    }
  ]
}
```

**주요 메서드**:
```python
def calculate_cost(file_size_bytes: int) -> float
    # 파일 크기 기반 비용 계산
    # 공식: 1MB ≈ 10페이지, 평균 $0.06/페이지

def add_translation(...) -> None
    # 번역 기록 추가 및 저장

def get_summary() -> Dict
    # 전체 사용 현황 요약

def get_monthly_summary(year: int, month: int) -> Dict
    # 월별 통계
```

---

## 환경 설정

### 필수 환경 변수 (.env)

```env
# GCP 서비스 계정 키 파일 경로 (필수)
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json

# GCP 프로젝트 ID (필수)
GOOGLE_CLOUD_PROJECT=your-project-id
```

### GCP 설정 요구사항

1. **프로젝트 생성**: Google Cloud Console에서 프로젝트 생성
2. **API 활성화**: Cloud Translation API 활성화
3. **서비스 계정**: 
   - 역할: "Cloud Translation API 사용자"
   - JSON 키 다운로드 → `credentials.json`으로 저장

---

## API 제한사항

### Document Translation API 제약

- **최대 파일 크기**: 10MB
- **최대 페이지 수**: 300페이지
- **지원 형식**: PDF, DOCX, PPTX, XLSX 등
- **Location**: `us-central1` 또는 `global`

### 비용 구조

- **문서 번역**: 페이지당 $0.075 (최초 500페이지/월)
- **초과분**: 페이지당 $0.045
- **무료 할당량**: 없음 (v3 Document Translation)

---

## 데이터 흐름

### 번역 프로세스

```
1. 사용자 입력
   ↓
2. validate_credentials() - GCP 인증 확인
   ↓
3. TranslationClient 초기화
   ↓
4. 파일 목록 가져오기 (단일/배치)
   ↓
5. 각 파일별로:
   a. translate_document() - API 호출
   b. save_translated_document() - 결과 저장
   c. tracker.add_translation() - 사용 기록 저장
   ↓
6. 통계 출력 (개별 비용 + 누적 통계)
```

### 통계 조회 프로세스

```
1. UsageTracker 초기화
   ↓
2. usage_history.json 로드
   ↓
3. 요청에 따라:
   - 전체 요약 (get_summary)
   - 상세 내역 (get_recent_translations)
   - 월별 통계 (get_monthly_summary)
   ↓
4. 포맷된 결과 출력
```

---

## 에러 처리

### 인증 관련

- `GOOGLE_APPLICATION_CREDENTIALS` 미설정 → 사용자에게 .env 설정 안내
- `credentials.json` 파일 없음 → GCP Console에서 키 다운로드 안내
- `GOOGLE_CLOUD_PROJECT` 미설정 → 프로젝트 ID 설정 요청

### 파일 처리 관련

- PDF 아닌 파일 → "PDF만 지원" 메시지
- 파일 없음 → 경로 확인 요청
- 10MB 초과 파일 → 경고 표시 (처리는 진행)

### API 관련

- API 비활성화 → API 활성화 안내
- 할당량 초과 → 할당량 확인 요청
- 네트워크 오류 → 연결 확인 요청

---

## 출력 형식

### 번역 진행 중

```
============================================================
🌏 PDF Translator (Document Translation API)
============================================================
📁 입력: ./docs/ (3개 파일)
📂 출력: ./output
🌐 번역: 日本語 → 한국어
============================================================

[1/3] 📄 document1.pdf
   📊 파일 크기: 2.1 MB
   🌐 문서 번역 중... ✓
   💾 파일 저장 중... ✓ (2.3 MB)
   → ./output/document1_ko.pdf
   💰 예상 비용: $1.26
```

### 통계 출력

```
============================================================
📊 PDF Translator - 사용 현황
============================================================
📄 총 번역 파일: 15개
📦 총 처리 용량: 42.5 MB
💰 누적 예상 비용: $25.50 USD
============================================================
```

---

## 확장 가능성

### 향후 추가 기능 아이디어

1. **다중 출력 형식**: DOCX, TXT 변환 지원
2. **병렬 처리**: 여러 파일 동시 번역
3. **진행률 표시**: tqdm 등으로 상세 진행률
4. **클라우드 스토리지**: GCS 버킷에서 직접 읽기/쓰기
5. **웹 인터페이스**: Flask/FastAPI 기반 웹 UI
6. **캐싱**: 동일 파일 재번역 방지
7. **커스텀 용어집**: Translation API glossary 기능 활용

---

## 테스트 시나리오

### 기본 테스트

1. ✅ 단일 PDF 파일 번역
2. ✅ 폴더 일괄 번역 (--batch)
3. ✅ 언어 지정 (--source, --target)
4. ✅ 사용 현황 조회 (stats)
5. ✅ 월별 통계 조회 (stats --month)

### 에러 케이스

1. ✅ 인증 정보 없음
2. ✅ 잘못된 파일 경로
3. ✅ PDF가 아닌 파일
4. ✅ API 할당량 초과 (모의)
5. ✅ 10MB 초과 파일

---

## 버전 히스토리

### v2.0.0 (Current)
- ✅ Document Translation API (v3) 사용
- ✅ PDF 통째로 번역 (레이아웃 유지)
- ✅ 사용 현황 추적 및 비용 계산
- ✅ Click 기반 CLI 인터페이스
- ✅ stats 명령어 추가

### v1.0.0 (Deprecated)
- ❌ Text Translation API (v2) 사용
- ❌ 텍스트 추출 → 번역 → PDF 재생성
- ❌ 레이아웃 손실 문제
