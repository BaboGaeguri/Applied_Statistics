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

print(f"\n전체 데이터 : {all_kospi_df['종목코드'].nunique()}개 종목, {len(all_kospi_df)}개 행")

####################################
# 분석 대상: 보통주 + 금융주 제외
####################################

# 보통주만 필터링 (ticker 끝자리가 0인 종목)
all_kospi_df = all_kospi_df[all_kospi_df['종목코드'].str.endswith('0')]

print(f"\n전체 데이터 (보통주만): {all_kospi_df['종목코드'].nunique()}개 종목, {len(all_kospi_df)}개 행")

# 금융주 제외
exclude_keywords = [
    '리츠', 'REITs', '지주', '홀딩스', '금융', 
    '증권', '보험', '화재', '은행', '카드', '생명'
]

final_survived_df = all_kospi_df[~all_kospi_df['종목명'].str.contains('|'.join(exclude_keywords))]

print(f"제외 전: {len(all_kospi_df)}개")
print(f"제외 후: {len(final_survived_df)}개")
print(f"제거된 종목 수: {len(all_kospi_df) - len(final_survived_df)}개")

####################################
# bookvalue 계산
####################################

df = pd.read_csv("겨울방학분석플젝/preprocessing/mkt_cap.csv")

# df에서 year 추출 (병합용)
df['year'] = df['month'].str[:4].astype(int)

# df에서 12월 데이터만 추출
df_dec = df[df['month'].str.endswith('-12')]

# final_survived_df 기준으로 병합 (left join)
merged_df = final_survived_df.merge(
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

monthly_df.to_csv("겨울방학분석플젝/preprocessing/monthly_BEME.csv", index=False, encoding='utf-8-sig')
print("\nCSV 저장 완료:")
print("- 겨울방학분석플젝/preprocessing/monthly_BEME.csv")