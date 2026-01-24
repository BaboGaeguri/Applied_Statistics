import pandas as pd

# 첫 번째 엑셀 파일 불러오기
file_path = "겨울방학분석플젝/raw_data/기업규모/시가총액(kospi)_2016.xlsx"
df = pd.read_excel(file_path)

# print(df.head())
# print(df.info())

file_path = "겨울방학분석플젝/utils/편입편출_16to20.csv"
df_transfer1 = pd.read_csv(file_path)

file_path = "겨울방학분석플젝/utils/편입편출_20to25.csv"
df_transfer2 = pd.read_csv(file_path)

print(df_transfer1)
print(df_transfer2)