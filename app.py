import json
import matplotlib
matplotlib.use('Agg')  # Flaskとの互換のためGUIを使わない
import matplotlib.pyplot as plt
from matplotlib import rcParams
import jpholiday
import datetime
import os
from flask import Flask, render_template

# ✅ 日本語フォント（macOS用）
rcParams['font.family'] = 'Hiragino Sans'

# Flaskアプリ初期化
app = Flask(__name__)

# データ読み込み
with open("data/prices.json", "r", encoding="utf-8") as f:
    price_data = json.load(f)

# 日付リスト（180日分）
today = datetime.date.today()
date_list = [today + datetime.timedelta(days=i) for i in range(180)]
date_str_list = [d.strftime("%Y-%m-%d") for d in date_list]
date_label_list = [d.strftime("%m/%d") for d in date_list]

# X軸のラベル色設定（日曜・祝日：赤、土曜：青、平日：黒）
label_colors = []
for d in date_list:
    if jpholiday.is_holiday(d) or d.weekday() == 6:  # 日曜または祝日
        label_colors.append("red")
    elif d.weekday() == 5:  # 土曜
        label_colors.append("blue")
    else:
        label_colors.append("black")

# グラフ画像保存フォルダ
os.makedirs("static", exist_ok=True)
graph_files = []

# 30日ごとに6枚のグラフを生成
for i in range(6):
    start = i * 30
    end = (i + 1) * 30

    plt.figure(figsize=(14, 5))

    for hotel_name, prices in price_data.items():
        y = [prices.get(date_str_list[j]) for j in range(start, end)]
        plt.plot(date_label_list[start:end], y, marker="o", label=hotel_name)

    plt.title(f"小樽ホテル価格推移（日数 {start + 1}〜{end}）")
    plt.xlabel("日付")
    plt.ylabel("最安価格（円）")
    plt.xticks(rotation=45)

    # X軸のラベルに色を設定
    ax = plt.gca()
    for j, ticklabel in enumerate(ax.get_xticklabels()):
        ticklabel.set_color(label_colors[start + j])

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    filename = f"static/graph{i+1}.png"
    plt.savefig(filename)
    plt.close()
    graph_files.append("/" + filename)

# ルーティング
@app.route("/")
def index():
    return render_template("index.html", graphs=graph_files)

from flask import send_file

@app.route("/data")
def data():
    return send_file("data/prices.json", mimetype="application/json")


# アプリ起動
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    