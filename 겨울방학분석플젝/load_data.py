import pandas as pd

# 첫 번째 엑셀 파일 불러오기
file_path = "겨울방학분석플젝/raw_data/시장베타/kospi_2016~2017.xlsx"
df = pd.read_excel(file_path)

print(df.head())
print(df.info())

# print(df_transfer)


# KOSPI200 지수 구성종목 불러오기
file_path = "겨울방학분석플젝/raw_data/KOSPI200_연말구성종목및시총/지수구성종목_2016.csv"
df1 = pd.read_csv(file_path, encoding='cp949')


# print("\n첫 번째 데이터프레임 정보:")
# print(df1.head())
# print("\n두 번째 데이터프레임 정보:")
# print(df1.info())