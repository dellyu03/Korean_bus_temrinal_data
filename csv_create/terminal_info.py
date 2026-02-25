import requests
import pandas as pd
import os
from bs4 import BeautifulSoup

base_url = 'https://transportation.asamaru.net/'

class TerminalCrawler:
    def __init__(self, base_url: list, regions:list[str]):
        if type(base_url) != str:
            raise ValueError("⚠️ base_url is not str.")
        if type(regions) != list:
            raise ValueError("⚠️ regions is not list.")


def get_terminals(soup: BeautifulSoup, regions: list[str]):
    """
    crawl terminal names and timetable URLs by region

    input : BeautifulSoup Object, list of regions(Eng)
    output : dict of region and list of terminal dicts

    ex)
    {
        "seoulteugbyeolsi": [
            {"name": "서울고속버스터미널", "timetable_url": "https://transportation.asamaru.net/..."},
            ...
        ],
        ...
    }
    """
    result = {}
    for region in regions:
        div_tag = soup.find('div', attrs={'data-scrollspy-content': region})
        if not div_tag:
            continue

        ft_divs = div_tag.find_all('div', class_='ft-area-terminal')
        terminals = []
        for ft_div in ft_divs:
            for li in ft_div.find_all('li', class_='text-sm'):
                span = li.find('span', class_='pe-2')
                if not span:
                    continue
                name = span.text.strip()
                timetable_url = None
                for a in li.find_all('a'):
                    if '시간표' in a.text:
                        href = a.get('href', '')
                        if href:
                            timetable_url = base_url.rstrip('/') + href if href.startswith('/') else href
                        break
                terminals.append({"name": name, "timetable_url": timetable_url})
        result[region] = terminals
    return result


def add_timetable_to_csv(terminal_data: dict, csv_path: str):
    """터미널 이름 기준으로 timetable_url 컬럼을 CSV에 추가/업데이트"""
    url_map = {}
    for terminals in terminal_data.values():
        for t in terminals:
            url_map[t["name"]] = t["timetable_url"]

    df = pd.read_csv(csv_path)
    df["timetable_url"] = df["terminal_name"].map(url_map)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    matched = df["timetable_url"].notna().sum()
    print(f"완료: {matched}/{len(df)}개 터미널에 시간표 링크 추가됨 → {csv_path}")


if __name__ == "__main__":
    regions = [
    "seoulteugbyeolsi",
    "kyeongkido",
    "incheonkwangyeogsi",
    "daejeonkwangyeogsi",
    "daekukwangyeogsi",
    "ulsankwangyeogsi",
    "busankwangyeogsi",
    "kwangjukwangyeogsi",
    "sejongteugbyeoljachisi",
    "kangwonteugbyeoljachido",
    "chungcheongbugdo",
    "chungcheongnamdo",
    "kyeongsangbugdo",
    "kyeongsangnamdo",
    "jeonbugteugbyeoljachido",
    "jeonlanamdo",
    "jejuteugbyeoljachido",
    ]
    response = requests.get(base_url + '시외버스/터미널')

    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        terminal_data = get_terminals(soup, regions)

        for region, terminals in terminal_data.items():
            print(f"{region}: {[t['name'] for t in terminals]}")

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(base_dir, "bus_terminals_geo.csv")
        add_timetable_to_csv(terminal_data, csv_path)

    else:
        print("⚠️ 에러 발생 상태코드 : " + str(response.status_code))
