"""Scrape groundwater ordinance index from env.go.jp and emit an xlsx.

Source: https://www.env.go.jp/water/jiban/sui/index.html

Pulls every page that the index links one level down, parses each as a list of
ordinances belonging to a prefecture / municipality, and writes a single
worksheet with the columns: 都道府県, 市町村, 条例等の名称, URL.

The URL cell shows the literal text "URL" and is hyperlinked to the ordinance
target. Rows are emitted one per ordinance (split when a municipality has
multiple).
"""

from __future__ import annotations

import re
import sys
import time
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

INDEX_URL = "https://www.env.go.jp/water/jiban/sui/index.html"
OUTPUT_PATH = "groundwater_ordinances.xlsx"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

PREFECTURES = [
    "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
    "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
    "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
    "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県",
]


@dataclass
class Row:
    prefecture: str
    municipality: str
    name: str
    url: str


def fetch(url: str) -> str:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or resp.encoding
    return resp.text


def detect_prefecture(text: str) -> str | None:
    for pref in PREFECTURES:
        if pref in text:
            return pref
    # Tolerate truncated forms (e.g. "東京", "大阪").
    for pref in PREFECTURES:
        short = re.sub(r"[都道府県]$", "", pref)
        if short and short in text:
            return pref
    return None


def collect_child_pages(index_html: str) -> list[tuple[str, str]]:
    """Return (label, absolute_url) for each link one level down from index."""
    soup = BeautifulSoup(index_html, "html.parser")
    seen: dict[str, str] = {}
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("#") or href.startswith("mailto:"):
            continue
        absolute = urljoin(INDEX_URL, href)
        # Only same-host pages count as "one level down".
        if urlparse(absolute).netloc != urlparse(INDEX_URL).netloc:
            continue
        if absolute == INDEX_URL:
            continue
        label = a.get_text(" ", strip=True)
        seen.setdefault(absolute, label)
    return list(seen.items())


def parse_child_page(url: str, html: str) -> list[Row]:
    """Extract ordinance rows from a child page.

    Strategy: find tables; for each row, pick the first non-empty cell as
    locality, the cell containing an <a> as the ordinance name + URL. Fall
    back to harvesting <li> entries when no table is present.
    """
    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text(" ", strip=True)
    pref_from_page = detect_prefecture(page_text) or ""

    rows: list[Row] = []

    def push(locality: str, name: str, link: str) -> None:
        if not name or not link:
            return
        absolute = urljoin(url, link)
        pref = detect_prefecture(locality) or pref_from_page or ""
        muni = locality
        if pref and locality.startswith(pref):
            muni = locality[len(pref):].strip(" 　,、")
        muni = muni or "-"
        rows.append(Row(pref, muni, name.strip(), absolute))

    tables = soup.find_all("table")
    if tables:
        for table in tables:
            for tr in table.find_all("tr"):
                cells = tr.find_all(["td", "th"])
                if not cells:
                    continue
                texts = [c.get_text(" ", strip=True) for c in cells]
                links = [c.find("a", href=True) for c in cells]
                anchor = next((a for a in links if a is not None), None)
                if anchor is None:
                    continue
                name = anchor.get_text(" ", strip=True)
                href = anchor["href"]
                non_link_texts = [
                    t for t, a in zip(texts, links) if a is None and t
                ]
                locality = non_link_texts[0] if non_link_texts else ""
                push(locality, name, href)
    else:
        for li in soup.find_all("li"):
            anchor = li.find("a", href=True)
            if not anchor:
                continue
            name = anchor.get_text(" ", strip=True)
            push("", name, anchor["href"])

    return rows


def write_xlsx(rows: list[Row], path: str) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "地下水関連条例等"
    headers = ["都道府県", "市町村", "条例等の名称", "URL"]
    ws.append(headers)
    for col, _ in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="D9E1F2")
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for r in rows:
        ws.append([r.prefecture, r.municipality or "-", r.name, "URL"])
        url_cell = ws.cell(row=ws.max_row, column=4)
        url_cell.hyperlink = r.url
        url_cell.font = Font(color="0563C1", underline="single")

    widths = [12, 20, 60, 8]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = w
    ws.freeze_panes = "A2"

    wb.save(path)


def main() -> int:
    print(f"Fetching index: {INDEX_URL}")
    index_html = fetch(INDEX_URL)
    children = collect_child_pages(index_html)
    print(f"Found {len(children)} candidate child pages")

    all_rows: list[Row] = []
    for url, label in children:
        try:
            time.sleep(0.5)
            html = fetch(url)
        except Exception as exc:
            print(f"  skip {url}: {exc}")
            continue
        page_rows = parse_child_page(url, html)
        if page_rows:
            print(f"  {label or url}: {len(page_rows)} rows")
        all_rows.extend(page_rows)

    pref_index = {p: i for i, p in enumerate(PREFECTURES)}
    all_rows.sort(key=lambda r: (pref_index.get(r.prefecture, 99), r.municipality, r.name))

    write_xlsx(all_rows, OUTPUT_PATH)
    print(f"Wrote {len(all_rows)} rows -> {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
