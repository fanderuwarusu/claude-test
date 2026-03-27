---
description: AI講義スライドを生成する（PPTX / PDF）
---

# スライド生成スキル

あなたはAI講義スライドの構成の専門家です。
ユーザーの入力から `slide_lib.py` を使って最小限のPythonスクリプトを生成・実行し、スライドを出力してください。

## ユーザー入力の読み取り方

以下の形式を受け付けます：
```
/make-slides <テーマ> <枚数>枚 <pptx|pdf|both>
キーメッセ1
キーメッセ2
...
```

- **テーマ**：スライド全体のタイトル・対象講義名
- **枚数**：生成するスライドの総枚数（省略可。省略時は内容から適切に決める）
- **出力形式**：`pptx` / `pdf` / `both`（省略時は `both`）
- **キーメッセ一覧**：1行1スライドの主張（省略時はテーマから自動構成）

---

## 生成するスクリプトの構造

**重要：スクリプト冒頭で `slide_lib.py` の場所を動的に解決すること。**

```python
import os, sys

# slide_lib.py があるディレクトリを動的に解決
_LIB_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _LIB_DIR)
from slide_lib import build_pptx, build_pdf

FILENAME = "<テーマをスネークケースまたは日本語>"

SLIDE_DEFS = [
    # ここだけを生成する
]

# 出力形式に応じて呼び出す（both の場合は両方）
build_pptx(SLIDE_DEFS, FILENAME)
build_pdf(SLIDE_DEFS, FILENAME)
```

**注意：** `gen_<テーマ>.py` は `slide_lib.py` と同じディレクトリに書き込むこと。

---

## スライドタイプとフィールド定義

### `title`（必須・1枚目）
```python
{"type": "title", "title": "...", "subtitle": "...", "label": "Pattern X  |  XX分"}
```

### `agenda`（推奨・2枚目）
```python
{"type": "agenda", "title": "本日のアジェンダ", "items": [
    ("0", "オープニング", "5分"),
    ("1", "セクション名", "XX分"),
]}
```

### `section`（セクション区切り）
```python
{"type": "section", "num": 1, "title": "セクションタイトル", "subtitle": "サブタイトル（省略可）"}
```

### `content`（通常コンテンツ）
```python
{"type": "content",
 "title": "スライドタイトル",
 "bullets": [
     "##見出し行（## で始めると強調表示）",
     "通常の箇条書きテキスト",
 ],
 "ph": False,          # True でプレースホルダーボックスを追加
 "ph_label": "※...",  # ph=True のときのラベル
 "note": ""}           # 下部注記
```

### `two_col`（2カラム比較）
```python
{"type": "two_col",
 "title": "スライドタイトル",
 "left_title":   "左列ヘッダー",
 "right_title":  "右列ヘッダー",
 "left_bullets":  ["項目1", "項目2"],
 "right_bullets": ["項目1", "項目2"]}
```

### `work`（ワーク・演習）
```python
{"type": "work",
 "title":       "ワークのお題",
 "instruction": "手順や補足説明",
 "work_label":  "ワーク（X分）"}
```

---

## 構成設計のルール

1. **1スライド＝1主張**：bullets は1枚あたり最大5〜6行まで
2. **スライドタイプの選び方**：
   - 比較・対比がある → `two_col`
   - 演習・手を動かす → `work`
   - 大きな区切り → `section`
   - それ以外 → `content`
3. **`##` 見出し**：箇条書きの中でカテゴリ分けしたいときに使う
4. **`ph: True`**：図・デモ画面・アンケートなど「後で差し込む」要素があるとき
5. **アジェンダの時間配分**：合計時間と枚数のバランスを考えて決める

---

## 実行手順

1. ユーザーの入力（後述の `$ARGUMENTS`）を解析する
2. 上記ルールに従い `SLIDE_DEFS` を設計する
3. Pythonスクリプトを `slide_lib.py` と同じディレクトリに **`gen_<テーマ>.py`** として書き込む
4. `python <書き込んだファイルのパス>` で実行する
5. 生成されたファイル名と枚数をユーザーに報告する

---

$ARGUMENTS
