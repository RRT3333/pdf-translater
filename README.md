# PDF Translator 🌏

Google Cloud Translation API v3 **Document Translation**을 사용하여 PDF 문서를 번역하는 CLI 프로그램입니다.

## 주요 특징

- ✅ **문서 통째로 번역**: 텍스트 추출 없이 PDF를 직접 번역
- ✅ **레이아웃 유지**: 원본 PDF의 레이아웃과 포맷 완벽 보존
- ✅ **고품질 번역**: Google Cloud Translation API v3의 문서 번역 기능 사용
- ✅ **단일/일괄 처리**: 파일 하나 또는 폴더 내 모든 PDF 번역
- ✅ **다양한 언어 지원**: 100개 이상의 언어 지원
- ✅ **사용 현황 추적**: API 사용량과 비용을 로컬에 자동 저장 및 조회

## 설치 방법

### 1. Python 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. Google Cloud 설정

#### 2.1 Google Cloud 프로젝트 생성
1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. 프로젝트 ID 확인

#### 2.2 Translation API 활성화
1. "API 및 서비스" > "라이브러리" 이동
2. "Cloud Translation API" 검색
3. "사용 설정" 클릭

#### 2.3 서비스 계정 생성 및 키 다운로드
1. "IAM 및 관리자" > "서비스 계정" 이동
2. "서비스 계정 만들기" 클릭
3. 이름 입력 (예: pdf-translator)
4. 역할 선택: "Cloud Translation API 사용자"
5. 생성된 서비스 계정 클릭 → "키" 탭 → "키 추가" → "JSON" 선택
6. 다운로드된 JSON 파일을 프로젝트 폴더에 `credentials.json`으로 저장

### 3. 환경 변수 설정

`.env.example` 파일을 복사하여 `.env` 파일 생성:

```bash
cp .env.example .env
```

`.env` 파일 내용 수정:

```env
# 다운로드한 서비스 계정 키 파일 경로
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json

# Google Cloud 프로젝트 ID (Console에서 확인)
GOOGLE_CLOUD_PROJECT=your-project-id
```

## 사용 방법

### 기본 사용법

```bash
# 단일 파일 번역
python translate.py -i ./document.pdf

# 출력 폴더 지정
python translate.py -i ./document.pdf -o ./translated/

# 폴더 내 모든 PDF 일괄 번역
python translate.py -i ./docs/ -o ./output/ --batch

# 언어 지정 (영어 → 한국어)
python translate.py -i ./english.pdf -s en -t ko
```

### 명령어 옵션

| 옵션 | 단축 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| `--input` | `-i` | ✅ | - | 입력 PDF 파일 또는 폴더 경로 |
| `--output` | `-o` | ❌ | `./output` | 출력 폴더 경로 |
| `--source` | `-s` | ❌ | `ja` | 출발어 코드 (ja, en, ko 등) |
| `--target` | `-t` | ❌ | `ko` | 도착어 코드 |
| `--batch` | `-b` | ❌ | `False` | 폴더 일괄 처리 모드 |

### 지원 언어 코드

- `ja` - 日本語 (일본어)
- `ko` - 한국어
- `en` - English (영어)
- `zh` - 中文 (중국어)
- `es` - Español (스페인어)
- `fr` - Français (프랑스어)
- `de` - Deutsch (독일어)
- [전체 언어 목록](https://cloud.google.com/translate/docs/languages)

## 사용 예시

### 예시 1: 단일 파일 번역

```bash
python translate.py -i ./目論見書.pdf -o ./output/
```

출력:
```
============================================================
🌏 PDF Translator (Document Translation API)
============================================================
📁 입력: ./目論見書.pdf (1개 파일)
📂 출력: ./output
🌐 번역: 日本語 → 한국어
============================================================

[1/1] 📄 目論見書.pdf
   📊 파일 크기: 2.1 MB
   🌐 문서 번역 중... ✓
   💾 파일 저장 중... ✓ (2.3 MB)
   → ./output/目論見書_ko.pdf

============================================================
✅ 완료! 총 1개 파일 번역 성공
============================================================
```

### 예시 2: 폴더 일괄 번역

```bash
python translate.py -i ./documents/ -o ./translated/ --batch
```

### 예시 3: 영어 → 한국어 번역

```bash
python translate.py -i ./english_doc.pdf -s en -t ko
```

### 예시 4: 사용 현황 조회

```bash
# 전체 요약
python translate.py stats

# 상세 내역 (최근 10건)
python translate.py stats --detail

# 이번 달 통계
python translate.py stats --month 2

# 특정 년월 통계
python translate.py stats --month 1 --year 2026
```

출력:
```
============================================================
📊 PDF Translator - 사용 현황
============================================================
📄 총 번역 파일: 15개
📦 총 처리 용량: 42.5 MB
💰 누적 예상 비용: $25.50 USD
============================================================

💡 상세 내역을 보려면: python translate.py stats --detail
```

## 프로젝트 구조

```
pdf-translator/
├── translate.py              # 메인 CLI 스크립트
├── translator/
│   ├── __init__.py          # 패키지 초기화
│   ├── client.py            # Google Cloud Translation 클라이언트
│   ├── utils.py             # PDF 처리 유틸리티
│   └── usage.py             # 사용 현황 추적
├── requirements.txt         # Python 패키지 의존성
├── .env.example            # 환경 변수 템플릿
├── .env                    # 환경 변수 (생성 필요)
├── credentials.json        # Google Cloud 서비스 계정 키 (생성 필요)
├── usage_history.json      # API 사용 기록 (자동 생성)
└── README.md               # 이 파일
```

## 사용 현황 추적

프로그램은 모든 번역 작업을 `usage_history.json` 파일에 자동으로 기록합니다.

### 추적되는 정보

- 번역 날짜 및 시간
- 입력/출력 파일명
- 출발어/도착어
- 파일 크기
- 예상 비용

### 사용 현황 조회 명령어

```bash
# 전체 요약
python translate.py stats

# 상세 내역 보기
python translate.py stats --detail

# 월별 통계
python translate.py stats --month 2 --year 2026

# 사용 기록 초기화 (주의!)
python translate.py stats --clear
```

## 비용 안내

Google Cloud Translation API v3 Document Translation 비용:

- **무료 할당량**: 없음 (v2 텍스트 번역만 월 500,000자 무료)
- **문서 번역 비용**: 
  - 페이지당 $0.075 (최초 500페이지/월)
  - 페이지당 $0.045 (500페이지 초과분)
- **예시**: 30페이지 PDF → 약 $2.25

자세한 내용은 [Google Cloud Translation 가격 정책](https://cloud.google.com/translate/pricing)을 참조하세요.

## Document Translation vs Text Translation 비교

| 특징 | Document Translation (v3) | Text Translation (v2) |
|------|---------------------------|------------------------|
| **입력** | PDF/DOCX 파일 | 텍스트 문자열 |
| **레이아웃** | 완벽 유지 | 손실 |
| **포맷** | 완벽 유지 (폰트, 이미지 등) | 손실 |
| **번역 품질** | 문맥 기반, 고품질 | 기본 품질 |
| **비용** | 페이지당 과금 | 문자당 과금 |
| **무료 할당** | 없음 | 월 500,000자 |

**이 프로그램은 Document Translation을 사용합니다.**

## 문제 해결

### 인증 오류

```
❌ 오류: GOOGLE_APPLICATION_CREDENTIALS 환경 변수가 설정되지 않았습니다.
```

**해결 방법**: `.env` 파일을 생성하고 `GOOGLE_APPLICATION_CREDENTIALS` 경로를 올바르게 설정하세요.

### 프로젝트 ID 오류

```
❌ 오류: GOOGLE_CLOUD_PROJECT 환경 변수가 설정되지 않았습니다.
```

**해결 방법**: `.env` 파일에 `GOOGLE_CLOUD_PROJECT`를 올바르게 설정하세요.

### API 활성화 오류

```
❌ 오류: Translation API가 활성화되지 않았습니다.
```

**해결 방법**: Google Cloud Console에서 Cloud Translation API를 활성화하세요.

### 파일 크기 제한

Document Translation API는 파일 크기 제한이 있습니다:
- **최대 파일 크기**: 10MB
- **최대 페이지 수**: 300페이지

큰 파일은 분할하여 처리하세요.

### 할당량 초과

```
❌ 오류: API 할당량을 초과했습니다.
```

**해결 방법**: 
- Google Cloud Console에서 할당량 확인
- 결제 계정이 활성화되어 있는지 확인
- 할당량 증가 요청

## 라이선스

MIT License

## 기여

이슈나 풀 리퀘스트는 언제든 환영합니다!

## 지원

문제가 발생하면 GitHub Issues에 등록해주세요.
