import pandas as pd

# 첫 번째 엑셀 파일 불러오기
file_path = "겨울방학분석플젝/raw_data/공공데이터포털_주식시세정보/KOSPI_data_2025.csv"
df = pd.read_csv(file_path)

# KOSPI200 지수 구성종목 불러오기
file_path = "겨울방학분석플젝/raw_data/KOSPI200_연말구성종목및시총/지수구성종목_2025.csv"
df_transfer = pd.read_csv(file_path, encoding='cp949')

# 종목코드 형식 맞추기 (5930 → 005930)
df_transfer['종목코드'] = df_transfer['종목코드'].astype(str).str.zfill(6)

# KOSPI200 구성종목과 주식시세정보 매칭
merged_df = pd.merge(df, df_transfer[['종목코드']], left_on='srtnCd', right_on='종목코드', how='inner')

print(merged_df['srtnCd'].nunique())  # 매칭된 종목 수 출력
print(merged_df.info())