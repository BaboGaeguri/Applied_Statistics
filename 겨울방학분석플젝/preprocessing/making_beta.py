import pandas as pd

####################################
# KOSPI 데이터 불러오기 (2020~2025년)
####################################

all_dfs = []

for year in range(2020, 2026):
    kospi_path = f"겨울방학분석플젝/raw_data/공공데이터포털_주식시세정보/KOSPI_data_{year}.csv"
    df = pd.read_csv(kospi_path)
    all_dfs.append(df)
    print(f"{year}년: {df['srtnCd'].nunique()}개 종목")

# 전체 데이터프레임 합치기
all_kospi_df = pd.concat(all_dfs, ignore_index=True)

####################################
# 분석 대상: 보통주 + 금융주 제외
####################################

# 보통주만 필터링 (ticker 끝자리가 0인 종목)
all_kospi_df = all_kospi_df[all_kospi_df['srtnCd'].str.endswith('0')]

print(f"\n전체 데이터 (보통주만): {all_kospi_df['srtnCd'].nunique()}개 종목, {len(all_kospi_df)}개 행")

# 금융주 제외
exclude_keywords = [
    '리츠', 'REITs', '지주', '홀딩스', '금융', 
    '증권', '보험', '화재', '은행', '카드', '생명'
]

final_survived_df = all_kospi_df[~all_kospi_df['itmsNm'].str.contains('|'.join(exclude_keywords))]

print(f"제외 전: {len(all_kospi_df)}개")
print(f"제외 후: {len(final_survived_df)}개")
print(f"제거된 종목 수: {len(all_kospi_df) - len(final_survived_df)}개")
print(final_survived_df.head())


# 일별 수익률 계산 (종가 기준)
daily_data = final_survived_df.sort_values(['srtnCd', 'basDt'])
daily_data['clpr'] = daily_data['clpr'].astype(float)
daily_data['daily_return'] = daily_data.groupby('srtnCd')['clpr'].pct_change()  # 소수점 형태 (0.025 = 2.5%)

df_daily_return = daily_data[['basDt', 'srtnCd', 'itmsNm', 'daily_return']].copy()
df_daily_return.columns = ['date', 'ticker', 'name', 'daily_return']
df_daily_return = df_daily_return.reset_index(drop=True)

####################################
# 시장 수익률 데이터 로드 및 병합
####################################

df_market_return = pd.read_csv("겨울방학분석플젝/preprocessing/mkt_return.csv")

# 날짜 형식 통일
df_daily_return['date'] = pd.to_datetime(df_daily_return['date'], format='%Y%m%d')
df_market_return['date'] = pd.to_datetime(df_market_return['date'])

# 개별 수익률과 시장 수익률 병합
df_merged = df_daily_return.merge(
    df_market_return[['date', 'weighted_market_return']],
    on='date',
    how='inner'
)

# year_month 컬럼 추가
df_merged['year_month'] = df_merged['date'].dt.to_period('M')

print(f"\n병합 후 데이터: {len(df_merged)}개 행")
print(df_merged.head())

####################################
# 12개월 롤링 베타 계산 (21년 1월 ~ 25년 12월)
####################################

def calculate_beta(group):
    """Cov(Ri, Rm) / Var(Rm)"""
    if len(group) < 20:  # 최소 20일 이상 데이터 필요
        return None
    cov = group['daily_return'].cov(group['weighted_market_return'])
    var = group['weighted_market_return'].var()
    if var == 0:
        return None
    return cov / var

# 월별 리스트 생성 (2021-01 ~ 2025-12)
months = pd.period_range(start='2021-01', end='2025-12', freq='M')

beta_results = []

for target_month in months:
    # 과거 12개월 범위 설정
    start_month = target_month - 11

    # 해당 기간 데이터 필터링
    mask = (df_merged['year_month'] >= start_month) & (df_merged['year_month'] <= target_month)
    period_data = df_merged[mask]

    # 종목별 베타 계산
    for ticker in period_data['ticker'].unique():
        ticker_data = period_data[period_data['ticker'] == ticker]
        beta = calculate_beta(ticker_data)

        if beta is not None:
            name = ticker_data['name'].iloc[0]
            beta_results.append({
                'year_month': str(target_month),
                'ticker': ticker,
                'name': name,
                'beta': beta,
                'obs_count': len(ticker_data)
            })

    print(f"{target_month} 완료")

# 결과 데이터프레임 생성
df_beta = pd.DataFrame(beta_results)

print(f"\n=== 베타 계산 결과 ===")
print(f"shape: {df_beta.shape}")
print(df_beta.head(20))
print(df_beta.info())
print(f"\n베타 통계:")
print(df_beta['beta'].describe())

df_beta.to_csv("겨울방학분석플젝/preprocessing/beta.csv", index=False, encoding='utf-8-sig')
print("\nCSV 저장 완료:")
print("- 겨울방학분석플젝/preprocessing/beta.csv")