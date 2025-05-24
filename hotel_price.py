import requests
import datetime
import time
import matplotlib.pyplot as plt

url = "https://app.rakuten.co.jp/services/api/Travel/VacantHotelSearch/20170426"
app_id = "1088217021824693179"
hotel_no = 8674

dates = []
prices = []

today = datetime.date.today()
for i in range(30):  # 30日分
    checkin_date = today + datetime.timedelta(days=i)
    params = {
        "applicationId": app_id,
        "hotelNo": hotel_no,
        "checkinDate": checkin_date.strftime("%Y-%m-%d"),
        "checkoutDate": (checkin_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
        "adultNum": 1,
        "format": "json"
    }

    response = requests.get(url, params=params)
    print(f"📅 {checkin_date.strftime('%Y-%m-%d')} の結果:")

    if response.status_code == 200:
        try:
            data = response.json()
            hotels = data.get("hotels", [])
            all_prices = []

            for hotel in hotels:
                for item in hotel.get("hotel", []):
                    if "roomInfo" in item:
                        for room in item["roomInfo"]:
                            if "dailyCharge" in room:
                                price = room["dailyCharge"].get("rakutenCharge")
                                if price:
                                    all_prices.append(price)

            if all_prices:
                min_price = min(all_prices)
                print(f"✅ 最安料金: {min_price}円\n")
                dates.append(checkin_date.strftime("%m/%d"))
                prices.append(min_price)
            else:
                print("空室なし or 金額情報が取得できませんでした\n")

        except Exception as e:
            print(f"データ解析中にエラーが発生しました: {e}\n")
    else:
        print(f"エラー発生：{response.status_code}\n")

    time.sleep(1)

# ✅ グラフ描画
plt.figure(figsize=(12, 6))
plt.plot(dates, prices, marker='o')
plt.title("小樽グリーンホテル 価格推移（30日間）")
plt.xlabel("日付")
plt.ylabel("最安価格（円）")
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()

