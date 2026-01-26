import pandas as pd

all_dfs = []

for year in range(2020, 2025):
    kospi_path = f"겨울방학분석플젝/raw_data/장부가시가비율/data_{year}.csv"
    df = pd.read_csv(kospi_path, encoding='cp949')
    df['year'] = year
    all_dfs.append(df)
    print(f"{year}년: {df['종목코드'].nunique()}개 종목")

# 전체 데이터프레임 합치기
all_kospi_df = pd.concat(all_dfs, ignore_index=True)

# 보통주만 필터링 (ticker 끝자리가 0인 종목)
all_kospi_df = all_kospi_df[all_kospi_df['종목코드'].str.endswith('0')]

filtered_df = all_kospi_df[['종목명', '종목코드', 'year', 'BPS']]

print(f"\n전체 데이터 (보통주만): {filtered_df['종목코드'].nunique()}개 종목, {len(all_kospi_df)}개 행")

##################################
# 금융기업 제외해야함!!!!
##################################

df = pd.read_csv("겨울방학분석플젝/preprocessing/mkt_cap.csv")

# df에서 year 추출 (병합용)
df['year'] = df['month'].str[:4].astype(int)

# df에서 12월 데이터만 추출
df_dec = df[df['month'].str.endswith('-12')]

# filtered_df 기준으로 병합 (left join)
merged_df = filtered_df.merge(
    df_dec[['year', 'ticker', 'lstg_st_cnt', 'mkt_cap']],
    left_on=['year', '종목코드'],
    right_on=['year', 'ticker'],
    how='left'
)

# 중복 컬럼 제거
merged_df = merged_df.drop(columns=['종목코드'])

# bookvalue 계산 (BPS * lstg_st_cnt), BPS가 NaN이면 bookvalue도 NaN
merged_df['bookvalue'] = merged_df['BPS'] * merged_df['lstg_st_cnt']

# 기본 정보 확인
print(f"\n=== merged_df 기본 정보 ===")
print(f"shape: {merged_df.shape}")
print(merged_df.info())

# 결측치 확인
print(f"\n=== 컬럼별 결측치 수 ===")
print(merged_df.isnull().sum())

##################################
# 월별 BEME 계산
# t년 7월 ~ t+1년 6월: t-1년 bookvalue 사용
##################################

# df에서 월 정보 추출
df['year_month'] = df['month']
df['cal_year'] = df['month'].str[:4].astype(int)
df['cal_month'] = df['month'].str[5:7].astype(int)

# bookvalue 기준 연도 계산 (7월~12월: year-1, 1월~6월: year-2)
df['bv_year'] = df.apply(
    lambda x: x['cal_year'] - 1 if x['cal_month'] >= 7 else x['cal_year'] - 2,
    axis=1
)

# merged_df에서 ticker별 bookvalue만 추출
bv_df = merged_df[['year', 'ticker', 'bookvalue']].copy()
bv_df = bv_df.rename(columns={'year': 'bv_year'})

# df와 bookvalue 병합
monthly_df = df.merge(
    bv_df,
    on=['bv_year', 'ticker'],
    how='left'
)

# BEME 계산
monthly_df['BEME'] = monthly_df['bookvalue'] / monthly_df['mkt_cap']

# 정리 (필요한 컬럼만)
monthly_df = monthly_df[['year_month', 'ticker', 'mkt_cap', 'bookvalue', 'BEME', 'bv_year']]

# 2021년~2025년 데이터만 추출
monthly_df = monthly_df[(monthly_df['year_month'] >= '2021-07') & (monthly_df['year_month'] <= '2025-12')]

print(f"\n=== monthly_df 기본 정보 ===")
print(f"shape: {monthly_df.shape}")
print(monthly_df.head(20))
print(f"\n=== 컬럼별 결측치 수 ===")
print(monthly_df.isnull().sum())

# monthly_df.to_csv("겨울방학분석플젝/preprocessing/bookvalue.csv", index=False, encoding='utf-8-sig')

# print("\nCSV 저장 완료:")
# print("- 겨울방학분석플젝/preprocessing/bookvalue.csv")



'''
# 1. monthly_df에서 결측치가 발생한 데이터만 추출
nan_analysis = monthly_df[monthly_df['bookvalue'].isna()].copy()

# 2. 종목명 정보가 유실되었을 수 있으므로 다시 매칭 (확인용)
name_map = filtered_df[['종목코드', '종목명']].drop_duplicates()
nan_analysis = nan_analysis.merge(name_map, left_on='ticker', right_on='종목코드', how='left')

# 3. 종목별/연도별 결측치 빈도 계산
# (특정 종목이 특정 연도 구간에서 통째로 빠졌는지 확인)
nan_summary = nan_analysis.groupby(['ticker', '종목명', 'bv_year']).size().reset_index(name='missing_months')

print("\n" + "="*50)
print("     [결측치 발생 종목 TOP 20 분석]     ")
print("="*50)
# 결측 월수가 많은 순(최대 12개월)으로 출력
print(nan_summary.sort_values(by='missing_months', ascending=False).head(20))

# 4. 결측 원인 판별 함수
def diagnose_nan(row):
    ticker = row['ticker']
    bv_year = int(row['bv_year'])
    
    # 해당 연도-티커 조합이 merged_df에 있는지 확인
    match = merged_df[(merged_df['ticker'] == ticker) & (merged_df['year'] == bv_year)]
    
    if match.empty:
        return "Merge Miss (BPS 원본에 종목 없음 - 신규상장/리츠 등)"
    elif pd.isna(match['bookvalue'].values[0]):
        return "Value NaN (원본에 종목은 있으나 BPS값이 NaN)"
    else:
        return "Unknown (로직 확인 필요)"

# TOP 10 종목에 대해 구체적 원인 진단
print("\n" + "-"*50)
print("     [상위 10개 결측 종목 상세 진단]     ")
print("-"*50)
top_nan_list = nan_summary.sort_values(by='missing_months', ascending=False).head(10)
top_nan_list['diagnosis'] = top_nan_list.apply(diagnose_nan, axis=1)
print(top_nan_list[['ticker', '종목명', 'bv_year', 'missing_months', 'diagnosis']])

# 5. (선택) 특정 종목명이 포함된 결측치만 따로 보기 (예: 리츠)
reits_nan = nan_summary[nan_summary['종목명'].str.contains('리츠', na=False)]
print(f"\n* 결측치 중 '리츠' 포함 종목 수: {reits_nan['ticker'].nunique()}개")
'''