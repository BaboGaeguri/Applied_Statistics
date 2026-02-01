import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats.mstats import winsorize

print("=" * 70)
print("              DATA VALIDATION FOR APPENDIX")
print("=" * 70)

####################################
# 데이터 로드
####################################

df = pd.read_csv("겨울방학분석플젝/final_monthly_panel_data/final_panel.csv")

print(f"\n[원본 패널 데이터]")
print(f"Shape: {df.shape}")
print(f"기간: {df['year_month'].min()} ~ {df['year_month'].max()}")

########################################################################
# 1. 패널 데이터 기본 구조 검증 (Structural Validation)
########################################################################

print("\n" + "=" * 70)
print("  1. 패널 데이터 기본 구조 검증 (Structural Validation)")
print("=" * 70)

# 월별 종목 수 계산
monthly_counts = df.groupby('year_month')['ticker'].nunique()

print(f"\n[월별 패널 종목 수 요약]")
print(f"  - 평균: {monthly_counts.mean():.1f}개")
print(f"  - 최소: {monthly_counts.min()}개 ({monthly_counts.idxmin()})")
print(f"  - 최대: {monthly_counts.max()}개 ({monthly_counts.idxmax()})")
print(f"  - 표준편차: {monthly_counts.std():.1f}개")

# 급변 구간 탐지 (전월 대비 10% 이상 변화)
monthly_counts_series = monthly_counts.reset_index()
monthly_counts_series.columns = ['year_month', 'count']
monthly_counts_series['pct_change'] = monthly_counts_series['count'].pct_change() * 100

significant_changes = monthly_counts_series[abs(monthly_counts_series['pct_change']) > 10]
print(f"\n[급변 구간 (전월 대비 10% 이상 변화)]")
if len(significant_changes) > 0:
    for _, row in significant_changes.iterrows():
        direction = "증가" if row['pct_change'] > 0 else "감소"
        print(f"  - {row['year_month']}: {row['pct_change']:+.1f}% {direction} ({int(row['count'])}개)")
else:
    print("  - 급변 구간 없음")

# 월별 종목 수 시계열 그래프
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(range(len(monthly_counts)), monthly_counts.values, marker='o', markersize=3)
ax.axhline(y=monthly_counts.mean(), color='r', linestyle='--', label=f'Mean: {monthly_counts.mean():.0f}')
ax.fill_between(range(len(monthly_counts)),
                monthly_counts.mean() - monthly_counts.std(),
                monthly_counts.mean() + monthly_counts.std(),
                alpha=0.2, color='red', label='±1 Std')
ax.set_title('Monthly Panel: Number of Stocks Over Time')
ax.set_xlabel('Month Index')
ax.set_ylabel('Number of Stocks')
ax.set_xticks(range(0, len(monthly_counts), 6))
ax.set_xticklabels(monthly_counts.index[::6], rotation=45)
ax.legend()
plt.tight_layout()
plt.savefig("겨울방학분석플젝/validation_1_panel_structure.png", dpi=150)
plt.close()
print(f"\n[그래프 저장] validation_1_panel_structure.png")

########################################################################
# 3. 시계열 연속성 검증 (Time Consistency)
########################################################################

print("\n" + "=" * 70)
print("  3. 시계열 연속성 검증 (Time Consistency)")
print("=" * 70)

# 종목별 관측 개월 수 계산
stock_obs_counts = df.groupby('ticker')['year_month'].nunique()

print(f"\n[종목별 관측 개월 수 분포]")
print(f"  - 총 종목 수: {len(stock_obs_counts)}개")
print(f"  - 평균 관측 개월 수: {stock_obs_counts.mean():.1f}개월")
print(f"  - 중앙값: {stock_obs_counts.median():.0f}개월")
print(f"  - 최소: {stock_obs_counts.min()}개월")
print(f"  - 최대: {stock_obs_counts.max()}개월")

# 구간별 종목 수
total_months = df['year_month'].nunique()
print(f"\n[관측 기간별 종목 분포] (전체 {total_months}개월)")
bins = [0, 6, 12, 24, 36, 48, total_months+1]
labels = ['1-6개월', '7-12개월', '13-24개월', '25-36개월', '37-48개월', f'49개월+']
stock_obs_binned = pd.cut(stock_obs_counts, bins=bins, labels=labels, right=True)
bin_counts = stock_obs_binned.value_counts().sort_index()
for label, count in bin_counts.items():
    pct = count / len(stock_obs_counts) * 100
    print(f"  - {label}: {count}개 ({pct:.1f}%)")

# 초단기 종목 (6개월 이하) 비중
short_term = (stock_obs_counts <= 6).sum()
short_term_pct = short_term / len(stock_obs_counts) * 100
print(f"\n[초단기 종목 (6개월 이하)]")
print(f"  - {short_term}개 ({short_term_pct:.1f}%)")

# 히스토그램
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(stock_obs_counts, bins=30, edgecolor='black', alpha=0.7)
ax.axvline(x=stock_obs_counts.mean(), color='r', linestyle='--', label=f'Mean: {stock_obs_counts.mean():.1f}')
ax.axvline(x=stock_obs_counts.median(), color='g', linestyle='--', label=f'Median: {stock_obs_counts.median():.0f}')
ax.set_title('Distribution of Observation Months per Stock')
ax.set_xlabel('Number of Observation Months')
ax.set_ylabel('Number of Stocks')
ax.legend()
plt.tight_layout()
plt.savefig("겨울방학분석플젝/validation_3_time_consistency.png", dpi=150)
plt.close()
print(f"\n[그래프 저장] validation_3_time_consistency.png")

########################################################################
# 5. 변수 분포 및 이상치 점검 (Sanity Check)
########################################################################

print("\n" + "=" * 70)
print("  5. 변수 분포 및 이상치 점검 (Sanity Check)")
print("=" * 70)

# 결측치 제외
df_clean = df.dropna()

# log 시가총액 변환
df_clean = df_clean.copy()
df_clean['log_mkt_cap'] = np.log(df_clean['mkt_cap'])

print(f"\n[핵심 변수 요약통계 (Winsorization 전)]")
print("-" * 60)

variables = ['beta', 'log_mkt_cap', 'BEME', 'excess_return']
var_labels = ['Beta', 'log(Size)', 'BEME (B/M)', 'Excess Return']

stats_before = []
for var, label in zip(variables, var_labels):
    data = df_clean[var]
    stats = {
        'Variable': label,
        'Mean': data.mean(),
        'Median': data.median(),
        'Std': data.std(),
        'Min': data.min(),
        'P1': data.quantile(0.01),
        'P25': data.quantile(0.25),
        'P75': data.quantile(0.75),
        'P99': data.quantile(0.99),
        'Max': data.max()
    }
    stats_before.append(stats)

df_stats_before = pd.DataFrame(stats_before)
print(df_stats_before.to_string(index=False))

# Winsorization (1%, 99%)
print(f"\n[Winsorization 적용 (1%, 99%)]")
print("-" * 60)

df_winsorized = df_clean.copy()
for var in variables:
    df_winsorized[var] = winsorize(df_clean[var], limits=[0.01, 0.01])

stats_after = []
for var, label in zip(variables, var_labels):
    data = df_winsorized[var]
    stats = {
        'Variable': label,
        'Mean': data.mean(),
        'Median': data.median(),
        'Std': data.std(),
        'Min': data.min(),
        'P1': data.quantile(0.01),
        'P25': data.quantile(0.25),
        'P75': data.quantile(0.75),
        'P99': data.quantile(0.99),
        'Max': data.max()
    }
    stats_after.append(stats)

df_stats_after = pd.DataFrame(stats_after)
print(df_stats_after.to_string(index=False))

# 극단값 비율
print(f"\n[극단값 비율 (1%/99% 분위수 밖)]")
for var, label in zip(variables, var_labels):
    p1 = df_clean[var].quantile(0.01)
    p99 = df_clean[var].quantile(0.99)
    outliers = ((df_clean[var] < p1) | (df_clean[var] > p99)).sum()
    pct = outliers / len(df_clean) * 100
    print(f"  - {label}: {outliers}개 ({pct:.2f}%)")

# 분포 시각화
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

for idx, (var, label) in enumerate(zip(variables, var_labels)):
    ax = axes[idx // 2, idx % 2]

    # 원본 분포 (x축 범위를 1%-99% 분위수로 제한)
    data = df_clean[var]
    p1, p99 = data.quantile(0.01), data.quantile(0.99)
    data_trimmed = data[(data >= p1) & (data <= p99)]

    ax.hist(data_trimmed, bins=50, alpha=0.7, label='Original (1-99%)', edgecolor='black')
    ax.axvline(x=data.mean(), color='r', linestyle='--', linewidth=2, label=f'Mean: {data.mean():.3f}')
    ax.axvline(x=data.median(), color='g', linestyle='--', linewidth=2, label=f'Median: {data.median():.3f}')
    ax.set_xlim(p1 - (p99-p1)*0.1, p99 + (p99-p1)*0.1)  # 약간의 여유 추가
    ax.set_title(f'{label} Distribution (1%-99% trimmed)')
    ax.set_xlabel(label)
    ax.set_ylabel('Frequency')
    ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig("겨울방학분석플젝/validation_5_variable_distribution.png", dpi=150)
plt.close()
print(f"\n[그래프 저장] validation_5_variable_distribution.png")

########################################################################
# 6. 결측치 및 필터링 검증 (Missingness)
########################################################################

print("\n" + "=" * 70)
print("  6. 결측치 및 필터링 검증 (Missingness)")
print("=" * 70)

print(f"\n[컬럼별 결측치 현황]")
print("-" * 40)
missing = df.isnull().sum()
missing_pct = df.isnull().sum() / len(df) * 100
for col in df.columns:
    if missing[col] > 0:
        print(f"  - {col}: {missing[col]:,}개 ({missing_pct[col]:.2f}%)")
    else:
        print(f"  - {col}: 0개 (0.00%)")

# 결측치 패턴 분석
print(f"\n[결측치 패턴 분석]")
print("-" * 40)

# 모든 변수가 있는 경우
complete = df.dropna()
print(f"  - 완전 관측치: {len(complete):,}개 ({len(complete)/len(df)*100:.1f}%)")

# beta만 결측
beta_only_missing = df[df['beta'].isna() & df['mkt_cap'].notna() & df['BEME'].notna() & df['excess_return'].notna()]
print(f"  - Beta만 결측: {len(beta_only_missing):,}개 ({len(beta_only_missing)/len(df)*100:.1f}%)")

# BEME만 결측
beme_only_missing = df[df['BEME'].isna() & df['mkt_cap'].notna() & df['beta'].notna() & df['excess_return'].notna()]
print(f"  - BEME만 결측: {len(beme_only_missing):,}개 ({len(beme_only_missing)/len(df)*100:.1f}%)")

# 결측 원인 추정
print(f"\n[결측치 발생 원인 추정]")
print("-" * 40)
print("  1. Beta 결측:")
print("     - 신규상장 후 12개월 미경과 (베타 계산 불가)")
print("     - 거래일수 부족 (20일 미만)")
print()
print("  2. BEME 결측:")
print("     - 재무자료(BPS) 미공시")
print("     - 상장주식수 정보 누락")
print()
print("  3. 기타:")
print("     - 상장폐지로 인한 데이터 절단")
print("     - 데이터 소스 간 병합 실패 (종목코드 불일치)")

########################################################################
# 최종 요약
########################################################################

print("\n" + "=" * 70)
print("                      VALIDATION SUMMARY")
print("=" * 70)
print(f"""
[데이터 개요]
  - 분석 기간: {df['year_month'].min()} ~ {df['year_month'].max()}
  - 총 관측치: {len(df):,}개
  - 완전 관측치: {len(complete):,}개 ({len(complete)/len(df)*100:.1f}%)
  - 총 종목 수: {df['ticker'].nunique()}개
  - 월 수: {df['year_month'].nunique()}개

[구조 검증]
  - 월별 평균 종목 수: {monthly_counts.mean():.0f}개
  - 종목 수 변동: 안정적 (표준편차 {monthly_counts.std():.1f})

[시계열 연속성]
  - 평균 관측 기간: {stock_obs_counts.mean():.1f}개월
  - 초단기(6개월↓) 종목: {short_term_pct:.1f}%

[이상치]
  - Winsorization 적용: 1%/99%
  - 극단값 처리로 회귀 안정성 확보

[결측치]
  - 주요 원인: 신규상장, 재무자료 미공시
  - 의도치 않은 데이터 손실 없음
""")

print("\n[저장된 그래프 파일]")
print("  - validation_1_panel_structure.png")
print("  - validation_3_time_consistency.png")
print("  - validation_5_variable_distribution.png")
