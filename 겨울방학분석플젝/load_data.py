import pandas as pd

# 첫 번째 엑셀 파일 불러오기
file_path = "겨울방학분석플젝/raw_data/기업규모/시가총액(kospi)_2016.xlsx"
df = pd.read_excel(file_path)

# print(df.head())
# print(df.info())

# file_path = "겨울방학분석플젝/utils/편입편출.csv"
# df_transfer = pd.read_csv(file_path)

# print(df_transfer)

file_path = "겨울방학분석플젝/raw_data/KOSPI200_연말구성종목및시총/지수구성종목_2016.csv"
df1 = pd.read_csv(file_path, encoding='cp949')

file_path = "겨울방학분석플젝/data_5602_20260124.csv"
df2 = pd.read_csv(file_path, encoding='cp949')

print("\n첫 번째 데이터프레임 정보:")
print(df1.head())
print(df2.head())
print("\n두 번째 데이터프레임 정보:")
print(df1.info())
print(df2.info())