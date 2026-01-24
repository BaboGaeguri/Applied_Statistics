import pandas as pd
import statsmodels.api as sm

url = "https://www1.aucegypt.edu/faculty/hadi/RABE6/Data6/Bacteria.txt"
data = pd.read_csv(url, sep='\t')

print(data.info())