import requests
import pandas as pd
from dotenv import load_dotenv
import os

def get_kospi_data(beginBasDt, endBasDt):
    url = "https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"

    load_dotenv()
    api_key = os.getenv('API_KEY')

    all_items = []
    page_no = 1
    df = None  # 초기화

    while True:
        params = {
            "serviceKey": api_key,
            "numOfRows": "10000",
            "pageNo": str(page_no),
            "resultType": "json",
            "beginBasDt": str(beginBasDt),
            "endBasDt": str(endBasDt),
            "mrktCls": "KOSPI"
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            total_count = int(data['response']['body']['totalCount'])
            items = data['response']['body']['items'].get('item', [])

            if not items:
                break

            all_items.extend(items)
            print(f"페이지 {page_no} 완료 ({len(all_items)}/{total_count})")

            if len(all_items) >= total_count:
                df =  pd.DataFrame(all_items)

                # endBasDt에서 연도 추출
                year = str(endBasDt)[:4]

                # CSV 파일로 저장 (폴더 없으면 생성)
                save_dir = "겨울방학분석플젝/raw_data/공공데이터포털_주식시세정보"
                os.makedirs(save_dir, exist_ok=True)
                save_path = f"{save_dir}/KOSPI_data_{year}.csv"
                df.to_csv(save_path, index=False, encoding='utf-8-sig')
                print(f"저장 완료: {save_path}")
                break

            page_no += 1

        except Exception as e:
            print(f"에러 발생: {e}")
            return None

    return df

if __name__ == "__main__":
    '''
    df = get_kospi_data(20190101, 20191231)

    if df is not None:
        print(df.head())
        print(df.info())
    else:
        print("데이터를 가져오지 못했습니다.")
    '''



url = "https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"

load_dotenv()
api_key = os.getenv('API_KEY')

params = {
            "serviceKey": api_key,
            "numOfRows": "10000",
            "pageNo": "1",
            "resultType": "json",
            "beginBasDt": "20190101",
            "endBasDt": "20190131",
            "mrktCls": "KOSPI"
        }

response = requests.get(url, params=params)
response.raise_for_status()
data = response.json()

print(data)