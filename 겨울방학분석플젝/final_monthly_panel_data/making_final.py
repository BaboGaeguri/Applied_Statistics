import pandas as pd

####################################
# 데이터 로드
####################################

# beta.csv: year_month, ticker, name, beta, obs_count
df_beta = pd.read_csv("겨울방학분석플젝/preprocessing/beta.csv")

# mkt_cap.csv: month, ticker, mkt_cap 등
df_mkt_cap = pd.read_csv("겨울방학분석플젝/preprocessing/mkt_cap.csv")

# monthly_BEME.csv: year_month, ticker, BEME 등
df_beme = pd.read_csv("겨울방학분석플젝/preprocessing/monthly_BEME.csv")

# monthly_excess_return.csv: year_month, ticker, excess_return 등
df_excess = pd.read_csv("겨울방학분석플젝/preprocessing/monthly_excess_return.csv")

print("=== 각 데이터 컬럼명 ===")
print(f"beta: {df_beta.columns.tolist()}")
print(f"mkt_cap: {df_mkt_cap.columns.tolist()}")
print(f"beme: {df_beme.columns.tolist()}")
print(f"excess_return: {df_excess.columns.tolist()}")

df_beta = df_beta[['year_month', 'ticker', 'name', 'beta']]

df_mkt_cap = df_mkt_cap.rename(columns={'month': 'year_month'})
df_mkt_cap = df_mkt_cap[['year_month', 'ticker', 'mkt_cap']]

df_beme = df_beme[['year_month', 'ticker', 'BEME']]

df_excess = df_excess.rename(columns={'month': 'year_month'})
df_excess = df_excess[['year_month', 'ticker', 'excess_return']]

####################################
# 데이터 병합 (outer join으로 결측치 유지)
####################################

# beta 기준으로 시작
df_final = df_beta.merge(
    df_mkt_cap,
    on=['year_month', 'ticker'],
    how='outer'
)

df_final = df_final.merge(
    df_beme,
    on=['year_month', 'ticker'],
    how='outer'
)

df_final = df_final.merge(
    df_excess,
    on=['year_month', 'ticker'],
    how='outer'
)

# 컬럼 정리 및 순서 변경
df_final = df_final[['year_month', 'ticker', 'name', 'beta', 'mkt_cap', 'BEME', 'excess_return']]

# 정렬
df_final = df_final.sort_values(['year_month', 'ticker']).reset_index(drop=True)

# 필요한 기간 데이터만 추출
df_final = df_final[
    (df_final['year_month'] >= '2021-07') &
    (df_final['year_month'] <= '2025-12')
]

####################################
# 결과 확인
####################################

print(f"\n=== 최종 패널 데이터 ===")
print(f"shape: {df_final.shape}")
print(df_final.head(20))
print(df_final.info())

print(f"\n=== 컬럼별 결측치 수 ===")
print(df_final.isnull().sum())

print(f"\n=== 기간 범위 ===")
print(f"시작: {df_final['year_month'].min()}")
print(f"종료: {df_final['year_month'].max()}")

print(f"\n=== 종목 수 ===")
print(f"총 종목 수: {df_final['ticker'].nunique()}")

####################################
# 결측치 제거 시 월별 기업 수 확인
####################################

df_no_na = df_final.dropna()
monthly_counts = df_no_na.groupby('year_month')['ticker'].nunique()

print(f"\n=== 결측치 제거 후 월별 기업 수 ===")
print(monthly_counts.to_string())
print(f"\n평균: {monthly_counts.mean():.1f}개")
print(f"최소: {monthly_counts.min()}개 ({monthly_counts.idxmin()})")
print(f"최대: {monthly_counts.max()}개 ({monthly_counts.idxmax()})")

df_final.to_csv("겨울방학분석플젝/final_monthly_panel_data/final_panel.csv", index=False, encoding='utf-8-sig')
print("\nCSV 저장 완료:")
print("- 겨울방학분석플젝/final_monthly_panel_data/final_panel.csv")
