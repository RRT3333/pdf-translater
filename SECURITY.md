# PDF Translator - Security Checklist

이 문서는 Git에 코드를 푸시하기 전에 확인해야 할 보안 체크리스트입니다.

---

## ✅ Git 커밋 전 필수 체크리스트

### 1. 민감한 파일 확인

**절대 커밋하면 안 되는 파일들**:

```bash
# 확인 명령어
git status
git check-ignore .env credentials.json usage_history.json
```

- [ ] `.env` - 환경 변수 파일
- [ ] `credentials.json` - GCP 서비스 계정 키
- [ ] `.credentials.json` - GCP 서비스 계정 키 (다른 이름)
- [ ] `*credentials*.json` - credentials가 포함된 모든 JSON 파일
- [ ] `usage_history.json` - API 사용 기록 (파일명 등 개인정보 포함)
- [ ] `output/` - 번역된 파일들 (개인 문서)
- [ ] `docs/` - 원본 PDF 파일들 (개인 문서)
- [ ] `*.pdf` - 모든 PDF 파일

### 2. .gitignore 확인

**현재 .gitignore에 포함된 항목**:

```gitignore
# 환경 설정
.env
.venv
venv/

# GCP 인증 (보안 중요!)
.credentials.json
credentials.json
*credentials*.json

# API 사용 기록 (개인 정보)
usage_history.json
*_history.json

# 프로젝트 파일 (개인 문서)
docs/
output/
*.pdf

# Python
__pycache__/
*.pyc
venv/

# IDE
.vscode/
```

**확인 방법**:
```bash
# .gitignore가 제대로 작동하는지 확인
git check-ignore .env credentials.json usage_history.json

# 추적되지 않는 파일 확인
git status --ignored
```

---

## 🔍 코드 스캔 체크리스트

### 3. 하드코딩된 비밀 정보 검색

```bash
# 민감한 정보 패턴 검색
grep -r "AKIA" .                    # AWS 키
grep -r "AIza" .                    # Google API 키
grep -r "sk-" .                     # OpenAI 키
grep -r "@gmail.com" .              # 이메일
grep -r "password.*=.*\"" .         # 하드코딩된 비밀번호
grep -r "secret.*=.*\"" .           # 하드코딩된 시크릿
```

**PowerShell에서**:
```powershell
# 민감한 정보 검색
Select-String -Path *.py -Pattern "AKIA|AIza|sk-|password.*=|secret.*=" -AllMatches
```

### 4. 환경 변수 사용 확인

**✅ 올바른 패턴**:
```python
# Good - 환경 변수 사용
credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
```

**❌ 위험한 패턴**:
```python
# Bad - 하드코딩
PROJECT_ID = "my-project-12345"
CREDENTIALS = "./my-secret-key.json"
API_KEY = "AIzaSyABC123..."
```

---

## 📋 커밋 전 단계별 가이드

### Step 1: 파일 상태 확인

```bash
git status
```

**확인 사항**:
- [ ] `.env` 파일이 표시되지 않는가?
- [ ] `credentials.json` 파일이 표시되지 않는가?
- [ ] `usage_history.json` 파일이 표시되지 않는가?
- [ ] `output/` 폴더가 표시되지 않는가?

### Step 2: 추적 중인 민감한 파일 확인

```bash
# 이미 추적 중인 파일 목록
git ls-files

# 민감한 파일이 포함되어 있는지 확인
git ls-files | grep -E "(\.env|credentials|usage_history)"
```

**만약 민감한 파일이 이미 추적 중이라면**:
```bash
# Git 추적에서 제거 (파일은 유지)
git rm --cached .env
git rm --cached credentials.json
git rm --cached usage_history.json

# 커밋
git commit -m "Remove sensitive files from tracking"
```

### Step 3: .gitignore 테스트

```bash
# 각 민감한 파일이 무시되는지 확인
git check-ignore -v .env
git check-ignore -v credentials.json
git check-ignore -v .credentials.json
git check-ignore -v usage_history.json
git check-ignore -v output/
```

**예상 출력**:
```
.gitignore:XX:.env                    .env
.gitignore:XX:credentials.json        credentials.json
.gitignore:XX:usage_history.json      usage_history.json
```

### Step 4: 코드 검토

```bash
# Python 파일에서 의심스러운 패턴 검색
grep -r "password\|secret\|api_key\|token" --include="*.py" .
```

**확인 사항**:
- [ ] 하드코딩된 API 키가 없는가?
- [ ] 하드코딩된 경로가 없는가? (예: `C:\Users\myname\...`)
- [ ] 개인 식별 정보가 없는가?

### Step 5: 안전한 커밋

```bash
# 변경사항 스테이징
git add .

# 스테이징된 파일 확인
git diff --cached --name-only

# 민감한 파일이 없는지 최종 확인
git diff --cached --name-only | grep -E "(\.env|credentials|usage_history|\.pdf)"

# 커밋
git commit -m "Add PDF translation CLI"

# 푸시 전 마지막 확인
git log -1 --stat
```

---

## 🚨 긴급: 민감한 정보를 이미 커밋한 경우

### 로컬에만 커밋하고 푸시 안 한 경우

```bash
# 마지막 커밋 취소 (변경사항은 유지)
git reset --soft HEAD~1

# 민감한 파일 제거
git rm --cached .env credentials.json

# .gitignore 업데이트 후 다시 커밋
git add .gitignore
git commit -m "Update .gitignore"
```

### 이미 푸시한 경우 (매우 위험!)

**⚠️ 즉시 조치 필요**:

1. **GCP 콘솔에서 즉시 키 폐기**:
   - Google Cloud Console → IAM → 서비스 계정
   - 해당 키 삭제 및 새 키 생성

2. **Git 히스토리에서 완전 제거** (BFG Cleaner 사용):
   ```bash
   # BFG 다운로드
   # https://rtyley.github.io/bfg-repo-cleaner/
   
   # 민감한 파일 제거
   java -jar bfg.jar --delete-files credentials.json
   java -jar bfg.jar --delete-files .env
   
   # Git 정리
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   
   # 강제 푸시 (주의!)
   git push --force
   ```

3. **팀원들에게 알림**:
   ```bash
   # 팀원들이 실행해야 할 명령어
   git fetch --all
   git reset --hard origin/main
   ```

---

## 🛡️ 추가 보안 권장사항

### 1. Pre-commit Hook 설정

`.git/hooks/pre-commit` 파일 생성:

```bash
#!/bin/bash

# 민감한 파일 체크
if git diff --cached --name-only | grep -qE "(\.env|credentials\.json|usage_history\.json)"; then
    echo "❌ 오류: 민감한 파일이 커밋에 포함되어 있습니다!"
    echo "다음 파일을 확인하세요:"
    git diff --cached --name-only | grep -E "(\.env|credentials\.json|usage_history\.json)"
    exit 1
fi

# 하드코딩된 비밀 정보 체크
if git diff --cached --name-only | xargs grep -l "AKIA\|AIza\|sk-\|password.*=.*\"" 2>/dev/null; then
    echo "❌ 오류: 하드코딩된 비밀 정보가 감지되었습니다!"
    exit 1
fi

exit 0
```

**실행 권한 부여**:
```bash
chmod +x .git/hooks/pre-commit
```

### 2. Git Secrets 설치

```bash
# macOS
brew install git-secrets

# Windows (Git Bash)
git clone https://github.com/awslabs/git-secrets.git
cd git-secrets
./install.sh

# 설정
cd /path/to/your/repo
git secrets --install
git secrets --register-aws
```

### 3. GitHub Secret Scanning 활성화

**GitHub 저장소 설정**:
1. Settings → Code security and analysis
2. "Secret scanning" 활성화
3. "Push protection" 활성화

### 4. .env.example 제공

**절대 커밋하지 않기**:
- ❌ `.env`

**항상 커밋하기**:
- ✅ `.env.example` (실제 값 없이 템플릿만)

```env
# .env.example
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
GOOGLE_CLOUD_PROJECT=your-project-id
```

### 5. README에 보안 안내 추가

```markdown
## ⚠️ 보안 주의사항

이 프로젝트를 사용하기 전에:

1. ✅ `.env` 파일을 절대 커밋하지 마세요
2. ✅ `credentials.json`을 절대 공유하지 마세요
3. ✅ 사용 후 서비스 계정 키를 안전하게 보관하세요
4. ✅ 불필요한 키는 GCP Console에서 삭제하세요
```

---

## 📊 보안 체크리스트 요약

| 항목 | 상태 | 비고 |
|------|------|------|
| `.gitignore` 설정 | ✅ | `.env`, `credentials.json` 포함 |
| 환경 변수 사용 | ✅ | 하드코딩 없음 |
| `.env.example` 제공 | ✅ | 템플릿만 포함 |
| 민감한 파일 미추적 | ⚠️ | `git status`로 확인 필요 |
| Pre-commit hook | ❌ | 권장 (선택사항) |
| Git Secrets | ❌ | 권장 (선택사항) |

---

## 🔐 커밋 직전 최종 점검 명령어

```bash
# 1단계: 상태 확인
git status

# 2단계: 민감한 파일이 무시되는지 확인
git check-ignore .env credentials.json usage_history.json

# 3단계: 커밋될 파일 확인
git diff --cached --name-only

# 4단계: 민감한 정보 검색
grep -r "AKIA\|AIza\|sk-\|password.*=" --include="*.py" .

# 5단계: 모두 통과하면 커밋
git add .
git commit -m "Your commit message"
```

---

## 📞 보안 사고 발생 시

1. **즉시 키 폐기**: GCP Console에서 서비스 계정 키 삭제
2. **새 키 발급**: 새 서비스 계정 및 키 생성
3. **Git 히스토리 정리**: BFG Cleaner 또는 git filter-branch 사용
4. **팀 공유**: 사고 발생 사실 공유 및 재설정 요청
5. **모니터링**: GCP 청구 및 로그 확인

---

## ✅ 이 프로젝트의 현재 보안 상태

- ✅ `.gitignore`에 모든 민감한 파일 포함
- ✅ 환경 변수로만 설정 관리
- ✅ `.env.example` 템플릿 제공
- ✅ 하드코딩된 비밀 정보 없음
- ✅ README에 보안 안내 포함
- ✅ 문서에 보안 규칙 명시

**현재 상태: 안전 ✅**

Git에 푸시해도 안전합니다!
