import pandas as pd
'''
all_merged_dfs = []

for year in range(2020, 2026):
    # 주식시세정보 불러오기
    kospi_path = f"겨울방학분석플젝/raw_data/공공데이터포털_주식시세정보/KOSPI_data_{year}.csv"
    df = pd.read_csv(kospi_path)

    # KOSPI200 지수 구성종목 불러오기
    kospi200_path = f"겨울방학분석플젝/raw_data/KOSPI200_연말구성종목및시총/지수구성종목_{year}.csv"
    df_transfer = pd.read_csv(kospi200_path, encoding='cp949')

    # 종목코드 형식 맞추기 (5930 → 005930)
    df_transfer['종목코드'] = df_transfer['종목코드'].astype(str).str.zfill(6)

    # KOSPI200 구성종목과 주식시세정보 매칭
    merged_df = pd.merge(df, df_transfer[['종목코드']], left_on='srtnCd', right_on='종목코드', how='inner')

    print(f"{year}년: {merged_df['srtnCd'].nunique()}개 종목 매칭")

    all_merged_dfs.append(merged_df)

# 전체 데이터프레임 합치기
final_df = pd.concat(all_merged_dfs, ignore_index=True)

print(f"\n전체 데이터:")
print(f"총 {final_df['srtnCd'].nunique()}개 종목, {len(final_df)}개 행")

# 20년부터 25년까지 모두 존재하는 종목 확인
final_df['year'] = final_df['basDt'].astype(str).str[:4].astype(int)
years_per_stock = final_df.groupby('srtnCd')['year'].nunique()
stocks_all_years = years_per_stock[years_per_stock == 6].index.tolist()

print(f"\n20~25년 모두 존재하는 종목: {len(stocks_all_years)}개")
print(stocks_all_years[:10])  # 처음 10개 종목 출력

##################################
# 금융기업 제외해야함!!!!
##################################

# 21~25년 모두 존재하는 종목만 필터링
final_survived_df = final_df[final_df['srtnCd'].isin(stocks_all_years)].copy()

# 날짜 처리
final_survived_df['basDt'] = pd.to_datetime(final_survived_df['basDt'], format='%Y%m%d')
final_survived_df['year_month'] = final_survived_df['basDt'].dt.to_period('M')

# 월말 데이터만 추출 (각 종목별 월의 마지막 거래일)
monthly_data = final_survived_df.loc[
    final_survived_df.groupby(['srtnCd', 'year_month'])['basDt'].idxmax()
]

# 시가총액 데이터프레임 (month, ticker, name, mkt_cap)
df_mkt_cap = monthly_data[['year_month', 'srtnCd', 'itmsNm', 'mrktTotAmt']].copy()
df_mkt_cap.columns = ['month', 'ticker', 'name', 'mkt_cap']
df_mkt_cap = df_mkt_cap.reset_index(drop=True)

# 월별 수익률 계산 (종가 기준)
monthly_data = monthly_data.sort_values(['srtnCd', 'year_month'])
monthly_data['clpr'] = monthly_data['clpr'].astype(float)
monthly_data['monthly_return'] = monthly_data.groupby('srtnCd')['clpr'].pct_change()  # 소수점 형태 (0.025 = 2.5%)

df_monthly_return = monthly_data[['year_month', 'srtnCd', 'itmsNm', 'monthly_return']].copy()
df_monthly_return.columns = ['month', 'ticker', 'name', 'monthly_return']
df_monthly_return = df_monthly_return.reset_index(drop=True)

print(f"\n월별 시가총액 (df_mkt_cap):")
print(df_mkt_cap.shape)
print(df_mkt_cap.head(10))

print(f"\n월별 수익률 (df_monthly_return):")
print(df_monthly_return.shape)
print(df_monthly_return.head(10))
'''

##################################
# KOSPI 전체 종목에서 6년 연속 존재하는 종목 확인
##################################

all_dfs = []

for year in range(2020, 2026):
    kospi_path = f"겨울방학분석플젝/raw_data/공공데이터포털_주식시세정보/KOSPI_data_{year}.csv"
    df = pd.read_csv(kospi_path)
    all_dfs.append(df)
    print(f"{year}년: {df['srtnCd'].nunique()}개 종목")

# 전체 데이터프레임 합치기
all_kospi_df = pd.concat(all_dfs, ignore_index=True)

# 보통주만 필터링 (ticker 끝자리가 0인 종목)
all_kospi_df = all_kospi_df[all_kospi_df['srtnCd'].str.endswith('0')]

print(f"\n전체 데이터 (보통주만): {all_kospi_df['srtnCd'].nunique()}개 종목, {len(all_kospi_df)}개 행")

##################################
# 금융기업 제외해야함!!!!
##################################

# 전체 보통주 데이터 사용
final_survived_df = all_kospi_df.copy()

# 날짜 처리
final_survived_df['basDt'] = pd.to_datetime(final_survived_df['basDt'], format='%Y%m%d')
final_survived_df['year_month'] = final_survived_df['basDt'].dt.to_period('M')

# 월말 데이터만 추출 (각 종목별 월의 마지막 거래일)
monthly_data = final_survived_df.loc[
    final_survived_df.groupby(['srtnCd', 'year_month'])['basDt'].idxmax()
]

# 시가총액 데이터프레임 (month, ticker, name, mkt_cap)
df_mkt_cap = monthly_data[['year_month', 'srtnCd', 'itmsNm', 'lstgStCnt','mrktTotAmt']].copy()
df_mkt_cap.columns = ['month', 'ticker', 'name', 'lstg_st_cnt', 'mkt_cap']
df_mkt_cap = df_mkt_cap.reset_index(drop=True)

# 월별 수익률 계산 (종가 기준)
monthly_data = monthly_data.sort_values(['srtnCd', 'year_month'])
monthly_data['clpr'] = monthly_data['clpr'].astype(float)
monthly_data['monthly_return'] = monthly_data.groupby('srtnCd')['clpr'].pct_change()  # 소수점 형태 (0.025 = 2.5%)

df_monthly_return = monthly_data[['year_month', 'srtnCd', 'itmsNm', 'monthly_return']].copy()
df_monthly_return.columns = ['month', 'ticker', 'name', 'monthly_return']
df_monthly_return = df_monthly_return.reset_index(drop=True)

print(f"\n월별 시가총액 (df_mkt_cap):")
print(df_mkt_cap.shape)
print(df_mkt_cap.head(10))

print(f"\n월별 수익률 (df_monthly_return):")
print(df_monthly_return.shape)
print(df_monthly_return.head(10))

##################################
# 무위험수익률 차감하여 초과수익률 계산
##################################

# 통안증권 91일 데이터 불러오기
rf_path = "겨울방학분석플젝/raw_data/통안증권91일_2020to2025.xls"
df_rf = pd.read_excel(rf_path, skiprows=2)  # 처음 2행(최고/최저) 스킵
df_rf.columns = ['month', 'rf_annual']

# 월 형식 변환 (2025-12 → Period)
df_rf['month'] = pd.to_datetime(df_rf['month']).dt.to_period('M')

# 연율(%) → 월율 소수점 변환 (/ 12 / 100)
df_rf['rf_monthly'] = df_rf['rf_annual'] / 12 / 100  # 소수점 형태 (0.002 = 0.2%)

# df_monthly_return과 머지
df_monthly_excess_return = df_monthly_return.merge(df_rf[['month', 'rf_monthly']], on='month', how='left')

# 초과수익률 계산
df_monthly_excess_return['excess_return'] = df_monthly_excess_return['monthly_return'] - df_monthly_excess_return['rf_monthly']

# 필요한 컬럼만 유지
df_monthly_excess_return = df_monthly_excess_return[['month', 'ticker', 'name', 'excess_return']]

print(f"\n월별 초과수익률 (df_monthly_excess_return):")
print(df_monthly_excess_return.shape)
print(df_monthly_excess_return.head(10))

##################################
# CSV 파일로 저장
##################################

df_monthly_excess_return.to_csv("겨울방학분석플젝/preprocessing/monthly_excess_return.csv", index=False, encoding='utf-8-sig')
df_mkt_cap.to_csv("겨울방학분석플젝/preprocessing/mkt_cap.csv", index=False, encoding='utf-8-sig')

print("\nCSV 저장 완료:")
print("- 겨울방학분석플젝/preprocessing/monthly_excess_return.csv")
print("- 겨울방학분석플젝/preprocessing/mkt_cap.csv")