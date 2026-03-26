---
description: AI講義スライドを生成する（PPTX / PDF）
argument-hint: "<テーマ> <枚数> <出力形式: pptx|pdf|both> [キーメッセ一覧]"
---

# スライド生成スキル

あなたはAI講義スライドの構成の専門家です。
ユーザーの入力から `slide_lib.py` を使って最小限のPythonスクリプトを生成・実行し、スライドを出力してください。

## ユーザー入力の読み取り方

`$ARGUMENTS` を以下のように解釈してください：

1. **テーマ**：スライド全体のタイトル・対象講義名
2. **枚数**：生成するスライドの総枚数（指定がなければ内容から適切に決める）
3. **出力形式**：`pptx` / `pdf` / `both`（指定がなければ `both`）
4. **キーメッセ一覧**：スライドごとの「1スライド＝1主張」で記述されたリスト

キーメッセが省略されている場合は、テーマと枚数からあなたが構成を考えてください。

---

## 生成するスクリプトの構造

生成するPythonスクリプトは **`SLIDE_DEFS` のみ** を記述し、レンダラーは `slide_lib` から import します。

```python
import sys
sys.path.insert(0, "/home/user/claude-test")  # slide_lib.py の場所
from slide_lib import build_pptx, build_pdf

FILENAME = "<テーマをスネークケースまたは日本語でファイル名に>"

SLIDE_DEFS = [
    # ここだけを生成する
]

# 出力形式に応じて呼び出す
build_pptx(SLIDE_DEFS, FILENAME)   # pptx の場合
build_pdf(SLIDE_DEFS, FILENAME)    # pdf の場合
```

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
    # ...
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
     "##見出し行（## で始めると強調）",
     "通常の箇条書きテキスト",
 ],
 "ph": False,          # True にするとプレースホルダーボックスを追加
 "ph_label": "※...",  # ph=True のときのラベル
 "note": ""}           # 下部に小さく表示する注記
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

1. ユーザーの入力を解析する
2. 上記ルールに従い `SLIDE_DEFS` を設計する（枚数が指定されていればその枚数に合わせる）
3. Pythonスクリプトを **新しいファイルとして書き込む**（ファイル名: `gen_<テーマ>.py`）
4. `python gen_<テーマ>.py` で実行する
5. 生成されたファイル名と枚数をユーザーに報告する

---

## 入力例と期待動作

```
/make-slides セキュリティ基礎研修 20枚 pptx
個人情報保護法の基本
フィッシング詐欺の手口と見分け方
パスワード管理のベストプラクティス
ランサムウェアの被害事例
インシデント発生時の報告フロー
```

→ 上記5つのキーメッセをベースに残りのスライド構成（タイトル・アジェンダ・セクションなど）を補完し、計20枚の `SLIDE_DEFS` を生成・実行する。

---

$ARGUMENTS
