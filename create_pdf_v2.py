"""
AI基礎講義_スライド_v2.pdf 生成スクリプト
reportlab で PPTX と同一内容の PDF を生成する
フォント：IPAGothic
スライドサイズ：4:3（720pt × 540pt）
v2: データ駆動型構造でスライド追加・変更が容易
"""

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

# ── フォント登録 ─────────────────────────────────────────────
FONT_PATH = "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"
pdfmetrics.registerFont(TTFont("JA", FONT_PATH))
F = "JA"

# ── サイズ（4:3） ────────────────────────────────────────────
PW = 10 * inch
PH = 7.5 * inch

OUTFILE = "AI基礎講義_スライド_v2.pdf"

# ── カラー ───────────────────────────────────────────────────
PRIMARY  = HexColor("#1A2E4A")
ACCENT   = HexColor("#008CD7")
BG       = HexColor("#F0F6FC")
WHITE    = HexColor("#FFFFFF")
GRAY     = HexColor("#6B7A8D")
PH_COLOR = HexColor("#CCCCCC")
PH_BG    = HexColor("#F7F7F7")
LT_BLUE  = HexColor("#A0C4E8")
ROW_WHITE = HexColor("#FFFFFF")


# ============================================================
# ユーティリティ
# ============================================================
def fill_bg(c, color=None):
    c.setFillColor(color or BG)
    c.rect(0, 0, PW, PH, fill=1, stroke=0)


def draw_rect(c, x, y, w, h, fill_color):
    c.setFillColor(fill_color)
    c.rect(x, PH - y - h, w, h, fill=1, stroke=0)


def text(c, s, x, y, size=14, color=PRIMARY, align="left", max_w=None):
    c.setFillColor(color)
    c.setFont(F, size)
    ry = PH - y - size
    if align == "center":
        c.drawCentredString(x + (max_w or 0) / 2, ry, s)
    elif align == "right":
        c.drawRightString(x + (max_w or 0), ry, s)
    else:
        c.drawString(x, ry, s)


def ph_box(c, x, y, w, h, label="※ここに内容を入力"):
    draw_rect(c, x, y, w, h, PH_BG)
    c.setStrokeColor(PH_COLOR)
    c.setLineWidth(0.5)
    c.rect(x, PH - y - h, w, h, fill=0, stroke=1)
    text(c, label, x, y + h / 2 - 6, size=11, color=PH_COLOR,
         align="center", max_w=w)


def header_bar(c, title):
    draw_rect(c, 0, 0, PW, 76, PRIMARY)
    draw_rect(c, 0, 76, PW, 4, ACCENT)
    text(c, title, 25, 14, size=20, color=WHITE)


# ============================================================
# スライド描画関数
# ============================================================
def render_title(c, d):
    fill_bg(c, PRIMARY)
    draw_rect(c, 0, 0, 32, PH, ACCENT)
    text(c, d["label"],    52, 102, size=13, color=ACCENT)
    text(c, d["title"],    52, 152, size=34, color=WHITE)
    text(c, d["subtitle"], 52, 270, size=16, color=LT_BLUE)
    text(c, "【日付】　【講師名】", 52, 408, size=12, color=GRAY)


def render_agenda(c, d):
    fill_bg(c)
    header_bar(c, d["title"])
    y = 90
    for i, (num, label, dur) in enumerate(d["items"]):
        bg = ACCENT if i % 2 == 0 else PRIMARY
        draw_rect(c, 25, y, 42, 46, bg)
        text(c, num, 25, y + 13, size=12, color=WHITE,
             align="center", max_w=42)
        draw_rect(c, 69, y, 523, 46, ROW_WHITE)
        text(c, label, 77, y + 14, size=12, color=PRIMARY)
        draw_rect(c, 594, y, 106, 46, HexColor("#D8EEEA"))
        text(c, dur, 594, y + 14, size=11, color=ACCENT,
             align="center", max_w=106)
        y += 52


def render_section(c, d):
    fill_bg(c, ACCENT)
    draw_rect(c, 0, 0, PW, 5, WHITE)
    draw_rect(c, 0, PH - 5, PW, 5, WHITE)
    text(c, f"Section {d['num']}", 0, 166, size=16, color=WHITE,
         align="center", max_w=PW)
    text(c, d["title"], 38, 206, size=28, color=WHITE,
         align="center", max_w=PW - 76)
    if d.get("subtitle"):
        text(c, d["subtitle"], 38, 300, size=14,
             color=HexColor("#D0ECFF"), align="center", max_w=PW - 76)


def render_content(c, d):
    fill_bg(c)
    header_bar(c, d["title"])
    y = 94
    bullets = d.get("bullets")
    if bullets:
        for b in bullets:
            if b.startswith("##"):
                text(c, b[2:].strip(), 28, y, size=14, color=ACCENT)
                y += 22
            else:
                text(c, f"▶  {b}", 28, y, size=13, color=PRIMARY)
                y += 20
            y += 4
    if d.get("ph"):
        ph_y = y + 6 if bullets else 94
        ph_h = min(120, PH - ph_y - 30) if bullets else (PH - 94 - 30)
        ph_box(c, 28, ph_y, PW - 56, ph_h, d.get("ph_label", "※ここに内容を入力"))
    if d.get("note"):
        text(c, f"📌 {d['note']}", 28, PH - 30, size=9, color=GRAY)


def render_two_col(c, d):
    fill_bg(c)
    header_bar(c, d["title"])
    cw = 308
    lx, rx = 25, 25 + cw + 22
    draw_rect(c, lx, 85, cw, 30, ACCENT)
    text(c, d["left_title"], lx + 6, 90, size=12, color=WHITE)
    draw_rect(c, rx, 85, cw, 30, PRIMARY)
    text(c, d["right_title"], rx + 6, 90, size=12, color=WHITE)
    lb = d.get("left_bullets")
    rb = d.get("right_bullets")
    if lb:
        y = 124
        for b in lb:
            text(c, f"・{b}" if b else "", lx + 6, y, size=12, color=PRIMARY)
            y += 18
    else:
        ph_box(c, lx, 118, cw, PH - 138, "※左カラム内容")
    if rb:
        y = 124
        for b in rb:
            text(c, f"・{b}" if b else "", rx + 6, y, size=12, color=PRIMARY)
            y += 18
    else:
        ph_box(c, rx, 118, cw, PH - 138, "※右カラム内容")


def render_work(c, d):
    fill_bg(c, PRIMARY)
    draw_rect(c, 28, 21, 120, 38, ACCENT)
    text(c, f"✏  {d.get('work_label', 'ワーク')}", 34, 27, size=12, color=WHITE)
    text(c, d["title"], 28, 80, size=24, color=WHITE)
    text(c, d["instruction"], 28, 158, size=13, color=LT_BLUE)
    ph_box(c, 28, 182, PW - 56, PH - 210, "※ワーク内容・手順をここに記載")


# ============================================================
# スライド定義（ここを編集してスライドを追加・変更）
# ============================================================
SLIDE_DEFS = [
    # ── 1: タイトル ───────────────────────────────────────────
    {
        "type": "title",
        "title": "AI基礎講義",
        "subtitle": "「AIを知る・使う」― 壁を下げ、業務で使える自分になる",
        "label": "Pattern 1  |  90分",
    },
    # ── 2: アジェンダ ─────────────────────────────────────────
    {
        "type": "agenda",
        "title": "本日のアジェンダ",
        "items": [
            ("0", "オープニング：今日のゴールと受講者のAI現在地確認",  "5分"),
            ("1", "生成AIとは何か：LLMの仕組みと限界",               "20分"),
            ("2", "AIツール実践：プロンプト設計＋業務ユースケース",   "40分"),
            ("3", "社会・産業へのAI浸透：競合・事例・動向",          "15分"),
            ("4", "リスクと注意点＋Q&A",                             "10分"),
        ],
    },
    # ── 3: 今日のゴール ───────────────────────────────────────
    {
        "type": "content",
        "title": "今日終わったら何が変わるか",
        "bullets": [
            "個人でAIを使っている状態　→　仕事でAIを使える状態へ",
            "AIを「怖い・難しい」から「使えるツール」に変える",
            "今日の終わりに：議事録・メール・要約を自分で試せる",
        ],
        "note": "オープニング  5分",
    },
    # ── 4: AI現在地確認 ───────────────────────────────────────
    {
        "type": "content",
        "title": "あなたの今のAI使用状況は？",
        "bullets": [
            "ChatGPT / Copilot / Gemini を使ったことがある？",
            "業務でAIを使っている？（週に何回くらい？）",
        ],
        "ph": True,
        "ph_label": "※ チェック項目 / アンケート結果を貼り付け",
        "note": "オープニング  5分",
    },
    # ── 5: Section 1 ──────────────────────────────────────────
    {
        "type": "section",
        "num": 1,
        "title": "生成AIとは何か",
        "subtitle": "LLMの仕組みと限界を平易に理解する",
    },
    # ── 6: LLMの仕組み ────────────────────────────────────────
    {
        "type": "content",
        "title": "そもそもAIとは何か：LLMの仕組み",
        "bullets": [
            "LLM（大規模言語モデル）とは",
            "どうやって「文章を生成」しているか",
            "なぜ「賢く見える」のか",
        ],
        "ph": True,
        "ph_label": "※ 図解：LLMの仕組み（トークン予測・確率分布）を挿入",
        "note": "Section 1  |  20分",
    },
    # ── 7: ハルシネーション ───────────────────────────────────
    {
        "type": "content",
        "title": "なぜAIは間違えるのか：ハルシネーション",
        "bullets": [
            "「確率的な次の単語予測」という本質",
            "ハルシネーション（事実と異なる回答）が起きるメカニズム",
            "知識のカットオフ日とは",
            "→ だから「確認」が重要",
        ],
        "note": "Section 1  |  20分",
    },
    # ── 8: できること・できないこと ───────────────────────────
    {
        "type": "two_col",
        "title": "AIにできること・できないこと",
        "left_title": "✅ 得意なこと",
        "right_title": "❌ 苦手なこと",
        "left_bullets": [
            "文章の要約・生成・翻訳",
            "アイデア出し・ブレスト",
            "コード補完・デバッグ支援",
            "定型メール・報告書の下書き",
            "データ整形・変換のコード生成",
        ],
        "right_bullets": [
            "最新情報の取得（カットオフ以降）",
            "正確な数値計算・統計処理",
            "社内固有ルールの自律判断",
            "責任ある意思決定",
            "感情・文脈の深い読み取り",
        ],
    },
    # ── 9: ツール比較 ─────────────────────────────────────────
    {
        "type": "content",
        "title": "ChatGPT・Claude・Gemini、何が違うか",
        "bullets": [
            "## ChatGPT（OpenAI）",
            "最も普及。GPT-4o。Copilot との連携で企業利用拡大",
            "## Claude（Anthropic）",
            "長文処理・安全性重視。コンテキストウィンドウが広い",
            "## Gemini（Google）",
            "Google Workspace との統合。検索連動で最新情報に強い",
        ],
        "note": "Section 1  |  20分",
    },
    # ── 10: AIエコシステム全体像（v2追加） ────────────────────
    {
        "type": "content",
        "title": "AIエコシステムの全体像",
        "bullets": [
            "## 基盤モデル層",
            "OpenAI / Anthropic / Google / Meta（LLaMA）など",
            "## アプリケーション層",
            "業務SaaS（Notion AI・Salesforce Einstein・GitHub Copilot）",
            "## 社内活用層",
            "RAG（社内文書検索）・エージェント・RPAとの連携",
        ],
        "note": "Section 1  |  20分",
    },
    # ── 11: Section 2 ─────────────────────────────────────────
    {
        "type": "section",
        "num": 2,
        "title": "AIツール実践",
        "subtitle": "プロンプト設計＋業務ユースケース（40分）",
    },
    # ── 12: 良い・悪いプロンプト ──────────────────────────────
    {
        "type": "two_col",
        "title": "良いプロンプトと悪いプロンプト",
        "left_title": "❌ 悪い例",
        "right_title": "✅ 良い例",
        "left_bullets": [
            "「まとめて」",
            "「なんかいい感じに」",
            "「報告書を書いて」",
            "",
            "→ 曖昧・ゴールが不明",
        ],
        "right_bullets": [
            "役割を指定する",
            "背景・条件を明示する",
            "出力形式を指定する",
            "例を示す（Few-shot）",
            "→ 具体・制約・ゴールが明確",
        ],
    },
    # ── 13: プロンプトテンプレート集（v2追加） ────────────────
    {
        "type": "content",
        "title": "すぐ使えるプロンプトテンプレート",
        "bullets": [
            "## 要約テンプレート",
            "「以下の文章を[対象読者]向けに[字数]字以内で要約してください」",
            "## 文章生成テンプレート",
            "「あなたは[役割]です。[背景]を踏まえて[形式]で書いてください」",
            "## 壁打ちテンプレート",
            "「[アイデア]について、メリット・デメリット・改善案を挙げてください」",
        ],
        "note": "Section 2  |  40分",
    },
    # ── 14: ライブデモ①議事録 ────────────────────────────────
    {
        "type": "content",
        "title": "ライブデモ①：議事録の自動要約",
        "bullets": [
            "手順：音声テキスト or 議事録テキストをそのまま貼り付ける",
            "プロンプト例：「以下の議事録を要約してください。決定事項・TODO・懸念点を箇条書きで」",
        ],
        "ph": True,
        "ph_label": "※ ライブデモ画面キャプチャ / プロンプトテンプレートを挿入",
        "note": "Section 2  |  40分",
    },
    # ── 15: ライブデモ②メール ────────────────────────────────
    {
        "type": "content",
        "title": "ライブデモ②：メール文案の生成",
        "bullets": [
            "手順：背景・相手・目的をひとこと伝えるだけ",
            "プロンプト例：「社内の営業部に依頼するメールを丁寧なビジネス文体で書いて」",
        ],
        "ph": True,
        "ph_label": "※ ライブデモ画面キャプチャ / プロンプトテンプレートを挿入",
        "note": "Section 2  |  40分",
    },
    # ── 16: ライブデモ③データ要約（v2追加） ──────────────────
    {
        "type": "content",
        "title": "ライブデモ③：表データの要約・考察",
        "bullets": [
            "手順：CSVや表をテキスト形式で貼り付ける",
            "プロンプト例：「以下のデータを分析し、傾向・課題・改善提案を3点ずつ挙げてください」",
        ],
        "ph": True,
        "ph_label": "※ ライブデモ画面キャプチャ / プロンプトテンプレートを挿入",
        "note": "Section 2  |  40分",
    },
    # ── 17: ワーク ────────────────────────────────────────────
    {
        "type": "work",
        "title": "自分でプロンプトを1つ打ってみよう",
        "instruction": "今日学んだ「良いプロンプトの型」を使って、実際に1問送信しましょう（5分）",
        "work_label": "ワーク（5分）",
    },
    # ── 18: Section 3 ─────────────────────────────────────────
    {
        "type": "section",
        "num": 3,
        "title": "社会・産業へのAI浸透",
        "subtitle": "業種別事例と「他社はここまでやっている」",
    },
    # ── 19: 業種別事例 ────────────────────────────────────────
    {
        "type": "content",
        "title": "業種別 AI導入事例",
        "bullets": [
            "## 事例①　【受講者企業に近い業種】",
            "※事例内容・効果をここに記載",
            "## 事例②　【受講者企業に近い業種】",
            "※事例内容・効果をここに記載",
            "## 事例③　【受講者企業に近い業種】",
            "※事例内容・効果をここに記載",
        ],
        "note": "Section 3  |  15分  ｜  受講者企業の業種に合わせて差し替えること",
    },
    # ── 20: AI導入の効果・ROI（v2追加） ──────────────────────
    {
        "type": "content",
        "title": "AI導入で何が変わるか：生産性・ROIの実態",
        "bullets": [
            "## 時間削減効果（McKinsey 2024調査より）",
            "定型業務（メール・要約・調査）：週平均 約3〜5時間削減",
            "## コスト試算例",
            "10人チーム × 年間240時間削減 ≒ 年間約480万円相当の効率化",
            "## 導入成功の共通点",
            "小さく始めて効果を測る → 横展開する",
        ],
        "note": "Section 3  |  15分",
    },
    # ── 21: Section 4 ─────────────────────────────────────────
    {
        "type": "section",
        "num": 4,
        "title": "リスクと注意点",
        "subtitle": "安全に使うための最低限の知識",
    },
    # ── 22: リスクと注意点 ────────────────────────────────────
    {
        "type": "content",
        "title": "AIを使う上でのリスクと注意点",
        "bullets": [
            "情報漏洩リスク：個人情報・社外秘は入力しない",
            "ハルシネーション：出力は必ず確認・ファクトチェック",
            "著作権・利用規約：商用利用時は各サービスの規約を確認",
            "社内ルールの確認：利用可能なツール・用途を把握しておく",
        ],
        "note": "Section 4  |  10分",
    },
    # ── 23: まとめ・Q&A ───────────────────────────────────────
    {
        "type": "content",
        "title": "まとめ・Q&A",
        "bullets": [
            "## 今日の3つのポイント",
            "① AIは「確率的な文章予測」――必ず確認する習慣を",
            "② 良いプロンプトは「役割・条件・形式」を明示する",
            "③ 他社はすでに動いている――まず1つ業務で試してみる",
        ],
        "ph": True,
        "ph_label": "※ Q&Aメモ欄",
        "note": "10分",
    },
]

# ============================================================
# ディスパッチ & ビルド
# ============================================================
RENDERERS = {
    "title":   render_title,
    "agenda":  render_agenda,
    "section": render_section,
    "content": render_content,
    "two_col": render_two_col,
    "work":    render_work,
}


def build():
    c = canvas.Canvas(OUTFILE, pagesize=(PW, PH))
    c.setTitle("AI基礎講義")

    for i, d in enumerate(SLIDE_DEFS):
        RENDERERS[d["type"]](c, d)
        if i < len(SLIDE_DEFS) - 1:
            c.showPage()

    c.save()
    print(f"✅ PDF生成完了: {OUTFILE}  ({len(SLIDE_DEFS)}ページ)")


if __name__ == "__main__":
    build()
