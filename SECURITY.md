# Security Guidelines

This document outlines security best practices for committing code to version control and deploying the PDF translation CLI.


## Overview

This project handles sensitive information including Google Cloud credentials, API keys, and potentially confidential documents. Proper security measures are essential to prevent unauthorized access and data exposure.


## Critical Files to Exclude

### Google Cloud Credentials

**Files**: `credentials.json`, `.credentials.json`, `*credentials*.json`, `service-account*.json`

Never commit Google Cloud service account keys. These files grant access to your GCP project and can incur charges if misused.

**Verification**:
```bash
git check-ignore credentials.json
git ls-files | grep credentials
```

### Environment Configuration

**File**: `.env`

Contains environment-specific configuration including:
```env
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
GOOGLE_CLOUD_PROJECT=your-project-id
```

Use `.env.example` as a template for documentation purposes only.

### Usage History

**File**: `usage_history.json`

Tracks API usage with metadata that may include:
- File paths and names
- Usage timestamps
- Cost information
- Translation patterns

This data may expose business intelligence or internal workflows.

### Document Files

**Locations**: `docs/`, `output/`, `*.pdf`

PDF files may contain:
- Proprietary information
- Personal data
- Copyrighted content

These should remain local only.


## Safe Files to Commit

The following files contain no sensitive information and should be included in version control:

- Source code: `translate.py`, `translator/*.py`
- Configuration templates: `.env.example`, `requirements.txt`
- Documentation: `README.md`, `TECHNICAL_SPEC.md`, `RULES.md`, `SKILLS.md`
- Git configuration: `.gitignore`

## Pre-Commit Checklist

Before committing or pushing code, verify:

### 1. Check Git Status

```bash
git status
```

Ensure no sensitive files appear in untracked or staged changes.

### 2. Verify .gitignore Rules

```bash
git check-ignore -v .env credentials.json usage_history.json output/
```

Each file should show the corresponding `.gitignore` rule.

### 3. Scan for Hardcoded Secrets

```bash
grep -r "AKIA\|AIza\|password\|secret\|api_key" --include="*.py" .
```

Verify that no credentials or API keys are hardcoded in source files.

### 4. Review Staged Files

```bash
git diff --cached --name-only
```

Confirm that only appropriate files are staged for commit.


## Secure Coding Patterns

### Correct: Environment Variables

```python
import os
from dotenv import load_dotenv

load_dotenv()
credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
```

### Incorrect: Hardcoded Values

```python
# DO NOT DO THIS
PROJECT_ID = "my-project-12345"
CREDENTIALS = "./my-secret-key.json"
API_KEY = "AIzaSyABC123..."
```


## Incident Response

If sensitive information has been committed:

### Local Repository Only (Not Pushed)

```bash
# Reset the last commit (keep changes)
git reset --soft HEAD~1

# Remove sensitive files from staging
git rm --cached .env credentials.json

# Recommit without sensitive files
git commit -m "Your commit message"
```

### Already Pushed to Remote

**Immediate Actions**:

1. **Revoke compromised credentials**:
   - Navigate to Google Cloud Console → IAM & Admin → Service Accounts
   - Delete the exposed key
   - Generate a new service account key

2. **Remove from Git history**:
   ```bash
   # Using git-filter-repo (recommended)
   git filter-repo --invert-paths --path credentials.json
   
   # Force push (coordinate with team)
   git push --force
   ```

3. **Notify team members** to pull fresh history:
   ```bash
   git fetch --all
   git reset --hard origin/main
   ```


## Additional Security Measures

### Pre-Commit Hooks (Optional)

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# Check for sensitive files
if git diff --cached --name-only | grep -qE "(\.env|credentials\.json|usage_history\.json)"; then
    echo "ERROR: Sensitive file detected in commit"
    git diff --cached --name-only | grep -E "(\.env|credentials\.json|usage_history\.json)"
    exit 1
fi

# Check for hardcoded secrets
if git diff --cached | grep -qE "(AKIA|AIza|sk-|password\s*=)"; then
    echo "ERROR: Potential secret detected in commit"
    exit 1
fi

exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### Git Secrets Tool

Install and configure [git-secrets](https://github.com/awslabs/git-secrets):

```bash
# Install (macOS)
brew install git-secrets

# Configure for repository
git secrets --install
git secrets --register-aws
```

### GitHub Secret Scanning

For public repositories, enable GitHub's secret scanning:
1. Navigate to repository Settings
2. Go to Code security and analysis
3. Enable "Secret scanning" and "Push protection"


## Current Security Status

This project implements the following security measures:

- Comprehensive `.gitignore` covering all sensitive files
- Environment variable-based configuration
- Template file (`.env.example`) for setup documentation
- No hardcoded credentials or secrets in source code
- Security documentation and guidelines

**Status**: Ready for version control


## Quick Reference

**Before first commit**:
```bash
git status
git check-ignore .env credentials.json usage_history.json
```

**Before each commit**:
```bash
git diff --cached --name-only
git diff --cached | grep -i "password\|secret\|key"
```

**Emergency credential revocation**:
- Google Cloud Console → IAM → Service Accounts → Delete Key
- Generate new credentials
- Update local `.env` file


## Additional Resources

- [Google Cloud Security Best Practices](https://cloud.google.com/security/best-practices)
- [Git Security Documentation](https://git-scm.com/book/en/v2/Git-Tools-Credential-Storage)
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
