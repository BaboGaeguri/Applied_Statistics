import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

####################################
# 데이터 로드
####################################

df = pd.read_csv("겨울방학분석플젝/final_monthly_panel_data/final_panel.csv")

print(f"=== 원본 데이터 ===")
print(f"shape: {df.shape}")

# 결측치 제거
df = df.dropna()
print(f"결측치 제거 후: {df.shape}")

# log 시가총액 변환
df['log_mkt_cap'] = np.log(df['mkt_cap'])

####################################
# 시차(lag) 처리: t월 수익률 ~ t-1월 변수
####################################

df = df.sort_values(['ticker', 'year_month']).reset_index(drop=True)

df['lag_log_mkt_cap'] = df.groupby('ticker')['log_mkt_cap'].shift(1)
df['lag_BEME'] = df.groupby('ticker')['BEME'].shift(1)

df = df.dropna(subset=['excess_return', 'lag_log_mkt_cap', 'lag_BEME'])
print(f"시차 처리 후: {df.shape}")

####################################
# 월별 10분위 포트폴리오 구성
####################################

def assign_decile(group, col, label):
    """월별로 10분위 할당"""
    group[label] = pd.qcut(group[col], q=10, labels=range(1, 11), duplicates='drop')
    return group

# 월별로 Size, BEME 10분위 할당
df = df.groupby('year_month', group_keys=False).apply(
    lambda x: assign_decile(x, 'lag_log_mkt_cap', 'size_decile')
)
df = df.groupby('year_month', group_keys=False).apply(
    lambda x: assign_decile(x, 'lag_BEME', 'beme_decile')
)

# decile을 숫자형으로 변환
df['size_decile'] = df['size_decile'].astype(int)
df['beme_decile'] = df['beme_decile'].astype(int)

####################################
# Size-BEME 매트릭스 생성 (평균 수익률)
####################################

# 각 Size-BEME 조합의 평균 excess_return 계산
matrix = df.groupby(['size_decile', 'beme_decile'])['excess_return'].mean().unstack()

# 월별 평균으로 변환 (% 단위)
matrix = matrix * 100

print("\n=== Size-BEME 평균 수익률 매트릭스 (월별 %) ===")
print(matrix.round(3))

####################################
# Size 효과 확인 (BEME 고정, Size 변화)
####################################

size_effect = df.groupby('size_decile')['excess_return'].mean() * 100
print(f"\n=== Size별 평균 수익률 (%) ===")
print(size_effect.round(3))
print(f"\nSMB (Small - Big): {size_effect[1] - size_effect[10]:.3f}%")

####################################
# BEME 효과 확인 (Size 고정, BEME 변화)
####################################

beme_effect = df.groupby('beme_decile')['excess_return'].mean() * 100
print(f"\n=== BEME별 평균 수익률 (%) ===")
print(beme_effect.round(3))
print(f"\nHML (High - Low): {beme_effect[10] - beme_effect[1]:.3f}%")

####################################
# 시각화
####################################

fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# 1. Size-BEME 히트맵
ax1 = axes[0, 0]
sns.heatmap(matrix, annot=True, fmt='.2f', cmap='RdYlGn', center=0, ax=ax1,
            cbar_kws={'label': 'Monthly Excess Return (%)'})
ax1.set_title('Size-BEME Double Sort: Average Monthly Excess Return (%)')
ax1.set_xlabel('BEME Decile (1=Low, 10=High)')
ax1.set_ylabel('Size Decile (1=Small, 10=Big)')

# 2. Size 효과 (막대 그래프)
ax2 = axes[0, 1]
colors = ['green' if x > 0 else 'red' for x in size_effect]
ax2.bar(size_effect.index, size_effect.values, color=colors, edgecolor='black')
ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax2.set_title('Size Effect: Average Monthly Excess Return by Size Decile')
ax2.set_xlabel('Size Decile (1=Small, 10=Big)')
ax2.set_ylabel('Monthly Excess Return (%)')
ax2.set_xticks(range(1, 11))

# 3. BEME 효과 (막대 그래프)
ax3 = axes[1, 0]
colors = ['green' if x > 0 else 'red' for x in beme_effect]
ax3.bar(beme_effect.index, beme_effect.values, color=colors, edgecolor='black')
ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax3.set_title('BEME Effect: Average Monthly Excess Return by BEME Decile')
ax3.set_xlabel('BEME Decile (1=Low/Growth, 10=High/Value)')
ax3.set_ylabel('Monthly Excess Return (%)')
ax3.set_xticks(range(1, 11))

# 4. Size-BEME 스프레드 (선 그래프)
ax4 = axes[1, 1]

# 각 Size 분위별 HML (High BEME - Low BEME)
hml_by_size = matrix[10] - matrix[1]
ax4.plot(hml_by_size.index, hml_by_size.values, marker='o', label='HML (BEME 10 - BEME 1)', color='blue')

# 각 BEME 분위별 SMB (Small - Big)
smb_by_beme = matrix.loc[1] - matrix.loc[10]
ax4.plot(smb_by_beme.index, smb_by_beme.values, marker='s', label='SMB (Size 1 - Size 10)', color='orange')

ax4.axhline(y=0, color='black', linestyle='--', linewidth=0.5)
ax4.set_title('Factor Spreads Across Deciles')
ax4.set_xlabel('Decile')
ax4.set_ylabel('Return Spread (%)')
ax4.legend()
ax4.set_xticks(range(1, 11))

plt.tight_layout()
plt.savefig("겨울방학분석플젝/size_beme_matrix.png", dpi=150)
plt.show()

print("\n그래프 저장 완료:")
print("- 겨울방학분석플젝/size_beme_matrix.png")

####################################
# 요약 통계
####################################

print("\n" + "="*60)
print("                    요약 (Summary)")
print("="*60)
print(f"분석 기간: {df['year_month'].min()} ~ {df['year_month'].max()}")
print(f"총 관측치: {len(df):,}개")
print(f"월 수: {df['year_month'].nunique()}개")
print(f"종목 수: {df['ticker'].nunique()}개")
print(f"\nSize 효과 (SMB): {size_effect[1] - size_effect[10]:.3f}% {'(소형주 프리미엄 O)' if size_effect[1] > size_effect[10] else '(소형주 프리미엄 X)'}")
print(f"Value 효과 (HML): {beme_effect[10] - beme_effect[1]:.3f}% {'(가치주 프리미엄 O)' if beme_effect[10] > beme_effect[1] else '(가치주 프리미엄 X)'}")
