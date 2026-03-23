# create-slides

マークダウンからプレゼンテーションスライド（PPTX＋PDF）を生成するスキル。

## あなたの役割

ユーザーが提供するマークダウンを解析し、デザインテンプレート付きのPPTXとPDFを生成する。
検索・調査が必要な箇所は `※〜` 形式のプレースホルダーとして明示したまま柄だけ作成する。

---

## Step 1: 対話で情報収集

以下の項目を**1メッセージにまとめて**ユーザーに確認する。

```
以下を教えてください：

1. **マークダウン** — スライドの構成・内容をマークダウンで貼り付けてください
   （まだなければ「後で」と言えばスキップできます）

2. **出力ファイル名** — 例: `AI研修_スライド`（拡張子不要）

3. **カラーテーマ** — 以下から選択、または16進数カラーコードで指定
   - [A] ネイビー × ブルー（デフォルト・ビジネス向け）
   - [B] ダークグリーン × ライトグリーン（研修・教育向け）
   - [C] チャコール × オレンジ（インパクト重視）
   - [D] カスタム（メインカラー・アクセントカラーを指定）

4. **スライドサイズ** — [A] 16:9（デフォルト）/ [B] 4:3
```

---

## Step 2: マークダウン解析ルール

ユーザーのマークダウンを以下のルールでスライド種別にマッピングする。

| マークダウン記法 | スライド種別 |
|---|---|
| `# タイトル` （文書先頭） | タイトルスライド |
| `## セクション名` | セクション区切りスライド |
| `### スライドタイトル` | コンテンツスライド |
| `### スライドタイトル` + 左右に `---` で分割されたリスト | 2カラムスライド |
| `### [ワーク] タイトル` または `### [演習]` | ワーク・体験スライド |
| `### アジェンダ` または `### 目次` | アジェンダスライド |
| 段落中の `※〜` または `【〜】` | プレースホルダー（グレーボックス） |

**注意：** マークダウンに `※` や `【検索必要】` などの記述があっても、
そのままプレースホルダーとして保持し、内容を補完しない。

---

## Step 3: Pythonスクリプト生成・実行

以下のテンプレートをベースに、解析結果に合わせたPythonスクリプトを生成して実行する。

### カラーテーマ定義

```python
THEMES = {
    "A": {  # ネイビー × ブルー
        "primary":   RGBColor(0x1A, 0x2E, 0x4A),
        "accent":    RGBColor(0x00, 0x8C, 0xD7),
        "bg":        RGBColor(0xF0, 0xF6, 0xFC),
        "white":     RGBColor(0xFF, 0xFF, 0xFF),
        "gray":      RGBColor(0x6B, 0x7A, 0x8D),
        "ph":        RGBColor(0xCC, 0xCC, 0xCC),
    },
    "B": {  # ダークグリーン × ライトグリーン
        "primary":   RGBColor(0x1A, 0x3A, 0x2A),
        "accent":    RGBColor(0x2E, 0xA8, 0x5A),
        "bg":        RGBColor(0xF0, 0xFA, 0xF3),
        "white":     RGBColor(0xFF, 0xFF, 0xFF),
        "gray":      RGBColor(0x6B, 0x7A, 0x6D),
        "ph":        RGBColor(0xCC, 0xCC, 0xCC),
    },
    "C": {  # チャコール × オレンジ
        "primary":   RGBColor(0x2C, 0x2C, 0x2C),
        "accent":    RGBColor(0xE8, 0x6A, 0x1A),
        "bg":        RGBColor(0xFA, 0xF8, 0xF5),
        "white":     RGBColor(0xFF, 0xFF, 0xFF),
        "gray":      RGBColor(0x7A, 0x7A, 0x7A),
        "ph":        RGBColor(0xCC, 0xCC, 0xCC),
    },
}
```

### スライドサイズ定義

```python
SIZES = {
    "16:9": (Inches(13.33), Inches(7.5)),
    "4:3":  (Inches(10.0),  Inches(7.5)),
}
```

### スライド部品（関数）

以下の関数を必ず実装すること（前回セッションで確立したデザインルールを踏襲）：

- `make_title_slide(prs, title, subtitle, label, theme)` — タイトルスライド
- `make_section_divider(prs, num, title, subtitle, theme)` — セクション区切り
- `make_content_slide(prs, title, bullets, has_placeholder, ph_label, note, theme)` — コンテンツ
- `make_two_col_slide(prs, title, left_title, right_title, left_bullets, right_bullets, theme)` — 2カラム
- `make_work_slide(prs, title, instruction, work_label, theme)` — ワーク
- `make_agenda_slide(prs, title, items, theme)` — アジェンダ
- `add_placeholder_box(slide, x, y, w, h, label, theme)` — プレースホルダーボックス

### PDF変換

PPTXを生成した後、`reportlab` + `python-pptx` でPDFも同時生成する。
日本語フォントは以下の順で自動検索して使用する：

```python
FONT_PATHS = [
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf",
    "/usr/share/fonts/truetype/vlgothic/VL-Gothic-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
```

---

## Step 4: 出力・確認

生成完了後に以下を報告する：

```
✅ 生成完了

📄 PPTX: <ファイル名>.pptx（XX枚）
📄 PDF:  <ファイル名>.pdf（GitHub上で閲覧可能）

プレースホルダー一覧（後から埋める箇所）：
- スライド X: ※〜
- スライド Y: 【〜】
...

Gitにコミット・プッシュしますか？
```

---

## 制約・注意事項

- `python-pptx` と `reportlab` が未インストールの場合は `pip install` してから実行する
- プレースホルダー（`※`・`【】`）の内容は**絶対に補完しない**
- スクリプトは実行後も `create_slides_<ファイル名>.py` として保存する
- マークダウンが提供されない場合はサンプル構成を提案してユーザーに確認してから生成する
