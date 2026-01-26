import pandas as pd
import OpenDartReader
from dotenv import load_dotenv
import os
import time

df = pd.read_csv("겨울방학분석플젝/preprocessing/mkt_cap.csv")

# df에서 year, month 추출
df['year'] = df['month'].str[:4].astype(int)
df['month_num'] = df['month'].str[5:7].astype(int)

# Fama-French 스타일: t년 7월 ~ t+1년 6월에 t년 자본총계 사용
# 따라서 매칭 연도(fiscal_year) 계산: 7월~12월은 해당 연도, 1월~6월은 전년도
df['fiscal_year'] = df.apply(
    lambda x: x['year'] if x['month_num'] >= 7 else x['year'] - 1, axis=1
)

# fiscal_year별로 unique한 종목 리스트 생성
yearly_tickers = {}
for fiscal_year in sorted(df['fiscal_year'].unique()):
    tickers = df[df['fiscal_year'] == fiscal_year]['ticker'].unique().tolist()
    yearly_tickers[fiscal_year] = tickers
    print(f"{fiscal_year}년 자본총계 → {fiscal_year}년 7월~{fiscal_year+1}년 6월: {len(tickers)}개 종목")

# 발급받은 API 키 입력
load_dotenv()
api_key = os.getenv('API_KEY_DART')
dart = OpenDartReader(api_key)

# 자본총계 데이터를 저장할 리스트
equity_data = []

# 연도별, 종목별 자본총계 가져오기
for year, tickers in yearly_tickers.items():
    print(f"\n=== {year}년 자본총계 수집 중... ===")

    for i, ticker in enumerate(tickers):
        try:
            # 사업보고서에서 재무제표 가져오기 (11011: 사업보고서)
            fn_data = dart.finstate(ticker, year, '11011')

            if fn_data is not None and len(fn_data) > 0:
                # 자본총계 추출
                equity_row = fn_data[fn_data['account_nm'] == '자본총계']
                if len(equity_row) > 0:
                    total_equity = equity_row['thstrm_amount'].values[0]
                    equity_data.append({
                        'year': year,
                        'ticker': ticker,
                        'total_equity': total_equity
                    })
                    print(f"  [{i+1}/{len(tickers)}] {ticker}: {total_equity}")
                else:
                    print(f"  [{i+1}/{len(tickers)}] {ticker}: 자본총계 항목 없음")
            else:
                print(f"  [{i+1}/{len(tickers)}] {ticker}: 데이터 없음")

        except Exception as e:
            print(f"  [{i+1}/{len(tickers)}] {ticker}: 오류 - {e}")

        # API 호출 제한 방지 (1초 대기)
        time.sleep(1)

# DataFrame으로 변환
df_equity = pd.DataFrame(equity_data)

# CSV로 저장
df_equity.to_csv("겨울방학분석플젝/raw_data/total_equity.csv", index=False, encoding='utf-8-sig')
print(f"\n=== 완료 ===")
print(f"총 {len(df_equity)}개 데이터 저장됨")
print(df_equity.head(10))