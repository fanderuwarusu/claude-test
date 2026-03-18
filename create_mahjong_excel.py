#!/usr/bin/env python3
"""
麻雀部結果管理 Excel ファイル生成スクリプト

シート構成:
  マスター      … 累計成績一覧（数式で自動更新）
  第1回(4人)    … 4人用サンプル入力シート
  第1回(8人)    … 8人用サンプル入力シート（A卓/B卓 分け）
  データ         … 集計用生データ（非表示）
  設定           … 参加者名リスト・ウマ設定（非表示）
  使い方         … 操作手順＆VBAコード
"""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

# ──────────────────────────────────────────────
# スタイルヘルパー
# ──────────────────────────────────────────────

def side(style="thin"):
    return Side(style=style)

def border(style="thin"):
    s = side(style)
    return Border(left=s, right=s, top=s, bottom=s)

def border_outer(style="medium"):
    m = side(style)
    t = side("thin")
    return Border(left=m, right=m, top=m, bottom=m)

def fill(color):
    return PatternFill(fill_type="solid", fgColor=color)

def font(bold=False, size=11, color="000000", name="游ゴシック"):
    return Font(bold=bold, size=size, color=color, name=name)

def align(h="center", v="center", wrap=False, h_align=None, indent=0):
    return Alignment(horizontal=h_align if h_align else h, vertical=v,
                     wrap_text=wrap, indent=indent)


def set_cell(ws, row, col, value=None, formula=None,
             bg=None, fg="000000", bold=False, size=11,
             h_align="center", wrap=False,
             border_style="thin", num_format=None,
             indent=0):
    cell = ws.cell(row=row, column=col)
    cell.value = formula if formula else value
    cell.font = Font(bold=bold, size=size, color=fg, name="游ゴシック")
    cell.alignment = Alignment(horizontal=h_align, vertical="center",
                                wrap_text=wrap, indent=indent)
    if bg:
        cell.fill = fill(bg)
    if border_style:
        s = side(border_style)
        cell.border = Border(left=s, right=s, top=s, bottom=s)
    if num_format:
        cell.number_format = num_format
    return cell


# ──────────────────────────────────────────────
# 色パレット
# ──────────────────────────────────────────────
C = {
    "navy":     "1B3A6B",
    "teal":     "005F6B",
    "teal_lt":  "E0F4F7",
    "a_dark":   "1565C0",   # A卓ヘッダー
    "a_light":  "E3F2FD",   # A卓行
    "b_dark":   "BF360C",   # B卓ヘッダー
    "b_light":  "FBE9E7",   # B卓行
    "gold":     "F9A825",
    "silver":   "9E9E9E",
    "bronze":   "8D6E63",
    "gray_hd":  "546E7A",
    "gray_lt":  "ECEFF1",
    "white":    "FFFFFF",
    "green":    "2E7D32",
    "yellow":   "FFFDE7",
}

SAMPLE_PLAYERS = [
    "鈴木太郎", "田中花子", "佐藤一郎", "山田次郎",
    "伊藤三郎", "渡辺四郎", "中村五郎", "小林六郎",
    "加藤七海", "吉田八重", "山本九太", "松本十子",
]


# ──────────────────────────────────────────────
# 設定シート
# ──────────────────────────────────────────────

def build_config(wb):
    ws = wb.create_sheet("設定")
    ws.sheet_state = "hidden"

    # ── 参加者リスト (A列)
    ws["A1"].value = "参加者リスト（ここに追加）"
    ws["A1"].font = Font(bold=True, size=11, name="游ゴシック")
    ws["A1"].fill = fill(C["navy"])
    ws["A1"].font = Font(bold=True, size=11, color="FFFFFF", name="游ゴシック")
    ws.column_dimensions["A"].width = 20

    for i, name in enumerate(SAMPLE_PLAYERS, 2):
        ws.cell(row=i, column=1, value=name)

    # ── ウマ設定 (C列)
    ws["C1"].value = "ウマ設定"
    ws["C1"].font = Font(bold=True, size=11, name="游ゴシック")
    ws["C1"].fill = fill(C["teal"])
    ws["C1"].font = Font(bold=True, size=11, color="FFFFFF", name="游ゴシック")

    uma_labels = ["1位", "2位", "3位", "4位"]
    uma_values = [20, 10, -10, -20]
    for i, (lbl, val) in enumerate(zip(uma_labels, uma_values), 2):
        ws.cell(row=i, column=3, value=lbl)
        ws.cell(row=i, column=4, value=val)
    ws.column_dimensions["C"].width = 8
    ws.column_dimensions["D"].width = 8

    # ── 返し点設定 (C7)
    ws["C6"].value = "返し点"
    ws["C7"].value = 30000

    return ws


# ──────────────────────────────────────────────
# データシート
# ──────────────────────────────────────────────

def build_data(wb):
    ws = wb.create_sheet("データ")
    ws.sheet_state = "hidden"

    headers = ["回数", "日付", "参加者名", "卓", "順位", "点数"]
    widths  = [8,      12,    18,       7,    7,    12  ]

    for c, (h, w) in enumerate(zip(headers, widths), 1):
        cell = ws.cell(row=1, column=c, value=h)
        cell.font  = Font(bold=True, color="FFFFFF", name="游ゴシック")
        cell.fill  = fill(C["navy"])
        cell.alignment = align()
        cell.border = border()
        ws.column_dimensions[get_column_letter(c)].width = w

    ws.row_dimensions[1].height = 25
    ws.freeze_panes = "A2"

    # サンプルデータ
    sample = [
        (1, "2024/01/20", "鈴木太郎", "-", 1, 42000),
        (1, "2024/01/20", "田中花子", "-", 2, 27000),
        (1, "2024/01/20", "佐藤一郎", "-", 3, 18000),
        (1, "2024/01/20", "山田次郎", "-", 4,  9000),
        (2, "2024/02/17", "鈴木太郎", "A", 2, 29000),
        (2, "2024/02/17", "田中花子", "A", 1, 38000),
        (2, "2024/02/17", "佐藤一郎", "A", 4,  8000),
        (2, "2024/02/17", "山田次郎", "A", 3, 21000),
        (2, "2024/02/17", "伊藤三郎", "B", 1, 44000),
        (2, "2024/02/17", "渡辺四郎", "B", 3, 20000),
        (2, "2024/02/17", "中村五郎", "B", 2, 32000),
        (2, "2024/02/17", "小林六郎", "B", 4,  4000),
    ]
    for r, row in enumerate(sample, 2):
        for c, val in enumerate(row, 1):
            cell = ws.cell(row=r, column=c, value=val)
            cell.border = border()
            cell.alignment = align()
            if c == 2:  # 日付
                cell.number_format = "yyyy/mm/dd"

    return ws


# ──────────────────────────────────────────────
# 参加者プルダウン用バリデーション
# ──────────────────────────────────────────────

def player_dropdown(target_cells):
    dv = DataValidation(
        type="list",
        formula1='設定!$A$2:$A$200',
        showDropDown=False,
        showErrorMessage=True,
        errorTitle="入力エラー",
        error="参加者リストから選択してください",
    )
    dv.add(target_cells)
    return dv


def rank_dropdown(target_cells):
    dv = DataValidation(
        type="list",
        formula1='"1,2,3,4"',
        showDropDown=False,
    )
    dv.add(target_cells)
    return dv


# ──────────────────────────────────────────────
# セッションシート共通ヘッダー
# ──────────────────────────────────────────────

def session_title_row(ws, title, row=1, cols=7):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=cols)
    cell = ws.cell(row=row, column=1, value=title)
    cell.font  = Font(bold=True, size=16, color="FFFFFF", name="游ゴシック")
    cell.fill  = fill(C["navy"])
    cell.alignment = align(wrap=True)
    ws.row_dimensions[row].height = 40


def session_date_row(ws, row=2):
    """日付・回数入力行"""
    ws.cell(row=row, column=1, value="日付").font = font(bold=True)
    ws.cell(row=row, column=1).fill = fill(C["gray_lt"])
    ws.cell(row=row, column=2).number_format = "yyyy/mm/dd"
    ws.cell(row=row, column=2).border = border()
    ws.cell(row=row, column=2).fill = fill(C["yellow"])

    ws.cell(row=row, column=4, value="回数").font = font(bold=True)
    ws.cell(row=row, column=4).fill = fill(C["gray_lt"])
    ws.cell(row=row, column=5).border = border()
    ws.cell(row=row, column=5).fill = fill(C["yellow"])
    ws.row_dimensions[row].height = 22


def table_header_row(ws, row, label, bg_color, cols=7):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=cols)
    cell = ws.cell(row=row, column=1, value=label)
    cell.font  = Font(bold=True, size=12, color="FFFFFF", name="游ゴシック")
    cell.fill  = fill(bg_color)
    cell.alignment = align()
    ws.row_dimensions[row].height = 28


def col_headers_row(ws, row, bg_color):
    headers = ["参加者", "順位", "点数（素点）", "ウマ", "収支", "メモ"]
    widths  = [20,       7,     13,            8,     10,    16  ]
    for c, (h, w) in enumerate(zip(headers, widths), 1):
        cell = ws.cell(row=row, column=c + 0, value=h)
        cell.font  = Font(bold=True, size=10, color="FFFFFF", name="游ゴシック")
        cell.fill  = fill(bg_color)
        cell.alignment = align()
        cell.border = border()
    ws.row_dimensions[row].height = 22


def player_row(ws, row, bg_color, row_in_table, session_row_ref_col5,
               uma_rank_formula, kaeshi=30000):
    """
    1行分のプレイヤー入力行を設定する
    列レイアウト: A=参加者, B=順位, C=点数, D=ウマ, E=収支, F=メモ
    """
    for c in range(1, 7):
        cell = ws.cell(row=row, column=c)
        cell.border = border()
        cell.fill   = fill(bg_color)
        cell.alignment = align()

    # 参加者プルダウン → caller側で DataValidation を追加
    ws.cell(row=row, column=1).alignment = align(h_align="left", indent=1)

    # ウマ (順位から自動計算)
    rank_cell = f"B{row}"
    ws.cell(row=row, column=4, value=uma_rank_formula.format(rank=rank_cell))

    # 収支 = (点数 - 返し点) / 1000 + ウマ
    ws.cell(row=row, column=5,
            value=f"=IF(C{row}=\"\",\"\",ROUND((C{row}-設定!$C$7)/1000+D{row},1))")
    ws.cell(row=row, column=5).number_format = "+0.0;-0.0;0.0"
    ws.cell(row=row, column=4).number_format = "+0;-0;0"

    ws.row_dimensions[row].height = 22


UMA_FORMULA = (
    '=IF({rank}="","",CHOOSE({rank},'
    '設定!$D$2,設定!$D$3,設定!$D$4,設定!$D$5))'
)


# ──────────────────────────────────────────────
# 4人用シート
# ──────────────────────────────────────────────

def build_4player_sheet(wb, sheet_name="第1回(4人用サンプル)"):
    ws = wb.create_sheet(sheet_name)

    # 列幅
    col_widths = [20, 7, 13, 8, 10, 16]
    for c, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(c)].width = w

    # ── タイトル
    session_title_row(ws, f"第X回 成績入力（4人）", row=1, cols=6)

    # ── 日付・回数
    session_date_row(ws, row=2)

    # ── 空行
    ws.row_dimensions[3].height = 8

    # ── テーブルヘッダー（4人は卓なし）
    table_header_row(ws, row=4, label="▶ 対局結果", bg_color=C["teal"], cols=6)
    col_headers_row(ws, row=5, bg_color=C["gray_hd"])

    # ── 4人分の行
    for i in range(4):
        r = 6 + i
        bg = C["teal_lt"] if i % 2 == 0 else C["white"]
        player_row(ws, r, bg_color=bg, row_in_table=i + 1,
                   session_row_ref_col5=5, uma_rank_formula=UMA_FORMULA)

    # ── 合計チェック行
    ws.row_dimensions[10].height = 8
    ws.merge_cells("A11:C11")
    ws.cell(row=11, column=1, value="点数合計（確認用）").font = font(bold=True, size=10)
    ws.cell(row=11, column=1).fill = fill(C["gray_lt"])
    ws.cell(row=11, column=4, value="=SUM(C6:C9)")
    ws.cell(row=11, column=4).border = border()
    ws.cell(row=11, column=4).number_format = "#,##0"
    ws.cell(row=11, column=4).fill = fill(C["yellow"])

    ws.merge_cells("A12:C12")
    ws.cell(row=12, column=1,
            value="※ 上の合計が 100,000 点になっていれば正確（30,000×4 - チップ精算分を除く）").font = Font(
        italic=True, size=9, color="666666", name="游ゴシック")
    ws.row_dimensions[12].height = 20

    ws.row_dimensions[13].height = 8

    # ── 集計ボタン説明
    ws.merge_cells("A14:F14")
    ws.cell(row=14, column=1,
            value='✅ 入力完了後：「集計に追加」マクロを実行するとマスターに反映されます').font = Font(
        bold=True, size=10, color="FFFFFF", name="游ゴシック")
    ws.cell(row=14, column=1).fill = fill(C["green"])
    ws.cell(row=14, column=1).alignment = align()
    ws.row_dimensions[14].height = 25

    # ── データバリデーション
    dv_player = player_dropdown("A6:A9")
    dv_rank   = rank_dropdown("B6:B9")
    ws.add_data_validation(dv_player)
    ws.add_data_validation(dv_rank)

    ws.freeze_panes = "A6"
    return ws


# ──────────────────────────────────────────────
# 8人用シート
# ──────────────────────────────────────────────

def build_8player_sheet(wb, sheet_name="第1回(8人用サンプル)"):
    ws = wb.create_sheet(sheet_name)

    col_widths = [20, 7, 13, 8, 10, 16]
    for c, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(c)].width = w

    # ── タイトル
    session_title_row(ws, "第X回 成績入力（8人 / A卓・B卓）", row=1, cols=6)

    # ── 日付・回数
    session_date_row(ws, row=2)

    ws.row_dimensions[3].height = 8

    # ═══════════════════════════
    # A 卓
    # ═══════════════════════════
    table_header_row(ws, row=4, label="🀇  A 卓", bg_color=C["a_dark"], cols=6)
    col_headers_row(ws, row=5, bg_color=C["a_dark"])

    for i in range(4):
        r = 6 + i
        bg = C["a_light"] if i % 2 == 0 else C["white"]
        player_row(ws, r, bg_color=bg, row_in_table=i + 1,
                   session_row_ref_col5=5, uma_rank_formula=UMA_FORMULA)

    # A卓 合計チェック
    ws.row_dimensions[10].height = 8
    ws.merge_cells("A11:C11")
    ws.cell(row=11, column=1, value="A卓 点数合計").font = font(bold=True, size=9, color="555555")
    ws.cell(row=11, column=1).fill = fill(C["gray_lt"])
    ws.cell(row=11, column=4, value="=SUM(C6:C9)").number_format = "#,##0"
    ws.cell(row=11, column=4).border = border()
    ws.cell(row=11, column=4).fill = fill(C["yellow"])

    ws.row_dimensions[12].height = 10

    # ═══════════════════════════
    # B 卓
    # ═══════════════════════════
    table_header_row(ws, row=13, label="🀗  B 卓", bg_color=C["b_dark"], cols=6)
    col_headers_row(ws, row=14, bg_color=C["b_dark"])

    for i in range(4):
        r = 15 + i
        bg = C["b_light"] if i % 2 == 0 else C["white"]
        player_row(ws, r, bg_color=bg, row_in_table=i + 1,
                   session_row_ref_col5=5, uma_rank_formula=UMA_FORMULA)

    # B卓 合計チェック
    ws.row_dimensions[19].height = 8
    ws.merge_cells("A20:C20")
    ws.cell(row=20, column=1, value="B卓 点数合計").font = font(bold=True, size=9, color="555555")
    ws.cell(row=20, column=1).fill = fill(C["gray_lt"])
    ws.cell(row=20, column=4, value="=SUM(C15:C18)").number_format = "#,##0"
    ws.cell(row=20, column=4).border = border()
    ws.cell(row=20, column=4).fill = fill(C["yellow"])

    ws.row_dimensions[21].height = 10

    # ── 集計ボタン説明
    ws.merge_cells("A22:F22")
    ws.cell(row=22, column=1,
            value='✅ 入力完了後：「集計に追加」マクロを実行するとマスターに反映されます').font = Font(
        bold=True, size=10, color="FFFFFF", name="游ゴシック")
    ws.cell(row=22, column=1).fill = fill(C["green"])
    ws.cell(row=22, column=1).alignment = align()
    ws.row_dimensions[22].height = 25

    # ── データバリデーション
    dv_player_a = player_dropdown("A6:A9")
    dv_rank_a   = rank_dropdown("B6:B9")
    dv_player_b = player_dropdown("A15:A18")
    dv_rank_b   = rank_dropdown("B15:B18")
    for dv in [dv_player_a, dv_rank_a, dv_player_b, dv_rank_b]:
        ws.add_data_validation(dv)

    ws.freeze_panes = "A6"
    return ws


# ──────────────────────────────────────────────
# マスターシート
# ──────────────────────────────────────────────

def build_master(wb):
    ws = wb.create_sheet("マスター", 0)

    # 列幅
    col_widths = [18, 10, 8, 9, 8, 8, 8, 8, 9, 9, 12, 11]
    for c, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(c)].width = w

    # ── タイトル
    ws.merge_cells("A1:L1")
    ws["A1"] = "麻雀部 成績マスター"
    ws["A1"].font  = Font(bold=True, size=18, color="FFFFFF", name="游ゴシック")
    ws["A1"].fill  = fill(C["navy"])
    ws["A1"].alignment = align()
    ws.row_dimensions[1].height = 48

    # ── 説明行
    ws.merge_cells("A2:L2")
    ws["A2"] = "※ 各回シートで「集計に追加」マクロを実行すると自動反映されます  |  参加者の追加は「設定」シートの A列へ"
    ws["A2"].font = Font(italic=True, size=9, color="555555", name="游ゴシック")
    ws["A2"].fill = fill("F0F4F8")
    ws["A2"].alignment = align()
    ws.row_dimensions[2].height = 18

    # ── ヘッダー行
    headers = [
        ("参加者",   "left"),
        ("参加\n回数", "center"),
        ("対局数",   "center"),
        ("平均\n順位","center"),
        ("1位\n回数","center"),
        ("2位\n回数","center"),
        ("3位\n回数","center"),
        ("4位\n回数","center"),
        ("トップ率", "center"),
        ("連対率",   "center"),
        ("合計収支", "center"),
        ("平均収支", "center"),
    ]
    ws.row_dimensions[3].height = 36
    for c, (h, ha) in enumerate(headers, 1):
        cell = ws.cell(row=3, column=c, value=h)
        cell.font  = Font(bold=True, size=10, color="FFFFFF", name="游ゴシック")
        cell.fill  = fill(C["teal"])
        cell.alignment = Alignment(horizontal=ha, vertical="center",
                                   wrap_text=True)
        cell.border = border()

    # ── 選手行（サンプル参加者 + 数式）
    # データ参照: データ!C = 参加者名, E = 順位, F = 点数, A = 回数, D = 卓
    for row_idx, player in enumerate(SAMPLE_PLAYERS, 4):
        ws.row_dimensions[row_idx].height = 22
        alt = row_idx % 2 == 0
        row_bg = "F5F8FF" if alt else "FFFFFF"

        p = f"$A{row_idx}"  # player name cell

        # A列: 参加者名
        cell = ws.cell(row=row_idx, column=1, value=player)
        cell.font  = Font(bold=True, size=11, name="游ゴシック")
        cell.fill  = fill(row_bg)
        cell.alignment = align(h_align="left", indent=1)
        cell.border = border()

        # 数式群
        formulas = [
            # B: 参加回数（ユニークな回数の数）
            f"=SUMPRODUCT((データ!$C$2:$C$2000={p})*1/COUNTIF(データ!$A$2:$A$2000,データ!$A$2:$A$2000)*(データ!$C$2:$C$2000={p}))",
            # C: 対局数
            f"=COUNTIF(データ!$C:$C,{p})",
            # D: 平均順位
            f'=IFERROR(AVERAGEIF(データ!$C:$C,{p},データ!$E:$E),"-")',
            # E: 1位回数
            f"=COUNTIFS(データ!$C:$C,{p},データ!$E:$E,1)",
            # F: 2位回数
            f"=COUNTIFS(データ!$C:$C,{p},データ!$E:$E,2)",
            # G: 3位回数
            f"=COUNTIFS(データ!$C:$C,{p},データ!$E:$E,3)",
            # H: 4位回数
            f"=COUNTIFS(データ!$C:$C,{p},データ!$E:$E,4)",
            # I: トップ率
            f'=IFERROR(COUNTIFS(データ!$C:$C,{p},データ!$E:$E,1)/COUNTIF(データ!$C:$C,{p}),"-")',
            # J: 連対率 (1位+2位)
            f'=IFERROR((COUNTIFS(データ!$C:$C,{p},データ!$E:$E,1)+COUNTIFS(データ!$C:$C,{p},データ!$E:$E,2))/COUNTIF(データ!$C:$C,{p}),"-")',
            # K: 合計収支 (点数ベース簡易計算: (素点-30000)/1000 + ウマ はデータに無いので収支列がないため、ここでは素点ベースで近似)
            f"=SUMIF(データ!$C:$C,{p},データ!$F:$F)",
            # L: 平均素点
            f'=IFERROR(AVERAGEIF(データ!$C:$C,{p},データ!$F:$F),"-")',
        ]

        num_formats = [
            "0",       # 参加回数
            "0",       # 対局数
            "0.00",    # 平均順位
            "0",       # 1位
            "0",       # 2位
            "0",       # 3位
            "0",       # 4位
            "0.0%",    # トップ率
            "0.0%",    # 連対率
            "#,##0",   # 合計
            "#,##0",   # 平均
        ]

        rank_colors = {4: "FFD700", 5: "C0C0C0", 6: "CD7F32"}  # 1-3位強調

        for c, (fml, nfmt) in enumerate(zip(formulas, num_formats), 2):
            cell = ws.cell(row=row_idx, column=c, value=fml)
            cell.border = border()
            cell.fill   = fill(row_bg)
            cell.alignment = align()
            cell.number_format = nfmt

    ws.freeze_panes = "B4"
    return ws


# ──────────────────────────────────────────────
# 使い方シート + VBAコード
# ──────────────────────────────────────────────

VBA_CODE = '''
' ============================================================
' 麻雀部成績管理 - VBAコード（Alt+F11 で貼り付け）
' ============================================================
' 標準モジュールに貼り付けて使ってください。
' その後 [開発タブ] > [マクロ] から実行できます。
' ボタンにマクロを割り当てると便利です。
' ============================================================

' ----------------------------------------------------------
' 4人用シートを新規作成（テンプレートをコピー）
' ----------------------------------------------------------
Sub 新規シート_4人()
    Dim num As String
    Dim dt  As String
    num = InputBox("回数を入力してください（例: 3）", "新規セッション作成")
    If num = "" Then Exit Sub
    dt = InputBox("日付を入力してください（例: 2024/03/15）", "日付入力", Format(Date, "yyyy/mm/dd"))
    If dt = "" Then Exit Sub

    Dim srcName As String: srcName = "第1回(4人用サンプル)"
    Dim newName As String: newName = "第" & num & "回(4人)"

    If SheetExists(newName) Then
        MsgBox "「" & newName & "」は既に存在します。", vbExclamation: Exit Sub
    End If

    Sheets(srcName).Copy After:=Sheets(Sheets.Count)
    With ActiveSheet
        .Name = newName
        .Range("B2").Value = CDate(dt)
        .Range("E2").Value = CLng(num)
        .Range("A6:F9").ClearContents
    End With
    MsgBox "「" & newName & "」を作成しました！", vbInformation
End Sub

' ----------------------------------------------------------
' 8人用シートを新規作成
' ----------------------------------------------------------
Sub 新規シート_8人()
    Dim num As String
    Dim dt  As String
    num = InputBox("回数を入力してください（例: 3）", "新規セッション作成")
    If num = "" Then Exit Sub
    dt = InputBox("日付を入力してください（例: 2024/03/15）", "日付入力", Format(Date, "yyyy/mm/dd"))
    If dt = "" Then Exit Sub

    Dim srcName As String: srcName = "第1回(8人用サンプル)"
    Dim newName As String: newName = "第" & num & "回(8人)"

    If SheetExists(newName) Then
        MsgBox "「" & newName & "」は既に存在します。", vbExclamation: Exit Sub
    End If

    Sheets(srcName).Copy After:=Sheets(Sheets.Count)
    With ActiveSheet
        .Name = newName
        .Range("B2").Value = CDate(dt)
        .Range("E2").Value = CLng(num)
        .Range("A6:F9").ClearContents
        .Range("A15:F18").ClearContents
    End With
    MsgBox "「" & newName & "」を作成しました！", vbInformation
End Sub

' ----------------------------------------------------------
' アクティブシートのデータをデータシートに集計
' ----------------------------------------------------------
Sub 集計に追加()
    Dim ws     As Worksheet: Set ws = ActiveSheet
    Dim wsData As Worksheet: Set wsData = Sheets("データ")

    Dim num  As Variant: num  = ws.Range("E2").Value
    Dim dt   As Variant: dt   = ws.Range("B2").Value

    If num = "" Or num = 0 Then
        MsgBox "回数（E2セル）を入力してください。", vbExclamation: Exit Sub
    End If
    If dt = "" Then
        MsgBox "日付（B2セル）を入力してください。", vbExclamation: Exit Sub
    End If

    ' 既存データを確認
    If Application.CountIf(wsData.Columns("A"), num) > 0 Then
        If MsgBox("第" & num & "回のデータは既に登録されています。上書きしますか？", _
                  vbYesNo + vbQuestion, "上書き確認") = vbNo Then Exit Sub
        ' 削除
        Dim i As Long
        For i = wsData.Cells(wsData.Rows.Count, "A").End(xlUp).Row To 2 Step -1
            If wsData.Cells(i, "A").Value = num Then wsData.Rows(i).Delete
        Next i
    End If

    Dim lastRow As Long
    Dim r As Integer

    ' ── 4人シート判定（B2行から下に4行 or 8行）
    Dim is8player As Boolean
    is8player = (InStr(ws.Name, "8人") > 0 Or ws.Range("A13").Value <> "")

    If is8player Then
        ' A卓 (行6-9)
        For r = 6 To 9
            Call WriteRow(wsData, num, dt, ws, r, "A")
        Next r
        ' B卓 (行15-18)
        For r = 15 To 18
            Call WriteRow(wsData, num, dt, ws, r, "B")
        Next r
    Else
        ' 4人 (行6-9)
        For r = 6 To 9
            Call WriteRow(wsData, num, dt, ws, r, "-")
        Next r
    End If

    MsgBox "集計に追加しました！  マスターシートを確認してください。", vbInformation
End Sub

' ----------------------------------------------------------
' 1行書き込みサブルーチン
' ----------------------------------------------------------
Private Sub WriteRow(wsData As Worksheet, num As Variant, dt As Variant, _
                     ws As Worksheet, r As Integer, taku As String)
    Dim nm As String: nm = ws.Cells(r, 1).Value
    If nm = "" Then Exit Sub

    Dim lastRow As Long
    lastRow = wsData.Cells(wsData.Rows.Count, "A").End(xlUp).Row + 1

    wsData.Cells(lastRow, 1).Value = num
    wsData.Cells(lastRow, 2).Value = dt
    wsData.Cells(lastRow, 2).NumberFormat = "yyyy/mm/dd"
    wsData.Cells(lastRow, 3).Value = nm
    wsData.Cells(lastRow, 4).Value = taku
    wsData.Cells(lastRow, 5).Value = ws.Cells(r, 2).Value  ' 順位
    wsData.Cells(lastRow, 6).Value = ws.Cells(r, 3).Value  ' 点数
End Sub

' ----------------------------------------------------------
' シート存在確認
' ----------------------------------------------------------
Private Function SheetExists(nm As String) As Boolean
    Dim s As Worksheet
    On Error Resume Next
    Set s = Sheets(nm)
    SheetExists = Not s Is Nothing
    On Error GoTo 0
End Function
'''


def build_howto(wb):
    ws = wb.create_sheet("使い方")

    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 60
    ws.column_dimensions["C"].width = 40

    # タイトル
    ws.merge_cells("A1:C1")
    ws["A1"] = "使い方ガイド"
    ws["A1"].font  = Font(bold=True, size=16, color="FFFFFF", name="游ゴシック")
    ws["A1"].fill  = fill(C["navy"])
    ws["A1"].alignment = align()
    ws.row_dimensions[1].height = 40

    steps = [
        ("", ""),
        ("【STEP 1】参加者を登録する", ""),
        ("", "「設定」シート（非表示）の A列に部員名を追加してください。"),
        ("", "→ シートタブを右クリック ▶ [再表示] ▶ 設定 を選択"),
        ("", ""),
        ("【STEP 2】各回のシートを作成する", ""),
        ("", "・4人の場合：「新規シート_4人」マクロを実行"),
        ("", "・8人の場合：「新規シート_8人」マクロを実行"),
        ("", "→ [開発] タブ ▶ [マクロ] ▶ 実行  (または割り当てたボタンを押す)"),
        ("", ""),
        ("【STEP 3】結果を入力する", ""),
        ("", "・参加者：プルダウンから選択"),
        ("", "・順位：1〜4 をプルダウンから選択"),
        ("", "・点数：素点を入力（例: 42000）"),
        ("", "・ウマ・収支 は自動計算されます"),
        ("", "・8人の場合、A卓とB卓 に分けて入力 → 同卓が一目でわかります"),
        ("", ""),
        ("【STEP 4】集計に追加する", ""),
        ("", "「集計に追加」マクロを実行 → 「マスター」シートに自動反映"),
        ("", ""),
        ("【ウマ設定の変更】", ""),
        ("", "「設定」シート D2〜D5 の数値を変更してください（デフォルト: 20/10/-10/-20）"),
        ("", "返し点は 設定!C7（デフォルト: 30000）"),
        ("", ""),
        ("【VBAの追加方法】", ""),
        ("", "① Excel で Alt+F11 を押す"),
        ("", "② 左ペインでブック名を右クリック ▶ 挿入 ▶ 標準モジュール"),
        ("", "③ 下のコードボックス内のコードを貼り付ける"),
        ("", "④ Alt+F11 で戻る → [開発] タブ ▶ [マクロ] で実行できます"),
        ("", ""),
    ]

    for r, (title, desc) in enumerate(steps, 2):
        ws.row_dimensions[r].height = 18
        if title.startswith("【"):
            cell_t = ws.cell(row=r, column=2, value=title)
            cell_t.font = Font(bold=True, size=11, color=C["navy"], name="游ゴシック")
            cell_t.fill = fill("E8F0FE")
        elif title:
            ws.cell(row=r, column=2, value=title)
        if desc:
            cell_d = ws.cell(row=r, column=2, value=desc)
            cell_d.font = Font(size=10, name="游ゴシック")
            cell_d.alignment = Alignment(horizontal="left", vertical="center", indent=2)

    # VBAコード表示
    r_start = len(steps) + 3
    ws.merge_cells(f"A{r_start}:C{r_start}")
    ws.cell(row=r_start, column=1, value="▼ VBAコード（以下をコピーして標準モジュールに貼り付け）")
    ws.cell(row=r_start, column=1).font = Font(bold=True, size=11, color="FFFFFF", name="游ゴシック")
    ws.cell(row=r_start, column=1).fill = fill(C["teal"])
    ws.cell(row=r_start, column=1).alignment = align()
    ws.row_dimensions[r_start].height = 28

    r_code = r_start + 1
    ws.merge_cells(f"A{r_code}:C{r_code + 80}")
    cell_vba = ws.cell(row=r_code, column=1, value=VBA_CODE.strip())
    cell_vba.font = Font(size=9, name="Courier New", color="1A1A2E")
    cell_vba.fill = fill("F8F8F2")
    cell_vba.alignment = Alignment(horizontal="left", vertical="top",
                                    wrap_text=True)
    ws.row_dimensions[r_code].height = 15

    return ws


# ──────────────────────────────────────────────
# メイン
# ──────────────────────────────────────────────

def main():
    wb = Workbook()
    default = wb.active
    wb.remove(default)

    # シート作成順（マスターが最初になるよう最後に insert index=0 で作る）
    build_config(wb)    # hidden
    build_data(wb)      # hidden
    build_master(wb)    # index 0 で先頭に
    build_4player_sheet(wb, "第1回(4人用サンプル)")
    build_8player_sheet(wb, "第1回(8人用サンプル)")
    build_howto(wb)

    # タブ色設定
    wb["マスター"].sheet_properties.tabColor           = "1B3A6B"
    wb["第1回(4人用サンプル)"].sheet_properties.tabColor = "1565C0"
    wb["第1回(8人用サンプル)"].sheet_properties.tabColor = "BF360C"
    wb["使い方"].sheet_properties.tabColor             = "2E7D32"

    output = "/home/user/claude-test/麻雀部成績管理.xlsx"
    wb.save(output)
    print(f"✅ 作成完了: {output}")


if __name__ == "__main__":
    main()
