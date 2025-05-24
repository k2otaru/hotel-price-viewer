import requests
import datetime
import time
import json
import csv
import os

# 保存フォルダの確認と作成
os.makedirs("data", exist_ok=True)

# ホテル情報（10施設）
hotels = [
    {"name": "小樽グリーンホテル", "hotel_no": 8674},
    {"name": "ドーミーインPREMIUM小樽", "hotel_no": 76876},
    {"name": "ビジネスホテル大幸", "hotel_no": 165775},
    {"name": "はなえみ", "hotel_no": 139427},
    {"name": "朝里川温泉ホテル", "hotel_no": 183875},
    {"name": "グリッズプレミアム小樽", "hotel_no": 183954},
    {"name": "トリフィート小樽運河", "hotel_no": 166148},
    {"name": "アルファベッドイン小樽駅前", "hotel_no": 181196},
    {"name": "ファミグリーン小樽", "hotel_no": 180783},
    {"name": "ホテルノルド", "hotel_no": 3119}
]

# API設定
APP_ID = "1088217021824693179"
URL = "https://app.rakuten.co.jp/services/api/Travel/VacantHotelSearch/20170426"

# 調査期間：180日
today = datetime.date.today()
dates = [today + datetime.timedelta(days=i) for i in range(180)]

# データ格納構造
price_data = {}

# 各ホテルごとに価格を取得
for hotel in hotels:
    hotel_name = hotel["name"]
    hotel_no = hotel["hotel_no"]
    print(f"📥 取得開始：{hotel_name}")
    price_data[hotel_name] = {}

    for d in dates:
        date_str = d.strftime("%Y-%m-%d")
        params = {
            "applicationId": APP_ID,
            "hotelNo": hotel_no,
            "checkinDate": date_str,
            "checkoutDate": (d + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
            "adultNum": 1,
            "format": "json"
        }

        try:
            response = requests.get(URL, params=params)
            if response.status_code == 200:
                data = response.json()
                hotels_data = data.get("hotels", [])
                prices = []

                for h in hotels_data:
                    for item in h.get("hotel", []):
                        if "roomInfo" in item:
                            for room in item["roomInfo"]:
                                if "dailyCharge" in room:
                                    charge = room["dailyCharge"].get("rakutenCharge")
                                    if charge:
                                        prices.append(charge)

                min_price = min(prices) if prices else None
                price_data[hotel_name][date_str] = min_price
                print(f"✅ {hotel_name} {date_str} 最安値: {min_price if min_price else 'なし'}")
            else:
                print(f"⚠️ {hotel_name} {date_str} 取得失敗（status: {response.status_code}）")
                price_data[hotel_name][date_str] = None

        except Exception as e:
            print(f"❌ {hotel_name} {date_str} エラー: {e}")
            price_data[hotel_name][date_str] = None

        time.sleep(1)

# JSONとして保存
json_path = "data/prices.json"
with open(json_path, "w", encoding="utf-8") as jf:
    json.dump(price_data, jf, ensure_ascii=False, indent=2)
print(f"💾 JSON保存完了：{json_path}（ホテル数: {len(price_data)}）")

# CSVとして保存
csv_path = "data/prices.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as cf:
    writer = csv.writer(cf)
    writer.writerow(["date", "hotel_name", "price"])
    for hotel_name, date_prices in price_data.items():
        for date, price in date_prices.items():
            writer.writerow([date, hotel_name, price])
print(f"💾 CSV保存完了：{csv_path}（行数: {sum(len(v) for v in price_data.values())}）")

print("✅ 価格データの取得と保存がすべて完了しました。")

