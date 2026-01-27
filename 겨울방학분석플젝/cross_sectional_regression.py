import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

####################################
# 데이터 로드
####################################

df = pd.read_csv("겨울방학분석플젝/final_monthly_panel_data/final_panel.csv")

print(f"=== 원본 데이터 ===")
print(f"shape: {df.shape}")
print(df.head())

# log 시가총액 변환
df['log_mkt_cap'] = np.log(df['mkt_cap'])

####################################
# 시차(lag) 처리: t월 수익률 ~ t-1월 변수
####################################

# 정렬
df = df.sort_values(['ticker', 'year_month']).reset_index(drop=True)

# 종목별로 독립변수 1개월 lag
df['lag_beta'] = df.groupby('ticker')['beta'].shift(1)
df['lag_log_mkt_cap'] = df.groupby('ticker')['log_mkt_cap'].shift(1)
df['lag_BEME'] = df.groupby('ticker')['BEME'].shift(1)

# 결측치 제거 (lag로 인해 첫 월 데이터 제거됨)
df = df.dropna(subset=['excess_return', 'lag_beta', 'lag_log_mkt_cap', 'lag_BEME'])
print(f"\n시차 처리 및 결측치 제거 후: {df.shape}")

####################################
# 월별 횡단면 회귀분석 (Fama-MacBeth)
####################################

# 결과 저장용 리스트
regression_results = []

months = df['year_month'].unique()

for month in months:
    # 해당 월 데이터 추출
    monthly_data = df[df['year_month'] == month].copy()

    if len(monthly_data) < 30:  # 최소 30개 기업 필요
        continue

    # 종속변수: excess_return (t월)
    y = monthly_data['excess_return']

    # 독립변수: lag_beta, lag_log_mkt_cap, lag_BEME (t-1월)
    X = monthly_data[['lag_beta', 'lag_log_mkt_cap', 'lag_BEME']]
    X = sm.add_constant(X)  # 상수항 추가

    # OLS 회귀분석
    try:
        model = sm.OLS(y, X).fit()

        regression_results.append({
            'year_month': month,
            'n_obs': len(monthly_data),
            'const': model.params['const'],
            'gamma_beta': model.params['lag_beta'],
            'gamma_size': model.params['lag_log_mkt_cap'],
            'gamma_beme': model.params['lag_BEME'],
            'r_squared': model.rsquared
        })
    except Exception as e:
        print(f"{month}: 회귀분석 실패 - {e}")
        continue

# 결과 데이터프레임 생성
df_results = pd.DataFrame(regression_results)

print(f"\n=== 월별 횡단면 회귀 결과 ===")
print(f"분석 월 수: {len(df_results)}")
print(df_results.head(10))

####################################
# Fama-MacBeth 통계량 계산
####################################

def fama_macbeth_stats(series):
    """평균, 표준오차, t-통계량 계산"""
    mean = series.mean()
    std_error = series.std() / np.sqrt(len(series))
    t_stat = mean / std_error
    return mean, std_error, t_stat

print(f"\n=== Fama-MacBeth 결과 요약 ===")
print(f"{'변수':<15} {'평균':<12} {'표준오차':<12} {'t-통계량':<12}")
print("-" * 50)

for col in ['gamma_beta', 'gamma_size', 'gamma_beme']:
    mean, se, t = fama_macbeth_stats(df_results[col])
    var_name = col.replace('gamma_', '')
    print(f"{var_name:<15} {mean:<12.6f} {se:<12.6f} {t:<12.3f}")

print(f"\n평균 R-squared: {df_results['r_squared'].mean():.4f}")

####################################
# 시각화
####################################

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Beta 계수 시계열
ax1 = axes[0, 0]
ax1.plot(df_results['year_month'], df_results['gamma_beta'], marker='o', markersize=3)
ax1.axhline(y=0, color='r', linestyle='--', alpha=0.5)
ax1.axhline(y=df_results['gamma_beta'].mean(), color='g', linestyle='-', alpha=0.7, label=f'Mean: {df_results["gamma_beta"].mean():.4f}')
ax1.set_title('Beta Coefficient Over Time')
ax1.set_xlabel('Year-Month')
ax1.set_ylabel('Gamma (Beta)')
ax1.legend()
ax1.tick_params(axis='x', rotation=45)
# x축 라벨 간격 조정
ax1.set_xticks(ax1.get_xticks()[::6])

# 2. Size 계수 시계열
ax2 = axes[0, 1]
ax2.plot(df_results['year_month'], df_results['gamma_size'], marker='o', markersize=3, color='orange')
ax2.axhline(y=0, color='r', linestyle='--', alpha=0.5)
ax2.axhline(y=df_results['gamma_size'].mean(), color='g', linestyle='-', alpha=0.7, label=f'Mean: {df_results["gamma_size"].mean():.4f}')
ax2.set_title('Size (log_mkt_cap) Coefficient Over Time')
ax2.set_xlabel('Year-Month')
ax2.set_ylabel('Gamma (Size)')
ax2.legend()
ax2.tick_params(axis='x', rotation=45)
ax2.set_xticks(ax2.get_xticks()[::6])

# 3. BEME 계수 시계열
ax3 = axes[1, 0]
ax3.plot(df_results['year_month'], df_results['gamma_beme'], marker='o', markersize=3, color='green')
ax3.axhline(y=0, color='r', linestyle='--', alpha=0.5)
ax3.axhline(y=df_results['gamma_beme'].mean(), color='b', linestyle='-', alpha=0.7, label=f'Mean: {df_results["gamma_beme"].mean():.4f}')
ax3.set_title('BEME (Book-to-Market) Coefficient Over Time')
ax3.set_xlabel('Year-Month')
ax3.set_ylabel('Gamma (BEME)')
ax3.legend()
ax3.tick_params(axis='x', rotation=45)
ax3.set_xticks(ax3.get_xticks()[::6])

# 4. R-squared 시계열
ax4 = axes[1, 1]
ax4.plot(df_results['year_month'], df_results['r_squared'], marker='o', markersize=3, color='purple')
ax4.axhline(y=df_results['r_squared'].mean(), color='g', linestyle='-', alpha=0.7, label=f'Mean: {df_results["r_squared"].mean():.4f}')
ax4.set_title('R-squared Over Time')
ax4.set_xlabel('Year-Month')
ax4.set_ylabel('R-squared')
ax4.legend()
ax4.tick_params(axis='x', rotation=45)
ax4.set_xticks(ax4.get_xticks()[::6])

plt.tight_layout()
plt.savefig("겨울방학분석플젝/cross_sectional_regression_results.png", dpi=150)
plt.show()

print("\n그래프 저장 완료:")
print("- 겨울방학분석플젝/cross_sectional_regression_results.png")
# 결과 CSV 저장
df_results.to_csv("겨울방학분석플젝/monthly_gamma_coefficients.csv", index=False, encoding='utf-8-sig')
print("- 겨울방학분석플젝/monthly_gamma_coefficients.csv")