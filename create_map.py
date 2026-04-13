#!/usr/bin/env python3
"""
企業所在地マップ生成スクリプト
住友理工(株)小牧製作所を中心とした企業地図を作成します
"""

import folium
import time
import math
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# ===== データ定義 =====
companies = [
    {
        "name": "株式会社サカイフィールド",
        "address": "愛知県常滑市西阿野古池255",
        "row": 2,
        "is_center": False,
        "color": "red",
    },
    {
        "name": "極東開発工業(株)名古屋工場",
        "address": "愛知県小牧市東田中字松本1375",
        "row": 34,
        "is_center": False,
        "color": "blue",
    },
    {
        "name": "住友理工(株)小牧製作所",
        "address": "愛知県小牧市東三丁目1番地",
        "row": 55,
        "is_center": True,
        "color": "green",
    },
    {
        "name": "(株)チェリオ中部",
        "address": "愛知県小牧市大字河内屋新田字下岩倉入510-1",
        "row": 67,
        "is_center": False,
        "color": "blue",
    },
    {
        "name": "日本特殊陶業(株)小牧工場",
        "address": "愛知県小牧市大字岩崎2808",
        "row": 124,
        "is_center": False,
        "color": "blue",
    },
    {
        "name": "間口東海(株)小牧セットセンター出張所",
        "address": "愛知県小牧市大字東田中字南新田1605番地1",
        "row": 145,
        "is_center": False,
        "color": "blue",
    },
    {
        "name": "丸菱工業(株)",
        "address": "愛知県小牧市大字本庄字山ノ内1251-3",
        "row": 148,
        "is_center": False,
        "color": "blue",
    },
    {
        "name": "(株)両口屋是清小牧工場",
        "address": "愛知県小牧市大字間々字浦通り18",
        "row": 158,
        "is_center": False,
        "color": "blue",
    },
]

# ===== ジオコーディング =====
print("住所のジオコーディングを実行中...")
geolocator = Nominatim(user_agent="komaki_company_map_v1")

# フォールバック座標（手動で調査した概算値）
fallback_coords = {
    "株式会社サカイフィールド":              (34.9178, 136.8695),
    "極東開発工業(株)名古屋工場":            (35.2983, 136.9248),
    "住友理工(株)小牧製作所":               (35.2890, 136.9113),
    "(株)チェリオ中部":                     (35.2848, 136.9018),
    "日本特殊陶業(株)小牧工場":             (35.3128, 136.8968),
    "間口東海(株)小牧セットセンター出張所":  (35.2970, 136.9238),
    "丸菱工業(株)":                         (35.2762, 136.9082),
    "(株)両口屋是清小牧工場":               (35.3088, 136.9103),
}

for company in companies:
    name = company["name"]
    address = company["address"]
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            company["lat"] = location.latitude
            company["lon"] = location.longitude
            print(f"  OK  {name}: ({location.latitude:.4f}, {location.longitude:.4f})")
        else:
            company["lat"], company["lon"] = fallback_coords[name]
            print(f"  FB  {name}: フォールバック座標使用")
    except Exception as e:
        company["lat"], company["lon"] = fallback_coords[name]
        print(f"  FB  {name}: エラー → フォールバック使用 ({e})")
    time.sleep(1.2)  # Nominatim利用制限対応

# ===== 中心点（住友理工）の取得 =====
center_company = next(c for c in companies if c["is_center"])
center_lat = center_company["lat"]
center_lon = center_company["lon"]
print(f"\n中心座標: {center_lat:.4f}, {center_lon:.4f} ({center_company['name']})")

# ===== 距離計算 =====
for company in companies:
    if company["is_center"]:
        company["distance_km"] = 0.0
    else:
        dist = geodesic(
            (center_lat, center_lon),
            (company["lat"], company["lon"])
        ).km
        company["distance_km"] = dist

# 最大距離を確認してズームレベルを決定
max_dist = max(c["distance_km"] for c in companies if not c["is_center"])
print(f"\n最大距離: {max_dist:.2f} km")

# サカイフィールド（常滑市）は遠いので除外した範囲も確認
max_dist_local = max(
    c["distance_km"] for c in companies
    if not c["is_center"] and c["name"] != "株式会社サカイフィールド"
)
print(f"小牧市内最大距離: {max_dist_local:.2f} km")

# ===== ズームレベル決定 =====
# 全企業を含む場合は広域、小牧市内のみなら詳細
zoom_start = 12  # 全企業表示（常滑市含む）

# ===== Foliumマップ作成 =====
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=zoom_start,
    tiles="OpenStreetMap",
)

# ----- 距離円を追加（中心からの目安距離） -----
circle_configs = [
    (1,  "#2ECC71", "1km圏"),
    (3,  "#3498DB", "3km圏"),
    (5,  "#E67E22", "5km圏"),
    (10, "#E74C3C", "10km圏"),
    (30, "#9B59B6", "30km圏"),
]

for radius_km, color, label in circle_configs:
    folium.Circle(
        location=[center_lat, center_lon],
        radius=radius_km * 1000,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.04,
        opacity=0.6,
        weight=1.5,
        tooltip=label,
    ).add_to(m)

# ----- マーカー追加 -----
for company in companies:
    lat = company["lat"]
    lon = company["lon"]
    name = company["name"]
    dist = company["distance_km"]
    address = company["address"]
    is_center = company["is_center"]

    # ポップアップHTML
    popup_html = f"""
    <div style="font-family: 'Meiryo', sans-serif; min-width: 220px;">
        <h4 style="margin:0 0 6px 0; color:#2C3E50;">{name}</h4>
        <p style="margin:2px 0; font-size:12px; color:#555;">📍 {address}</p>
        <p style="margin:4px 0; font-size:13px;">
            <b>中心からの距離:</b>
            {'<span style="color:green;">中心地点</span>' if is_center else f'<span style="color:#E74C3C;"><b>{dist:.2f} km</b></span>'}
        </p>
    </div>
    """

    if is_center:
        # 中心マーカー（星型）
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"★ {name}（中心）",
            icon=folium.Icon(color="green", icon="star", prefix="fa"),
        ).add_to(m)
    else:
        color = "red" if name == "株式会社サカイフィールド" else "cadetblue"
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{name}  ({dist:.1f} km)",
            icon=folium.Icon(color=color, icon="building", prefix="fa"),
        ).add_to(m)

# ----- 凡例パネル -----
legend_html = """
<div style="
    position: fixed; bottom: 30px; left: 30px;
    z-index: 1000; background: white;
    border: 2px solid #ccc; border-radius: 8px;
    padding: 12px 16px; font-family: 'Meiryo', sans-serif;
    font-size: 12px; box-shadow: 2px 2px 6px rgba(0,0,0,0.2);
    min-width: 200px;
">
<b style="font-size:13px;">凡例</b><br><br>
<i class="fa fa-star" style="color:green;"></i> 住友理工(株)小牧製作所（中心）<br><br>
<i class="fa fa-building" style="color:cadetblue;"></i> 小牧市内企業<br>
<i class="fa fa-building" style="color:red;"></i> 常滑市企業<br><br>
<b>距離円</b><br>
<span style="color:#2ECC71;">●</span> 1km &nbsp;
<span style="color:#3498DB;">●</span> 3km &nbsp;
<span style="color:#E67E22;">●</span> 5km<br>
<span style="color:#E74C3C;">●</span> 10km &nbsp;
<span style="color:#9B59B6;">●</span> 30km
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# ----- 距離一覧テーブルパネル -----
sorted_companies = sorted(companies, key=lambda c: c["distance_km"])
table_rows = ""
for c in sorted_companies:
    dist_str = "中心" if c["is_center"] else f"{c['distance_km']:.2f} km"
    bg = "#E8F8F5" if c["is_center"] else "white"
    table_rows += f"""
    <tr style="background:{bg};">
        <td style="padding:3px 6px;">{c['name']}</td>
        <td style="padding:3px 6px; text-align:right; font-weight:bold;">{dist_str}</td>
    </tr>
    """

table_html = f"""
<div style="
    position: fixed; top: 80px; right: 15px;
    z-index: 1000; background: white;
    border: 2px solid #ccc; border-radius: 8px;
    padding: 10px 14px; font-family: 'Meiryo', sans-serif;
    font-size: 11px; box-shadow: 2px 2px 6px rgba(0,0,0,0.2);
    max-width: 340px;
">
<b style="font-size:13px;">中心からの距離一覧</b>
<table style="border-collapse:collapse; margin-top:6px; width:100%;">
<tr style="background:#2C3E50; color:white;">
    <th style="padding:4px 6px; text-align:left;">企業名</th>
    <th style="padding:4px 6px; text-align:right;">距離</th>
</tr>
{table_rows}
</table>
<p style="margin:6px 0 0 0; color:#888; font-size:10px;">※中心: 住友理工(株)小牧製作所</p>
</div>
"""
m.get_root().html.add_child(folium.Element(table_html))

# ===== 保存 =====
output_file = "/home/user/claude-test/komaki_company_map.html"
m.save(output_file)
print(f"\n地図を保存しました: {output_file}")

# ===== 距離サマリー表示 =====
print("\n" + "="*60)
print("企業所在地 距離一覧（住友理工小牧製作所からの直線距離）")
print("="*60)
for c in sorted_companies:
    if c["is_center"]:
        print(f"  ★ {c['name']:30s}  【中心】")
    else:
        bar = "█" * int(c["distance_km"] / max_dist * 30)
        print(f"    {c['name']:30s}  {c['distance_km']:6.2f} km  {bar}")
print("="*60)
print(f"\n地図の推奨ズームレベル: {zoom_start}")
print(f"  - 全企業表示（常滑市含む）: zoom 10-11")
print(f"  - 小牧市内集中表示: zoom 12-13")
print(f"  - 詳細表示: zoom 14-15")
