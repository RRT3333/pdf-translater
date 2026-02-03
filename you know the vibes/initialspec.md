## Google Cloud Translation PDF 번역 CLI - Spec Sheet

### 개요
일본어 PDF 문서를 한국어로 번역하는 CLI 프로그램

---

### 기술 스택
- **언어:** Python 3.10+
- **주요 라이브러리:**
  - `google-cloud-translate` - Google Cloud Translation API
  - `click` 또는 `argparse` - CLI 인터페이스
  - `python-dotenv` - 환경변수 관리

---

### 기능 요구사항

| 기능 | 설명 |
|------|------|
| 단일 파일 번역 | PDF 파일 1개 번역 |
| 폴더 일괄 번역 | 지정 폴더 내 모든 PDF 번역 |
| 언어 설정 | 출발어/도착어 지정 (기본값: ja → ko) |
| 출력 경로 | 번역된 PDF 저장 위치 지정 |
| 진행 상황 표시 | 번역 진행률 출력 |

---

### CLI 인터페이스

```bash
# 단일 파일 번역
python translate.py --input ./docs/目論見書.pdf --output ./output/

# 폴더 일괄 번역
python translate.py --input ./docs/ --output ./output/ --batch

# 언어 지정 (기본값: ja → ko)
python translate.py --input ./docs/ --output ./output/ --source ja --target ko
```

---

### 명령어 옵션

| 옵션 | 단축 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| `--input` | `-i` | O | - | 입력 파일 또는 폴더 경로 |
| `--output` | `-o` | X | `./output` | 출력 폴더 경로 |
| `--source` | `-s` | X | `ja` | 출발어 코드 |
| `--target` | `-t` | X | `ko` | 도착어 코드 |
| `--batch` | `-b` | X | `False` | 폴더 일괄 처리 모드 |

---

### 환경 설정

```
# .env 파일
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
GOOGLE_CLOUD_PROJECT=your-project-id
```

---

### 폴더 구조

```
pdf-translator/
├── translate.py        # 메인 CLI
├── translator/
│   ├── __init__.py
│   ├── client.py       # Google Cloud Translation 클라이언트
│   └── utils.py        # 유틸리티 함수
├── .env.example
├── requirements.txt
└── README.md
```

---

### requirements.txt

```
google-cloud-translate>=3.0.0
click>=8.0.0
python-dotenv>=1.0.0
```

---

### 출력 예시

```
$ python translate.py -i ./docs/ -o ./output/ --batch

[PDF Translator] 시작
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
입력: ./docs/ (6개 파일)
출력: ./output/
번역: 日本語 → 한국어
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1/6] 目論見書_キャピタル世界株式.pdf
      30 페이지 | 번역 중... ████████████ 100%
      → output/目論見書_キャピタル世界株式_ko.pdf

[2/6] 月次レポート_キャピタル世界株式.pdf
      5 페이지 | 번역 중... ████████████ 100%
      → output/月次レポート_キャピタル世界株式_ko.pdf

...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
완료! 총 6개 파일 | 210 페이지 | 예상 비용: $16.80
```

---

### 에러 처리

| 에러 | 처리 |
|------|------|
| 인증 실패 | credentials.json 경로 확인 메시지 |
| 파일 없음 | 입력 경로 확인 메시지 |
| API 할당량 초과 | 대기 후 재시도 또는 중단 |
| 지원하지 않는 형식 | PDF만 지원한다는 메시지 |