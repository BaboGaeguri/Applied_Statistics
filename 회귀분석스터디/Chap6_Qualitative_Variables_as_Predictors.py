import pandas as pd
import statsmodels.api as sm

url = "https://www1.aucegypt.edu/faculty/hadi/RABE6/Data6/Salary.Survey.txt"
data = pd.read_csv(url, sep='\t')  # 탭 구분자 사용

# print(data.info())

# E 변수의 고유값 확인
# print("\nE 변수의 고유값:", data['E'].unique())
# print("E 변수의 빈도:", data['E'].value_counts().sort_index())

# E 변수를 두 개의 이진변수로 변환
# E=3을 기준(reference)으로 하여 E=1, E=2에 대한 더미 변수 생성
data['E1'] = (data['E'] == 1).astype(int)
data['E2'] = (data['E'] == 2).astype(int)

# print("\n더미 변수가 추가된 데이터:")
# print(data.head(10))

# 회귀분석 수행
# 독립변수 설정 (X, E1, E2, M)
X = data[['X', 'E1', 'E2', 'M']]
X = sm.add_constant(X)  # 절편 추가

# 종속변수 설정 (S: Salary)
y = data['S']

# 회귀모델 적합
model = sm.OLS(y, X).fit()

# 결과 출력
print("\n회귀분석 결과:")
print(model.summary())