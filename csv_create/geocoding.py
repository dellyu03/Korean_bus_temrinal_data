from dotenv import load_dotenv
import os
import time
import requests
import pandas as pd

load_dotenv()

API_KEY = os.environ.get('GEOCODING_API_KEY')


def get_terminalGeo_json(terminal_name: str) -> dict | None:
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": terminal_name,
        "key": API_KEY,
        "language": "ko"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] == "OK":
        return data
    return None


def terminalGeo_json_to_dict(terminalGeoJSON: dict) -> dict:
    result = terminalGeoJSON["results"][0]
    address = result["formatted_address"]
    lat = result["geometry"]["location"]["lat"]
    lng = result["geometry"]["location"]["lng"]

    return {"address": address, "lat": lat, "lng": lng}


def process_terminals(csv_path: str, output_path: str):
    df = pd.read_csv(csv_path)

    addresses = []
    lats = []
    lngs = []

    total = len(df)
    for i, row in df.iterrows():
        query = f"{row['province']} {row['city']} {row['terminal_name']}"
        print(f"[{i+1}/{total}] 검색 중: {query}")

        geo_json = get_terminalGeo_json(query)
        if geo_json:
            geo = terminalGeo_json_to_dict(geo_json)
            addresses.append(geo["address"])
            lats.append(geo["lat"])
            lngs.append(geo["lng"])
        else:
            addresses.append(None)
            lats.append(None)
            lngs.append(None)
            print(f"  → 검색 실패")

        time.sleep(0.1)  # API 요청 간격

    df["address"] = addresses
    df["lat"] = lats
    df["lng"] = lngs

    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n완료: {output_path} 저장됨 ({total}건)")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_csv = os.path.join(base_dir, "bus_terminals.csv")
    output_csv = os.path.join(base_dir, "bus_terminals_geo.csv")

    process_terminals(input_csv, output_csv)
