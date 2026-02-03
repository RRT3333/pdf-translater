# PDF Translator 🌏

[한국어](README_ko.md) | [English](README.md) | 日本語

Google Cloud Translation API v3 **Document Translation**を使用してPDFドキュメントを翻訳するCLIプログラムです。

## 主な機能

- **ドキュメント全体の翻訳**: テキスト抽出なしでPDFを直接翻訳
- **レイアウト保持**: 元のPDFのレイアウトとフォーマットを完全に保存
- **高品質翻訳**: Google Cloud Translation API v3のドキュメント翻訳機能を使用
- **単一/一括処理**: 単一ファイルまたはフォルダ内のすべてのPDFを翻訳
- **多言語サポート**: 100以上の言語をサポート
- **使用状況の追跡**: API使用量とコストをローカルに自動保存および表示

## インストール方法

### 1. Pythonパッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. Google Cloudの設定

#### 2.1 Google Cloudプロジェクトの作成
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成するか、既存のプロジェクトを選択
3. プロジェクトIDを確認

#### 2.2 Translation APIの有効化
1. 「APIとサービス」>「ライブラリ」に移動
2. 「Cloud Translation API」を検索
3. 「有効にする」をクリック

#### 2.3 サービスアカウントの作成とキーのダウンロード
1. 「IAMと管理」>「サービスアカウント」に移動
2. 「サービスアカウントを作成」をクリック
3. 名前を入力（例：pdf-translator）
4. 役割を選択：「Cloud Translation API ユーザー」
5. 作成されたサービスアカウントをクリック→「キー」タブ→「キーを追加」→「JSON」を選択
6. ダウンロードしたJSONファイルをプロジェクトフォルダに`credentials.json`として保存

### 3. 環境変数の設定

`.env.example`ファイルをコピーして`.env`ファイルを作成：

```bash
cp .env.example .env
```

`.env`ファイルを編集：

```env
# ダウンロードしたサービスアカウントキーファイルのパス
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json

# Google CloudプロジェクトID（コンソールで確認）
GOOGLE_CLOUD_PROJECT=your-project-id
```

## 使用方法

### 基本的な使い方

```bash
# 単一ファイルの翻訳（デフォルト：日本語 → 韓国語）
python translate.py -i ./document.pdf

# 出力フォルダを指定
python translate.py -i ./document.pdf -o ./translated/

# フォルダ内のすべてのPDFを一括翻訳
python translate.py -i ./docs/ -o ./output/ --batch

# 言語を指定（英語→韓国語）
python translate.py -i ./english.pdf -s en -t ko
```

### コマンドオプション

| オプション | 短縮 | 必須 | デフォルト | 説明 |
|-----------|------|------|-----------|------|
| `--input` | `-i` | Y | - | 入力PDFファイルまたはフォルダパス |
| `--output` | `-o` | N | `./output` | 出力フォルダパス |
| `--source` | `-s` | N | `ja` | ソース言語コード |
| `--target` | `-t` | N | `ko` | ターゲット言語コード |
| `--batch` | `-b` | N | `False` | フォルダ一括処理モード |
| `--recursive` | `-r` | N | `False` | サブフォルダを含む再帰処理（フォルダ構造を保持） |

### サポートされている言語コード

- `ja` - 日本語
- `ko` - 한국어（韓国語）
- `en` - English（英語）
- `zh` - 中文（中国語）
- `es` - Español（スペイン語）
- `fr` - Français（フランス語）
- `de` - Deutsch（ドイツ語）
- [全言語リスト](https://cloud.google.com/translate/docs/languages)

## 使用例

### 例1: 単一ファイルの翻訳

```bash
python translate.py -i ./目論見書.pdf -o ./output/
```

出力:
```
============================================================
🌏 PDF Translator (Document Translation API)
============================================================
📁 入力: ./目論見書.pdf (1ファイル)
📂 出力: ./output
🌐 翻訳: 日本語 → 韓国語
============================================================

[1/1] 📄 目論見書.pdf
   📊 ファイルサイズ: 2.1 MB
   🌐 ドキュメントを翻訳中... ✓
   💾 ファイルを保存中... ✓ (2.3 MB)
   → ./output/目論見書_ko.pdf

============================================================
✅ 完了！合計1ファイルの翻訳に成功しました
============================================================
```

### 例2: フォルダの再帰的な一括翻訳（日本語→韓国語）

```bash
python translate.py -i ./docs/ -o ./output/ --recursive -s ja -t ko
```

### 例3: サブフォルダ内のファイルを翻訳（デフォルト使用：日本語 → 韓国語）

```bash
python translate.py -i "./docs/キャピタル世界株式ファンド (分配金再投資)/jp-ark-gef.pdf"
```

### 例4: 使用統計の確認

```bash
# サマリー
python translate.py stats

# 詳細履歴（最新10件）
python translate.py stats --detail

# 月次統計
python translate.py stats --month 2

# 特定の年月の統計
python translate.py stats --month 1 --year 2026
```

出力:
```
============================================================
📊 PDF Translator - 使用統計
============================================================
📄 翻訳されたファイル総数: 15
📦 処理されたデータ総量: 42.5 MB
💰 累積推定コスト: $25.50 USD
============================================================

💡 詳細履歴を見るには: python translate.py stats --detail
```

## プロジェクト構造

```
pdf-translator/
├── translate.py              # メインCLIスクリプト
├── translator/
│   ├── __init__.py          # パッケージ初期化
│   ├── client.py            # Google Cloud Translationクライアント
│   ├── config.py            # 設定定数
│   ├── service.py           # 翻訳オーケストレーションレイヤー
│   ├── validators.py        # 入力検証関数
│   ├── utils.py             # ユーティリティ関数
│   └── usage.py             # 使用状況追跡
├── requirements.txt         # Pythonパッケージの依存関係
├── .env.example            # 環境変数テンプレート
├── .env                    # 環境変数（作成が必要）
├── credentials.json        # Google Cloudサービスアカウントキー（作成が必要）
├── usage_history.json      # API使用記録（自動生成）
└── README.md               # このファイル
```

## 使用状況の追跡

プログラムは、すべての翻訳タスクを`usage_history.json`ファイルに自動的に記録します。

### 追跡される情報

- 翻訳日時
- 入力/出力ファイル名
- ソース/ターゲット言語
- ファイルサイズ
- 推定コスト

### 使用統計コマンド

```bash
# サマリー
python translate.py stats

# 詳細履歴を表示
python translate.py stats --detail

# 月次統計
python translate.py stats --month 2 --year 2026

# 使用履歴をクリア（注意！）
python translate.py stats --clear
```

## 料金

Google Cloud Translation API v3 Document Translation料金：

- **無料枠**: なし（v2テキスト翻訳のみ月50万文字無料）
- **ドキュメント翻訳コスト**: 
  - ページあたり$0.075（最初の月500ページ）
  - ページあたり$0.045（500ページ超過分）
- **例**: 30ページのPDF → 約$2.25

詳細については、[Google Cloud Translation料金](https://cloud.google.com/translate/pricing)を参照してください。

## Document Translation vs Text Translation

| 機能 | Document Translation (v3) | Text Translation (v2) |
|------|---------------------------|------------------------|
| **入力** | PDF/DOCXファイル | テキスト文字列 |
| **レイアウト** | 完全に保持 | 損失 |
| **フォーマット** | 完全に保持（フォント、画像など） | 損失 |
| **翻訳品質** | コンテキストベース、高品質 | 基本品質 |
| **料金** | ページごと | 文字ごと |
| **無料枠** | なし | 月50万文字 |

**このプログラムはDocument Translationを使用しています。**

## トラブルシューティング

### 認証エラー

```
❌ エラー: GOOGLE_APPLICATION_CREDENTIALS環境変数が設定されていません。
```

**解決方法**: `.env`ファイルを作成し、`GOOGLE_APPLICATION_CREDENTIALS`パスを正しく設定してください。

### プロジェクトIDエラー

```
❌ エラー: GOOGLE_CLOUD_PROJECT環境変数が設定されていません。
```

**解決方法**: `.env`ファイルで`GOOGLE_CLOUD_PROJECT`を正しく設定してください。

### API有効化エラー

```
❌ エラー: Translation APIが有効になっていません。
```

**解決方法**: Google Cloud ConsoleでCloud Translation APIを有効にしてください。

### ファイルサイズの制限

Document Translation APIにはファイルサイズの制限があります：
- **最大ファイルサイズ**: 10MB
- **最大ページ数**: 300ページ

大きなファイルは分割して処理してください。

### クォータ超過

```
❌ エラー: APIクォータを超過しました。
```

**解決方法**: 
- Google Cloud Consoleでクォータを確認
- 請求アカウントが有効になっていることを確認
- クォータの増加をリクエスト

## ライセンス

MIT License

## 貢献

イシューやプルリクエストはいつでも歓迎します！

## サポート

問題が発生した場合は、GitHubでイシューを作成してください。
