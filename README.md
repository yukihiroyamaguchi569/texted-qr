# Texted QR

QRコードのドットパターンの中に、指定した文字が浮かび上がって見える画像を生成する Web アプリ。

![example](docs/example.png)

## 特徴

- テキストはドットを「削除」せず「色変え」するだけなので、QR コードは 100% スキャン可能
- エラー訂正レベル H（30% 損傷許容）を使用
- フォントサイズを自動計算（画像幅の 60% に収まる最大サイズ）
- テキスト配置を 中央 / 上 / 下 から選択可能
- アクセントカラーをカラーピッカーで自由に指定
- PNG ダウンロード対応

## セットアップ

```bash
git clone <repo-url>
cd texted-QR

python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## 起動

```bash
source venv/bin/activate
python app.py
```

ブラウザで `http://127.0.0.1:5000` を開く。

## 使い方

1. **URL** に埋め込みたいリンクを入力
2. **テキスト** に浮かび上がらせたい文字を入力（20 文字以内推奨）
3. **配置**（中央 / 上 / 下）と**アクセントカラー**を選択
4. 「生成」ボタンを押してプレビュー確認
5. スマホカメラでスキャンして動作確認
6. 「PNG ダウンロード」で保存

## ファイル構成

```
texted-QR/
├── app.py            # Flask ルート（/, /generate, /download）
├── qr_engine.py      # コアアルゴリズム
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   └── style.css
└── fonts/
    └── NotoSans-Bold.ttf
```

## 技術スタック

| 用途 | ライブラリ |
|------|-----------|
| Web フレームワーク | Flask |
| QR 生成 | qrcode[pil] |
| 画像処理 | Pillow |
| フォント | Noto Sans Bold |

## アルゴリズム概要

```
QR マトリクス生成（ERROR_CORRECT_H）
    ↓
テキストマスク画像を生成（グレースケール）
    ↓
各モジュールを走査
  ON + マスク内 → アクセントカラーのドット
  ON + マスク外 → 黒いドット
  OFF           → 白背景
    ↓
PNG 出力
```
