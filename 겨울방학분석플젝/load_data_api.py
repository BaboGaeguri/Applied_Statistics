import requests
import pandas as pd
from dotenv import load_dotenv
import os

def get_kospi_data_2025(beginBasDt, endBasDt,num_rows=100):
    url = "https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"
    
    load_dotenv()
    api_key = os.getenv('API_KEY')

    # 2025년 전체 데이터를 가져오기 위한 파라미터 설정
    params = {
        "serviceKey": api_key,
        "numOfRows": num_rows,      # 한 페이지 결과 수
        "pageNo": "1",              # 페이지 번호
        "resultType": "json",       # 결과 형식
        "beginBasDt": str(beginBasDt),   # 2025년 시작일
        "endBasDt": str(endBasDt),     # 2025년 종료일
        "mrktCls": "KOSPI"          # 시장구분: KOSPI
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        items = data['response']['body']['items']['item']
        
        # 데이터프레임으로 변환하여 정리
        df = pd.DataFrame(items)
        
        # 주요 컬럼 한글화 (선택 사항)
        columns_map = {
            'basDt': '기준일자',
            'itmsNm': '종목명',
            'clpr': '종가',
            'vs': '대비',
            'fltRt': '등락률',
            'trqu': '거래량',
            'mrktTotAmt': '시가총액'
        }
        return df[list(columns_map.keys())].rename(columns=columns_map)

    except Exception as e:
        print(f"에러 발생: {e}")
        return None

# 실제 사용 시 '본인의_인증키'를 입력하세요.
# MY_KEY = "YOUR_DECODED_SERVICE_KEY"
# result_df = get_kospi_data_2025(MY_KEY)
# print(result_df.head())

a = get_kospi_data_2025(api_key)

print(a.head())
print(a.info())


