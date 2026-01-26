import pandas as pd

df = pd.read_csv("겨울방학분석플젝/preprocessing/mkt_cap.csv")
print(df['ticker'].nunique())
print(df.info())
print(df['ticker'].nunique() * df['month'].nunique())