import requests
import json

# 気象庁の地域リストAPIのURL
URL = "https://www.jma.go.jp/bosai/common/const/area.json"

def fetch_and_save_area_list(output_file="area_list.json"):
    """
    気象庁のAPIから地域リストを取得し、JSON形式で保存する。
    
    Args:
        output_file (str): 保存先のJSONファイル名
    """
    try:
        # APIリクエストを送信
        response = requests.get(URL)
        response.raise_for_status()  # ステータスコードが200以外の場合は例外を投げる

        # JSONレスポンスを解析
        data = response.json()

        # 地域データを整形
        area_list = {}
        for center_code, center_info in data["centers"].items():
            area_list[center_info["name"]] = {
                "code": center_code,
                "prefectures": {
                    pref_code: data["offices"][pref_code]["name"]
                    for pref_code in center_info["children"]
                }
            }

        # 整形したデータをファイルに保存
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(area_list, f, ensure_ascii=False, indent=4)

        print(f"地域リストが正常に保存されました: {output_file}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# 実行
fetch_and_save_area_list()
