# PDF Translator CLI Tool

A command-line tool for translating PDF documents using Google Cloud Translation API v3 Document Translation. This tool preserves the original document layout and formatting.

## Prerequisites

- Python 3.8+
- Google Cloud Project with Translation API enabled
- Service account credentials JSON file
- Environment variables configured in `.env`:
  - `GOOGLE_APPLICATION_CREDENTIALS` - Path to credentials JSON
  - `GOOGLE_CLOUD_PROJECT` - Your GCP project ID

## Available Commands

### Translate Command (Default)

Translates PDF documents from source language to target language.

**Basic Usage:**
```bash
python translate.py -i <input> -o <output> [options]
```

**Options:**
- `-i, --input` - (Required) Input PDF file or folder path
- `-o, --output` - Output folder path (default: `./output`)
- `-s, --source` - Source language code (default: `ja` for Japanese, use empty string `""` for auto-detection)
- `-t, --target` - Target language code (default: `ko` for Korean)
- `-b, --batch` - Enable batch processing mode for folders
- `-r, --recursive` - Process folders recursively, preserving subfolder structure

**Supported Language Codes:**
- `ja` - Japanese (日本語)
- `ko` - Korean (한국어)
- `en` - English
- `zh` - Chinese (中文)
- `es` - Spanish (Español)
- `fr` - French (Français)
- `de` - German (Deutsch)
- `ru` - Russian (Русский)
- `ar` - Arabic (العربية)

**Examples:**

Translate a single PDF file:
```bash
python translate.py -i document.pdf -o output/
```

Translate with specific languages:
```bash
python translate.py -i document.pdf -s en -t ko -o output/
```

Auto-detect source language:
```bash
python translate.py -i document.pdf -s "" -t ko -o output/
```

Batch translate all PDFs in a folder:
```bash
python translate.py -i docs/ -o output/ --batch
```

Recursive translation (preserves folder structure):
```bash
python translate.py -i docs/ -o output/ --recursive
```

Translate from English to Korean (folder):
```bash
python translate.py -i docs/ -s en -t ko -o output/ --batch
```

### Stats Command

View usage statistics and translation history.

**Basic Usage:**
```bash
python translate.py stats [options]
```

**Options:**
- `-d, --detail` - Show detailed translation history (last 10 records)
- `--month` - View statistics for specific month (1-12)
- `--year` - Specify year (default: current year)
- `--clear` - Clear all usage history (irreversible)

**Examples:**

View summary statistics:
```bash
python translate.py stats
```

View detailed history:
```bash
python translate.py stats --detail
```

View current month statistics:
```bash
python translate.py stats --month 2
```

View specific year-month statistics:
```bash
python translate.py stats --month 2 --year 2026
```

Clear usage history:
```bash
python translate.py stats --clear
```

## Output

- **Translated PDFs**: Saved to the output directory
- **Naming Convention**: `{original_name}_{target_lang}.pdf`
- **Folder Structure**: 
  - Normal/batch mode: All files in output folder
  - Recursive mode: Preserves original folder structure

## Cost Estimation

The tool tracks estimated costs based on:
- File size → estimated page count (1MB ≈ 10 pages)
- Average rate: ~$0.06 per page
- Actual costs may vary based on Google Cloud pricing

## Usage History

Translation history is automatically saved to `usage_history.json`:
- Timestamp of each translation
- File information (name, size)
- Languages used
- Estimated cost
- Cumulative statistics

## Error Handling

The tool validates:
- ✅ Environment variables (credentials, project ID)
- ✅ File existence and permissions
- ✅ Folder paths for batch/recursive modes
- ✅ API authentication
- ✅ File format (PDF only)

## Notes

- Only PDF files are supported
- Large files (>10MB) will show a warning
- Empty source language (`-s ""`) enables auto-detection
- Recursive mode preserves the complete folder hierarchy
- All file operations are safe (creates directories automatically)
