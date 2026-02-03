# PDF Translator 🌏

[한국어](README_ko.md) | English | [日本語](README_ja.md)

A CLI program for translating PDF documents using Google Cloud Translation API v3 **Document Translation**.

## Key Features

- **Direct Document Translation**: Translate PDFs directly without text extraction
- **Layout Preservation**: Perfectly preserves the original PDF layout and format
- **High-Quality Translation**: Uses Google Cloud Translation API v3 document translation feature
- **Single/Batch Processing**: Translate a single file or all PDFs in a folder
- **Multiple Language Support**: Supports over 100 languages
- **Usage Tracking**: Automatically saves and displays API usage and costs locally

## Installation

### 1. Install Python Packages

```bash
pip install -r requirements.txt
```

### 2. Google Cloud Setup

#### 2.1 Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note the project ID

#### 2.2 Enable Translation API
1. Navigate to "APIs & Services" > "Library"
2. Search for "Cloud Translation API"
3. Click "Enable"

#### 2.3 Create Service Account and Download Key
1. Navigate to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Enter a name (e.g., pdf-translator)
4. Select role: "Cloud Translation API User"
5. Click on the created service account → "Keys" tab → "Add Key" → Select "JSON"
6. Save the downloaded JSON file as `credentials.json` in your project folder

### 3. Configure Environment Variables

Copy the `.env.example` file to create a `.env` file:

```bash
cp .env.example .env
```

Edit the `.env` file:

```env
# Path to the downloaded service account key file
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json

# Google Cloud Project ID (check in Console)
GOOGLE_CLOUD_PROJECT=your-project-id
```

## Usage

### Basic Usage

```bash
# Translate a single file (default: Japanese → Korean)
python translate.py -i ./document.pdf

# Specify output folder
python translate.py -i ./document.pdf -o ./translated/

# Batch translate all PDFs in a folder
python translate.py -i ./docs/ -o ./output/ --batch

# Specify languages (English → Korean)
python translate.py -i ./english.pdf -s en -t ko
```

### Command Options

| Option | Short | Required | Default | Description |
|--------|-------|----------|---------|-------------|
| `--input` | `-i` | Y | - | Input PDF file or folder path |
| `--output` | `-o` | N | `./output` | Output folder path |
| `--source` | `-s` | N | `ja` | Source language code (ja, en, ko, etc.) |
| `--target` | `-t` | N | `ko` | Target language code |
| `--batch` | `-b` | N | `False` | Batch processing mode |

### Supported Language Codes

- `ja` - 日本語 (Japanese)
- `ko` - 한국어 (Korean)
- `en` - English
- `zh` - 中文 (Chinese)
- `es` - Español (Spanish)
- `fr` - Français (French)
- `de` - Deutsch (German)
- [Full language list](https://cloud.google.com/translate/docs/languages)

## Usage Examples

### Example 1: Translate a Single File

```bash
python translate.py -i ./目論見書.pdf -o ./output/
```

Output:
```
============================================================
🌏 PDF Translator (Document Translation API)
============================================================
📁 Input: ./目論見書.pdf (1 file)
📂 Output: ./output
🌐 Translation: 日本語 → Korean
============================================================

[1/1] 📄 目論見書.pdf
   📊 File size: 2.1 MB
   🌐 Translating document... ✓
   💾 Saving file... ✓ (2.3 MB)
   → ./output/目論見書_ko.pdf

============================================================
✅ Complete! Successfully translated 1 file
============================================================
```

### Example 2: Batch Translate Folder Recursively (Japanese → Korean)

```bash
python translate.py -i ./docs/ -o ./output/ --recursive -s ja -t ko
```

### Example 3: Translate File in Subfolder (uses default: Japanese → Korean)

```bash
python translate.py -i "./docs/キャピタル世界株式ファンド (分配金再投資)/jp-ark-gef.pdf"
```

### Example 4: Check Usage Statistics

```bash
# Summary
python translate.py stats

# Detailed history (last 10 records)
python translate.py stats --detail

# Monthly statistics
python translate.py stats --month 2

# Specific month and year statistics
python translate.py stats --month 1 --year 2026
```

Output:
```
============================================================
📊 PDF Translator - Usage Statistics
============================================================
📄 Total files translated: 15
📦 Total data processed: 42.5 MB
💰 Cumulative estimated cost: $25.50 USD
============================================================

💡 For detailed history: python translate.py stats --detail
```

## Project Structure

```
pdf-translator/
├── translate.py              # Main CLI script
├── translator/
│   ├── __init__.py          # Package initialization
│   ├── client.py            # Google Cloud Translation client
│   ├── utils.py             # PDF processing utilities
│   └── usage.py             # Usage tracking
├── requirements.txt         # Python package dependencies
├── .env.example            # Environment variable template
├── .env                    # Environment variables (needs to be created)
├── credentials.json        # Google Cloud service account key (needs to be created)
├── usage_history.json      # API usage records (auto-generated)
└── README.md               # This file
```

## Usage Tracking

The program automatically records all translation tasks in the `usage_history.json` file.

### Tracked Information

- Translation date and time
- Input/output file names
- Source/target languages
- File size
- Estimated cost

### Usage Statistics Commands

```bash
# Summary
python translate.py stats

# View detailed history
python translate.py stats --detail

# Monthly statistics
python translate.py stats --month 2 --year 2026

# Clear usage history (caution!)
python translate.py stats --clear
```

## Pricing

Google Cloud Translation API v3 Document Translation pricing:

- **Free Tier**: None (only v2 text translation offers 500,000 characters/month free)
- **Document Translation Cost**: 
  - $0.075 per page (first 500 pages/month)
  - $0.045 per page (over 500 pages)
- **Example**: 30-page PDF → approximately $2.25

For more details, see [Google Cloud Translation Pricing](https://cloud.google.com/translate/pricing).

## Document Translation vs Text Translation

| Feature | Document Translation (v3) | Text Translation (v2) |
|---------|---------------------------|------------------------|
| **Input** | PDF/DOCX files | Text strings |
| **Layout** | Fully preserved | Lost |
| **Format** | Fully preserved (fonts, images, etc.) | Lost |
| **Translation Quality** | Context-based, high quality | Basic quality |
| **Pricing** | Per page | Per character |
| **Free Tier** | None | 500,000 characters/month |

**This program uses Document Translation.**

## Troubleshooting

### Authentication Error

```
❌ Error: GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.
```

**Solution**: Create a `.env` file and correctly set the `GOOGLE_APPLICATION_CREDENTIALS` path.

### Project ID Error

```
❌ Error: GOOGLE_CLOUD_PROJECT environment variable is not set.
```

**Solution**: Correctly set `GOOGLE_CLOUD_PROJECT` in the `.env` file.

### API Activation Error

```
❌ Error: Translation API is not enabled.
```

**Solution**: Enable the Cloud Translation API in Google Cloud Console.

### File Size Limits

Document Translation API has file size limitations:
- **Maximum file size**: 10MB
- **Maximum pages**: 300 pages

Split large files for processing.

### Quota Exceeded

```
❌ Error: API quota exceeded.
```

**Solution**: 
- Check quota in Google Cloud Console
- Ensure billing account is activated
- Request quota increase

## License

MIT License

## Contributing

Issues and pull requests are always welcome!

## Support

If you encounter any problems, please create an issue on GitHub.
