"""
AI講義設計スライド生成スクリプト
パターン1: AI基礎講義（90分）
パターン2: AI業務導入ワークショップ（60分）
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import copy

# ============================================================
# カラーパレット
# ============================================================
COLOR_NAVY    = RGBColor(0x1A, 0x2E, 0x4A)   # 濃紺（タイトル背景）
COLOR_ACCENT  = RGBColor(0x00, 0x8C, 0xD7)   # アクセントブルー
COLOR_LIGHT   = RGBColor(0xF0, 0xF6, 0xFC)   # 薄青（コンテンツ背景）
COLOR_WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
COLOR_DARK    = RGBColor(0x1A, 0x2E, 0x4A)
COLOR_GRAY    = RGBColor(0x6B, 0x7A, 0x8D)
COLOR_PLACEHOLDER = RGBColor(0xCC, 0xCC, 0xCC)  # プレースホルダー用グレー

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)


def set_bg(slide, color):
    """スライド背景色を設定"""
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, x, y, w, h, color, alpha=None):
    """矩形を追加"""
    shape = slide.shapes.add_shape(1, x, y, w, h)  # MSO_SHAPE_TYPE.RECTANGLE = 1
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def add_text(slide, text, x, y, w, h, font_size=18, bold=False,
             color=COLOR_DARK, align=PP_ALIGN.LEFT, wrap=True):
    """テキストボックスを追加"""
    txBox = slide.shapes.add_textbox(x, y, w, h)
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = color
    return txBox


def add_placeholder_box(slide, x, y, w, h, label="※ここに内容を入力"):
    """プレースホルダーボックス（点線風）"""
    rect = slide.shapes.add_shape(1, x, y, w, h)
    rect.fill.solid()
    rect.fill.fore_color.rgb = RGBColor(0xF7, 0xF7, 0xF7)
    rect.line.color.rgb = COLOR_PLACEHOLDER
    rect.line.width = Pt(1)
    tf = rect.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = label
    run.font.size = Pt(14)
    run.font.color.rgb = COLOR_PLACEHOLDER
    run.font.italic = True
    return rect


def make_title_slide(prs, title, subtitle, pattern_label):
    """タイトルスライド"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    set_bg(slide, COLOR_NAVY)

    # 左側アクセントバー
    add_rect(slide, Inches(0), Inches(0), Inches(0.5), SLIDE_H, COLOR_ACCENT)

    # パターンラベル
    add_text(slide, pattern_label,
             Inches(1), Inches(1.5), Inches(10), Inches(0.6),
             font_size=16, color=COLOR_ACCENT, bold=True)

    # メインタイトル
    add_text(slide, title,
             Inches(1), Inches(2.2), Inches(11), Inches(1.6),
             font_size=40, bold=True, color=COLOR_WHITE)

    # サブタイトル
    add_text(slide, subtitle,
             Inches(1), Inches(3.9), Inches(10), Inches(0.7),
             font_size=22, color=RGBColor(0xA0, 0xC4, 0xE8))

    # 日付・講師プレースホルダー
    add_text(slide, "【日付】　【講師名】",
             Inches(1), Inches(5.5), Inches(8), Inches(0.5),
             font_size=14, color=COLOR_GRAY)

    return slide


def make_section_divider(prs, section_num, section_title, section_subtitle=""):
    """セクション区切りスライド"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, COLOR_ACCENT)

    add_rect(slide, Inches(0), Inches(0), Inches(13.33), Inches(0.08), COLOR_WHITE)
    add_rect(slide, Inches(0), Inches(7.42), Inches(13.33), Inches(0.08), COLOR_WHITE)

    add_text(slide, f"Section {section_num}",
             Inches(1.5), Inches(2.2), Inches(10), Inches(0.8),
             font_size=20, color=COLOR_WHITE, align=PP_ALIGN.CENTER)

    add_text(slide, section_title,
             Inches(1), Inches(3.0), Inches(11.33), Inches(1.2),
             font_size=36, bold=True, color=COLOR_WHITE, align=PP_ALIGN.CENTER)

    if section_subtitle:
        add_text(slide, section_subtitle,
                 Inches(1.5), Inches(4.3), Inches(10), Inches(0.7),
                 font_size=18, color=RGBColor(0xD0, 0xEC, 0xFF), align=PP_ALIGN.CENTER)

    return slide


def make_content_slide(prs, title, bullet_points=None, has_placeholder=False,
                       placeholder_label="※ここに内容を入力", note=""):
    """通常コンテンツスライド"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, COLOR_LIGHT)

    # ヘッダーバー
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, Inches(1.1), COLOR_NAVY)
    # アクセントライン
    add_rect(slide, Inches(0), Inches(1.1), SLIDE_W, Inches(0.07), COLOR_ACCENT)

    # スライドタイトル
    add_text(slide, title,
             Inches(0.4), Inches(0.18), Inches(12), Inches(0.8),
             font_size=24, bold=True, color=COLOR_WHITE)

    if bullet_points:
        y_pos = Inches(1.4)
        for bp in bullet_points:
            if bp.startswith("##"):
                # サブヘッダー
                add_text(slide, bp[2:].strip(),
                         Inches(0.5), y_pos, Inches(12), Inches(0.45),
                         font_size=16, bold=True, color=COLOR_ACCENT)
                y_pos += Inches(0.48)
            else:
                add_text(slide, f"▶  {bp}",
                         Inches(0.7), y_pos, Inches(11.8), Inches(0.45),
                         font_size=15, color=COLOR_DARK)
                y_pos += Inches(0.48)

    if has_placeholder:
        ph_y = Inches(5.5) if bullet_points else Inches(1.5)
        ph_h = Inches(1.5) if bullet_points else Inches(5.0)
        add_placeholder_box(slide, Inches(0.5), ph_y, Inches(12.3), ph_h,
                            placeholder_label)

    if note:
        add_text(slide, f"📌 {note}",
                 Inches(0.5), Inches(6.8), Inches(12), Inches(0.4),
                 font_size=11, color=COLOR_GRAY)

    return slide


def make_two_col_slide(prs, title, left_title, right_title,
                       left_bullets=None, right_bullets=None):
    """2カラムスライド"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, COLOR_LIGHT)

    add_rect(slide, Inches(0), Inches(0), SLIDE_W, Inches(1.1), COLOR_NAVY)
    add_rect(slide, Inches(0), Inches(1.1), SLIDE_W, Inches(0.07), COLOR_ACCENT)

    add_text(slide, title,
             Inches(0.4), Inches(0.18), Inches(12), Inches(0.8),
             font_size=24, bold=True, color=COLOR_WHITE)

    col_w = Inches(5.8)
    # 左カラムヘッダー
    add_rect(slide, Inches(0.4), Inches(1.3), col_w, Inches(0.45), COLOR_ACCENT)
    add_text(slide, left_title,
             Inches(0.5), Inches(1.32), col_w - Inches(0.1), Inches(0.4),
             font_size=14, bold=True, color=COLOR_WHITE)

    # 右カラムヘッダー
    add_rect(slide, Inches(7.0), Inches(1.3), col_w, Inches(0.45), COLOR_NAVY)
    add_text(slide, right_title,
             Inches(7.1), Inches(1.32), col_w - Inches(0.1), Inches(0.4),
             font_size=14, bold=True, color=COLOR_WHITE)

    # 左コンテンツ
    if left_bullets:
        y = Inches(1.9)
        for b in left_bullets:
            add_text(slide, f"・{b}", Inches(0.5), y, Inches(5.6), Inches(0.45),
                     font_size=14, color=COLOR_DARK)
            y += Inches(0.48)
    else:
        add_placeholder_box(slide, Inches(0.4), Inches(1.85), col_w, Inches(5.0))

    # 右コンテンツ
    if right_bullets:
        y = Inches(1.9)
        for b in right_bullets:
            add_text(slide, f"・{b}", Inches(7.1), y, Inches(5.6), Inches(0.45),
                     font_size=14, color=COLOR_DARK)
            y += Inches(0.48)
    else:
        add_placeholder_box(slide, Inches(7.0), Inches(1.85), col_w, Inches(5.0))

    return slide


def make_work_slide(prs, title, instruction, work_label="ワーク"):
    """ワーク・体験スライド"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, COLOR_NAVY)

    # ワークバッジ
    add_rect(slide, Inches(0.4), Inches(0.3), Inches(1.8), Inches(0.6), COLOR_ACCENT)
    add_text(slide, f"✏  {work_label}",
             Inches(0.45), Inches(0.32), Inches(1.7), Inches(0.55),
             font_size=14, bold=True, color=COLOR_WHITE)

    add_text(slide, title,
             Inches(0.4), Inches(1.1), Inches(12.5), Inches(1.0),
             font_size=30, bold=True, color=COLOR_WHITE)

    add_text(slide, instruction,
             Inches(0.4), Inches(2.3), Inches(12.5), Inches(0.7),
             font_size=16, color=RGBColor(0xA0, 0xC4, 0xE8))

    add_placeholder_box(slide, Inches(0.4), Inches(3.2), Inches(12.5), Inches(3.7),
                        "※ワーク内容・手順をここに記載")

    return slide


def make_agenda_slide(prs, title, items):
    """アジェンダスライド"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, COLOR_LIGHT)

    add_rect(slide, Inches(0), Inches(0), SLIDE_W, Inches(1.1), COLOR_NAVY)
    add_rect(slide, Inches(0), Inches(1.1), SLIDE_W, Inches(0.07), COLOR_ACCENT)

    add_text(slide, title,
             Inches(0.4), Inches(0.18), Inches(12), Inches(0.8),
             font_size=24, bold=True, color=COLOR_WHITE)

    y = Inches(1.35)
    for i, (num, label, duration) in enumerate(items):
        bg_col = COLOR_ACCENT if i % 2 == 0 else COLOR_NAVY
        add_rect(slide, Inches(0.4), y, Inches(0.7), Inches(0.55), bg_col)
        add_text(slide, num, Inches(0.4), y + Inches(0.05), Inches(0.7), Inches(0.45),
                 font_size=14, bold=True, color=COLOR_WHITE, align=PP_ALIGN.CENTER)

        add_rect(slide, Inches(1.15), y, Inches(9.8), Inches(0.55),
                 RGBColor(0xFF, 0xFF, 0xFF))
        add_text(slide, label, Inches(1.25), y + Inches(0.05), Inches(8.5), Inches(0.45),
                 font_size=14, color=COLOR_DARK)

        add_rect(slide, Inches(10.9), y, Inches(2.0), Inches(0.55),
                 RGBColor(0xE8, 0xF4, 0xFF))
        add_text(slide, duration, Inches(10.9), y + Inches(0.05), Inches(2.0), Inches(0.45),
                 font_size=13, color=COLOR_ACCENT, align=PP_ALIGN.CENTER)

        y += Inches(0.62)

    return slide


# ============================================================
# パターン1: AI基礎講義（90分）
# ============================================================
def create_pattern1():
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H

    # 1. タイトル
    make_title_slide(prs,
        "AI基礎講義",
        "「AIを知る・使う」― 壁を下げ、業務で使える自分になる",
        "Pattern 1  |  90分")

    # 2. 本日のゴール
    make_content_slide(prs, "本日のゴール",
        bullet_points=[
            "個人でAIを使っている状態　→　仕事でAIを使える状態へ",
            "AIを「怖い・難しい」から「使えるツール」に変える",
            "今日の終わりに：議事録・メール・要約を自分で試せる",
        ])

    # 3. あなたのAI現在地は？
    make_content_slide(prs, "あなたのAI現在地は？",
        bullet_points=[
            "ChatGPT / Copilot / Gemini を使ったことがある？",
            "業務でAIを使っている？",
        ],
        has_placeholder=True,
        placeholder_label="※ チェック項目 / アンケート結果を貼り付け",
        note="オープニング 5分")

    # 4. セクション1
    make_section_divider(prs, 1, "生成AIとは何か", "LLMの仕組みと限界を平易に理解する")

    # 5. LLMの仕組み
    make_content_slide(prs, "生成AIとは何か：LLMの仕組み",
        bullet_points=[
            "LLM（大規模言語モデル）とは",
            "どうやって「文章を生成」しているか",
            "なぜ「賢く見える」のか",
        ],
        has_placeholder=True,
        placeholder_label="※ 図解：LLMの仕組みを挿入（トークン予測・確率分布など）",
        note="Section 1  |  20分")

    # 6. なぜ間違えるのか
    make_content_slide(prs, "なぜ間違えるのか：ハルシネーション",
        bullet_points=[
            "「確率的な次の単語予測」という本質",
            "ハルシネーション（事実と異なる回答）が起きるメカニズム",
            "知識のカットオフ日とは",
            "→ だから「確認」が重要",
        ],
        note="Section 1  |  20分")

    # 7. セクション2
    make_section_divider(prs, 2, "AIツール実践", "プロンプト設計＋業務ユースケース")

    # 8. プロンプト設計：悪い例
    make_two_col_slide(prs,
        "プロンプト設計：良い例 vs 悪い例",
        "❌ 悪い例",
        "✅ 良い例",
        left_bullets=None,
        right_bullets=None)

    # 9. 業務ユースケース①：議事録
    make_content_slide(prs, "業務ユースケース①：議事録自動生成",
        bullet_points=["使い方・プロンプト例"],
        has_placeholder=True,
        placeholder_label="※ ライブデモ画面キャプチャ or プロンプトテンプレートを挿入",
        note="Section 2  |  40分")

    # 10. 業務ユースケース②：メール文案
    make_content_slide(prs, "業務ユースケース②：メール文案生成",
        bullet_points=["使い方・プロンプト例"],
        has_placeholder=True,
        placeholder_label="※ ライブデモ画面キャプチャ or プロンプトテンプレートを挿入",
        note="Section 2  |  40分")

    # 11. 業務ユースケース③：要約
    make_content_slide(prs, "業務ユースケース③：文章要約",
        bullet_points=["使い方・プロンプト例"],
        has_placeholder=True,
        placeholder_label="※ ライブデモ画面キャプチャ or プロンプトテンプレートを挿入",
        note="Section 2  |  40分")

    # 12. ワーク
    make_work_slide(prs,
        "自分で打ってみよう",
        "1問だけ、実際にプロンプトを入力して送信してみましょう",
        work_label="ワーク（5分）")

    # 13. セクション3
    make_section_divider(prs, 3, "社会・産業へのAI浸透", "業種別事例と競合動向")

    # 14. 業種別導入事例
    make_content_slide(prs, "業種別導入事例",
        bullet_points=[
            "## 事例①　【受講者企業に近い業種】",
            "（事例内容）",
            "## 事例②　【受講者企業に近い業種】",
            "（事例内容）",
            "## 事例③　【受講者企業に近い業種】",
            "（事例内容）",
        ],
        has_placeholder=False,
        note="Section 3  |  15分 ｜ 受講者企業の業種に合わせて事例を差し替えること")

    # 15. セクション4
    make_section_divider(prs, 4, "リスクと注意点", "安全に使うための最低限の知識")

    # 16. リスクと注意点
    make_content_slide(prs, "リスクと注意点",
        bullet_points=[
            "情報漏洩リスク：入力してはいけない情報",
            "ハルシネーション：出力を鵜呑みにしない",
            "著作権・利用規約の確認",
            "社内ルールの確認",
        ],
        note="Section 4  |  10分")

    # 17. Q&A・まとめ
    make_content_slide(prs, "まとめ・Q&A",
        bullet_points=[
            "今日のポイント３つ（振り返り）",
            "明日からできること",
        ],
        has_placeholder=True,
        placeholder_label="※ Q&Aメモ欄",
        note="10分")

    prs.save("AI基礎講義_スライド.pptx")
    print("✅ AI基礎講義_スライド.pptx を生成しました")


# ============================================================
# パターン2: AI業務導入ワークショップ（60分）
# ============================================================
def create_pattern2():
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H

    # 1. タイトル
    make_title_slide(prs,
        "AI業務導入ワークショップ",
        "「AIを入れる」― 自社業務の分析と導入可能性の検討",
        "Pattern 2  |  60分  |  個社クローズド")

    # 2. 本日のゴール
    make_content_slide(prs, "本日のゴール",
        bullet_points=[
            "自社業務でのAI導入可能性を具体的に検討できる状態になる",
            "導入ロードマップの第一稿を持ち帰る",
            "次のアクションを決めて終わる",
        ])

    # 3. 事前分析サマリー
    make_content_slide(prs, "事前分析サマリー（ヒアリング結果）",
        bullet_points=[
            "## ヒアリング対象",
            "（対象者・部署）",
            "## 主な課題・ペイン",
            "（ヒアリング内容を記載）",
            "## 今日の焦点",
            "（絞り込んだ議論ポイント）",
        ],
        note="オープニング 10分 ｜ 事前ヒアリング内容に合わせて差し替えること")

    # 4. セクション1
    make_section_divider(prs, 1, "業務フロー確認", "AI介入ポイントの特定")

    # 5. 自社の業務フロー
    make_content_slide(prs, "自社の業務フロー（現状）",
        has_placeholder=True,
        placeholder_label="※ 業務フロー図を挿入（事前分析シートより）",
        note="Section 1  |  20分")

    # 6. AI介入ポイントの特定
    make_content_slide(prs, "AI介入ポイントの特定",
        bullet_points=[
            "繰り返し作業・定型業務はどこか",
            "データが蓄積されている工程はどこか",
            "人手エラーが起きやすい箇所はどこか",
        ],
        has_placeholder=True,
        placeholder_label="※ 特定した介入ポイントを記載",
        note="Section 1  |  20分")

    # 7. 優先度・難易度マトリクス
    make_content_slide(prs, "優先度・難易度マトリクス",
        bullet_points=["効果 × 実現難易度 × 緊急度　の3軸で評価"],
        has_placeholder=True,
        placeholder_label="※ 4象限マトリクス図を挿入（各候補をプロット）",
        note="Section 1  |  20分")

    # 8. セクション2
    make_section_divider(prs, 2, "導入可能性レポート", "技術・コスト・組織ハードルの整理")

    # 9. 技術的実現性
    make_two_col_slide(prs,
        "導入可能性レポート：技術・コスト・組織",
        "技術的実現性 / コスト感",
        "組織ハードル",
        left_bullets=None,
        right_bullets=None)

    # 10. セクション3
    make_section_divider(prs, 3, "導入ロードマップ", "短期・中期・長期フェーズ")

    # 11. 導入ロードマップ
    make_content_slide(prs, "導入ロードマップ",
        bullet_points=[
            "## 短期（〜3ヶ月）",
            "（PoC・パイロット導入）",
            "## 中期（3〜12ヶ月）",
            "（本番導入・効果検証）",
            "## 長期（1年〜）",
            "（全社展開・継続改善）",
        ],
        note="Section 3  |  15分")

    # 12. 次のアクション・クロージング
    make_content_slide(prs, "次のアクション・クロージング",
        bullet_points=[
            "今日決まったこと",
            "次回までのアクション（担当・期日）",
            "ご支援できること",
        ],
        has_placeholder=True,
        placeholder_label="※ アクションリストを記載",
        note="クロージング 15分")

    prs.save("AI業務導入ワークショップ_スライド.pptx")
    print("✅ AI業務導入ワークショップ_スライド.pptx を生成しました")


if __name__ == "__main__":
    create_pattern1()
    create_pattern2()
