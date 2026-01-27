import pandas as pd

####################################
# KOSDAQ 데이터 불러오기 (2018~2025년)
####################################

all_kosdaq_dfs = []

for year in range(18, 25, 2):
    kosdaq_path = f"겨울방학분석플젝/raw_data/개별지수시세정보_KRX/KOSDAQ_{year}to{year+1}.csv"
    df = pd.read_csv(kosdaq_path, encoding='cp949')
    all_kosdaq_dfs.append(df)

# 전체 데이터프레임 합치기
all_kosdaq_df = pd.concat(all_kosdaq_dfs, ignore_index=True)

# 날짜 처리
all_kosdaq_df['date'] = pd.to_datetime(all_kosdaq_df['일자'], format="%Y/%m/%d")

# 일별 수익률 계산 (종가 기준)
all_kosdaq_df = all_kosdaq_df.sort_values(['date'])
all_kosdaq_df['daily_return'] = all_kosdaq_df['종가'].pct_change()

df_daily_kosdaq_return = all_kosdaq_df[['date', '상장시가총액', 'daily_return']].copy()
df_daily_kosdaq_return.columns = ['date', 'mkt_cap_kosdaq', 'daily_return_kosdaq']
df_daily_kosdaq_return = df_daily_kosdaq_return.reset_index(drop=True)
df_daily_kosdaq_return['lag_mkt_cap_kosdaq'] = df_daily_kosdaq_return['mkt_cap_kosdaq'].shift(1)

# print(df_daily_kosdaq_return.head())
# print(df_daily_kosdaq_return.info())

####################################
# KOSPI 데이터 불러오기 (2018~2025년)
####################################

all_kospi_dfs = []

for year in range(18, 25, 2):
    kospi_path = f"겨울방학분석플젝/raw_data/개별지수시세정보_KRX/KOSPI_{year}to{year+1}.csv"
    df = pd.read_csv(kospi_path, encoding='cp949')
    all_kospi_dfs.append(df)

# 전체 데이터프레임 합치기
all_kospi_df = pd.concat(all_kospi_dfs, ignore_index=True)

# 날짜 처리
all_kospi_df['date'] = pd.to_datetime(all_kospi_df['일자'], format="%Y/%m/%d")

# 일별 수익률 계산 (종가 기준)
all_kospi_df = all_kospi_df.sort_values(['date'])
all_kospi_df['daily_return'] = all_kospi_df['종가'].pct_change()

df_daily_kospi_return = all_kospi_df[['date', '상장시가총액', 'daily_return']].copy()
df_daily_kospi_return.columns = ['date', 'mkt_cap_kospi', 'daily_return_kospi']
df_daily_kospi_return = df_daily_kospi_return.reset_index(drop=True)
df_daily_kospi_return['lag_mkt_cap_kospi'] = df_daily_kospi_return['mkt_cap_kospi'].shift(1)

####################################
# KOSPI + KOSDAQ 병합 및 시총가중평균 수익률 계산
####################################

# date 기준으로 병합
df_market_return = df_daily_kospi_return.merge(
    df_daily_kosdaq_return[['date', 'daily_return_kosdaq', 'lag_mkt_cap_kosdaq']],
    on='date',
    how='inner'
)

# 시총가중평균 수익률 계산
df_market_return['weighted_market_return'] = (
    df_market_return['daily_return_kospi'] * df_market_return['lag_mkt_cap_kospi'] +
    df_market_return['daily_return_kosdaq'] * df_market_return['lag_mkt_cap_kosdaq']
) / (df_market_return['lag_mkt_cap_kospi'] + df_market_return['lag_mkt_cap_kosdaq'])

print("=== 최종 시장 수익률 데이터 ===")
print(df_market_return.head())
print(df_market_return.info())

df_market_return.to_csv("겨울방학분석플젝/preprocessing/mkt_return.csv", index=False, encoding='utf-8-sig')
print("\nCSV 저장 완료:")
print("- 겨울방학분석플젝/preprocessing/mkt_return.csv")
