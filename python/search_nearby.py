import math
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup

base_url = 'https://transportation.asamaru.net/'

def express_route_info(link:str) -> list[str]:
    response = requests.get(link)

    if response.status_code != 200:
        print("⚠️ 에러 발생 상태코드 : " + str(response.status_code))
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    source = [h2.text.strip() for h2 in soup.find_all('h2')]
    cut_index = source.index("예매 안내")
    return source[:cut_index]


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """두 좌표 사이의 거리를 km 단위로 반환 (Haversine 공식)"""
    R = 6371.0
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlng / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def find_terminal(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """터미널 이름으로 검색 (부분 일치)"""
    return df[df["terminal_name"].str.contains(query, na=False)]


def search_nearby_terminals(csv_path: str, radius_km: float = 200.0):
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["lat", "lng"])

    query = input("검색할 터미널 이름을 입력하세요: ").strip()
    matches = find_terminal(df, query)

    if matches.empty:
        print("검색 결과가 없습니다.")
        return

    if len(matches) > 1:
        print(f"\n'{query}' 검색 결과 {len(matches)}건:")
        for i, (_, row) in enumerate(matches.iterrows()):
            print(f"  [{i}] {row['province']} {row['city']} {row['terminal_name']}")
        while True:
            try:
                idx = int(input("번호를 선택하세요: "))
                if 0 <= idx < len(matches):
                    selected = matches.iloc[idx]
                    break
            except ValueError:
                pass
            print("올바른 번호를 입력하세요.")
    else:
        selected = matches.iloc[0]

    origin_lat = selected["lat"]
    origin_lng = selected["lng"]
    origin_name = selected["terminal_name"]

    timetable_url = selected["timetable_url"]

    print(f"\n기준 터미널: {selected['province']} {selected['city']} {origin_name}")
    print(f"좌표: ({origin_lat:.6f}, {origin_lng:.6f})")
    print(f"노선 정보 조회 중...")
    routes = express_route_info(timetable_url)
    if not routes:
        print(f"⚠️  '{origin_name}'의 노선 정보를 가져올 수 없습니다.")
        return
    print(f"연결 노선 {len(routes)}개 확인. 반경 {radius_km}km 이내 + 노선 연결 터미널 검색 중...\n")

    results = []
    for _, row in df.iterrows():
        if row["terminal_name"] == origin_name and row["lat"] == origin_lat:
            continue
        # 노선에 포함된 터미널만 대상으로 처리
        if row["terminal_name"] not in routes:
            continue
        dist = haversine_km(origin_lat, origin_lng, row["lat"], row["lng"])
        if dist <= radius_km:
            results.append({
                "거리(km)": round(dist, 1),
                "시/도": row["province"],
                "시/군/구": row["city"],
                "터미널명": row["terminal_name"],
                "주소": row["address"],
            })

    results.sort(key=lambda x: x["거리(km)"])

    # 시/도 + 시/군/구 단위로 가장 가까운 터미널 하나만 유지
    seen = set()
    deduped = []
    for r in results:
        key = (r["시/도"], r["시/군/구"])
        if key not in seen:
            seen.add(key)
            deduped.append(r)
    results = deduped

    if not results:
        print("범위 내 노선 연결 터미널이 없습니다.")
        return

    print(f"총 {len(results)}개 시/군/구 (가까운 순):\n")
    print(f"{'거리(km)':>8}  {'시/도':<12}  {'시/군/구':<16}  터미널명")
    print("-" * 70)
    for r in results:
        print(f"{r['거리(km)']:>8.1f}  {r['시/도']:<12}  {r['시/군/구']:<16}  {r['터미널명']}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "bus_terminals_geo.csv")
    search_nearby_terminals(csv_path, radius_km=200.0)


