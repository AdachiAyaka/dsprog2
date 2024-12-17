import flet as ft
import requests
import sqlite3

# SQLite データベースのセットアップ
def setup_database():
    """データベースのセットアップ"""
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()
    # 地域テーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS regions (
        region_id INTEGER PRIMARY KEY,
        region_name TEXT NOT NULL
    );
    """)

    # 都道府県テーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prefectures (
        prefecture_id TEXT PRIMARY KEY,
        region_id INTEGER,
        prefecture_name TEXT NOT NULL,
        FOREIGN KEY (region_id) REFERENCES regions (region_id)
    );
    """)

    # 天気予報テーブル
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather_forecasts (
        forecast_id INTEGER PRIMARY KEY AUTOINCREMENT,
        prefecture_id TEXT,
        date TEXT,
        forecast TEXT,
        FOREIGN KEY (prefecture_id) REFERENCES prefectures (prefecture_id)
    );
    """)
    conn.commit()
    return conn

# 地域と都道府県データの初期投入
def insert_regions_and_prefectures(conn, area_list):
    cursor = conn.cursor()
    for region_id, (region_name, data) in enumerate(area_list.items(), start=1):
        cursor.execute("INSERT OR IGNORE INTO regions (region_id, region_name) VALUES (?, ?)", (region_id, region_name))
        for prefecture_code, prefecture_name in data["prefectures"].items():
            cursor.execute(
                "INSERT OR IGNORE INTO prefectures (prefecture_id, region_id, prefecture_name) VALUES (?, ?, ?)",
                (prefecture_code, region_id, prefecture_name)
            )
    conn.commit()

# 天気データを保存する関数
def save_weather_to_db(conn, prefecture_code, weather_data):
    try:
        cursor = conn.cursor()
        areas = weather_data[0]["timeSeries"][0]["areas"]
        for area in areas:
            forecast = area['weathers'][0]
            date = weather_data[0]["timeSeries"][0]["timeDefines"][0]
            cursor.execute(
                "INSERT INTO weather_forecasts (prefecture_id, date, forecast) VALUES (?, ?, ?)",
                (prefecture_code, date, forecast)
            )
        conn.commit()
    except Exception as e:
        print(f"Error saving weather data: {e}")

# 気象庁APIから天気データを取得する関数
def get_weather_data(prefecture_code: str):
    """指定された都道府県コードで天気予報を取得する関数"""
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{prefecture_code}.json"
    try:
        # APIへリクエストを送信
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json() # 正常応答の場合、JSONデータを返す
        else:
            print(f"Error: {response.status_code} - {response.reason}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}") # リクエストが失敗した場合のエラー処理
        return None

# 気象庁の地域リストを辞書で定義
# 地域とそれに対応する都道府県コード・名称を含む
area_list = {
    "北海道地方": {
        "code": "010100",
        "prefectures": {
            "011000": "宗谷地方",
            "012000": "上川・留萌地方",
            "013000": "網走・北見・紋別地方",
            "014030": "十勝地方",
            "014100": "釧路・根室地方",
            "015000": "胆振・日高地方",
            "016000": "石狩・空知・後志地方",
            "017000": "渡島・檜山地方"
        }
    },
    "東北地方": {
        "code": "010200",
        "prefectures": {
            "020000": "青森県",
            "030000": "岩手県",
            "040000": "宮城県",
            "050000": "秋田県",
            "060000": "山形県",
            "070000": "福島県"
        }
    },
    "関東甲信地方": {
        "code": "010300",
        "prefectures": {
            "080000": "茨城県",
            "090000": "栃木県",
            "100000": "群馬県",
            "110000": "埼玉県",
            "120000": "千葉県",
            "130000": "東京都",
            "140000": "神奈川県",
            "190000": "山梨県",
            "200000": "長野県"
        }
    },
    "東海地方": {
        "code": "010400",
        "prefectures": {
            "210000": "岐阜県",
            "220000": "静岡県",
            "230000": "愛知県",
            "240000": "三重県"
        }
    },
    "北陸地方": {
        "code": "010500",
        "prefectures": {
            "150000": "新潟県",
            "160000": "富山県",
            "170000": "石川県",
            "180000": "福井県"
        }
    },
    "近畿地方": {
        "code": "010600",
        "prefectures": {
            "250000": "滋賀県",
            "260000": "京都府",
            "270000": "大阪府",
            "280000": "兵庫県",
            "290000": "奈良県",
            "300000": "和歌山県"
        }
    },
    "中国地方（山口県を除く）": {
        "code": "010700",
        "prefectures": {
            "310000": "鳥取県",
            "320000": "島根県",
            "330000": "岡山県",
            "340000": "広島県"
        }
    },
    "四国地方": {
        "code": "010800",
        "prefectures": {
            "360000": "徳島県",
            "370000": "香川県",
            "380000": "愛媛県",
            "390000": "高知県"
        }
    },
    "九州北部地方（山口県を含む）": {
        "code": "010900",
        "prefectures": {
            "350000": "山口県",
            "400000": "福岡県",
            "410000": "佐賀県",
            "420000": "長崎県",
            "430000": "熊本県",
            "440000": "大分県"
        }
    },
    "九州南部・奄美地方": {
        "code": "011000",
        "prefectures": {
            "450000": "宮崎県",
            "460040": "奄美地方",
            "460100": "鹿児島県（奄美地方除く）"
        }
    },
    "沖縄地方": {
        "code": "011100",
        "prefectures": {
            "471000": "沖縄本島地方",
            "472000": "大東島地方",
            "473000": "宮古島地方",
            "474000": "八重山地方"
        }
    }
}

# メイン関数 - アプリの構成を設定
def main(page: ft.Page):
    # SQLite データベースのセットアップ
    conn = setup_database()
    insert_regions_and_prefectures(conn, area_list)

    page.title = "天気予報アプリ"
    page.spacing = 0
    page.padding = 0
    page.window_width = 900  # ウィンドウ幅
    page.window_height = 800  # ウィンドウ高さ
    page.window_resizable = True  # サイズ変更可能

    # 天気表示用のテキストウィジェット
    weather_display = ft.Text("天気情報がここに表示されます", expand=True)
    expansion_tiles = ft.Column()

    # 都道府県を表示するためのエリア
    expansion_tiles = ft.Column()

    # 地域が選択されたときの処理
    def update_region_tiles(selected_index):
        # 選択された地域のインデックスから地域情報を取得
        selected_region = list(area_list.keys())[selected_index]
        prefectures = area_list[selected_region]["prefectures"]
        
        # 選択された地域の都道府県リストを表示
        expansion_tiles.controls = [
            ft.ExpansionTile(
                title=ft.Text(selected_region),  # 地域名をタイトルに表示
                subtitle=ft.Text("都道府県を選択してください"), # サブタイトル
                affinity=ft.TileAffinity.LEADING, # タイルの配置
                initially_expanded=True, # 初期状態で展開
                text_color=ft.colors.BLUE, 
                collapsed_text_color=ft.colors.BLUE,
                controls=[
                    # 都道府県名のリストを作成
                    ft.ListTile(
                        title=ft.Text(prefecture_name), # 都道府県名を表示
                        on_click=lambda e, code=prefecture_code: update_weather(code), # クリック時の処理
                    )
                    for prefecture_code, prefecture_name in prefectures.items()
                ],
            )
        ]
        page.update()

    # 天気情報を更新する関数
    def update_weather(prefecture_code):
        # 天気データを取得
        weather_data = get_weather_data(prefecture_code)
        if weather_data:
            try:
                # 天気データを解析して表示形式を作成
                areas = weather_data[0]["timeSeries"][0]["areas"]
                weather_details = "\n".join(
                    f"{area['area']['name']}: {area['weathers'][0]}"
                    for area in areas
                )
                weather_display.value = f"天気情報:\n{weather_details}"
            except (KeyError, IndexError) as e:
                print(f"Data parsing error: {e}")
                weather_display.value = "天気情報の解析に失敗しました。" # データ解析エラー時の表示
        else:
            weather_display.value = "天気情報の取得に失敗しました。" # APIエラー時の表示
        page.update()

    # サイドバー (ナビゲーションレール) の作成
    navigation_rail = ft.NavigationRail(
        destinations=[
            # 地域ごとに項目を追加
            ft.NavigationRailDestination(icon=ft.icons.LOCATION_CITY, label=region)
            for region in area_list.keys()
        ],
        selected_index=0, # 初期選択地域のインデックス
        on_change=lambda e: update_region_tiles(e.control.selected_index), # 選択時の処理
    )

    # ページの初期レイアウトを構築
    page.add(
        ft.Row(
            controls=[
                navigation_rail, # サイドバー
                ft.VerticalDivider(width=1), # ディバイダー
                ft.Column([expansion_tiles, weather_display], expand=True), # エリアと天気情報
            ],
            expand=True, # サイドバーとエリアを均等に分割
        )
    )

    # ページ更新後に初期状態を設定
    page.update()
    update_region_tiles(0) # 初期地域の都道府県リストを表示


ft.app(target=main)
