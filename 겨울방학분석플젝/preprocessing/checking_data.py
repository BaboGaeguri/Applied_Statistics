import pandas as pd

df_beta = pd.read_csv("겨울방학분석플젝/preprocessing/beta.csv")
print(df_beta.head())
print(df_beta.info())

print(df_beta[df_beta['obs_count']<=100].nunique(), "개 종목 남음 after obs_count 필터링")