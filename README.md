# Fama-French 3-Factor 한국 주식시장 실증 분석

Fama-MacBeth(1973) 방법론으로 한국 주식시장(KOSPI+KOSDAQ)에서 **베타, 규모, 장부가시가비율(BEME)** 이 월별 초과수익률을 설명하는지 검증한다.

---

## 분석 모형

```
excess_return(t) = α + γ₁·beta(t-1) + γ₂·log(mkt_cap)(t-1) + γ₃·BEME(t-1) + ε
```

- 매월 횡단면 OLS 회귀 → 월별 γ 계수 수집 → 시계열 평균 및 t-통계량으로 유의성 판단
- 독립변수는 모두 **1개월 lag** 처리 (t-1월 변수로 t월 수익률 예측)
- 분석 기간: **2021-08 ~ 2025-12 (53개월)**
- 분석 대상: 코스피·코스닥 비금융 보통주 (월평균 약 690개 종목)

---

## 주요 결과

| 변수 | 평균 γ | t-통계량 | 방향 | FF1992 일치 |
|------|--------|---------|------|------------|
| beta | -0.003 | ≈ -0.4 | — | ✓ (베타 비유의) |
| log(mkt_cap) | -0.003 | ≈ -1.8 | 음(−) | ✓ (소형주 프리미엄) |
| BEME | +0.004 | ≈ +2.0 | 양(+) | ✓ (가치주 프리미엄) |

- 세 변수의 **부호 방향은 Fama-French(1992)와 완전히 일치**
- t-통계량이 원 논문보다 낮은 것은 표본 기간 차이(53개월 vs 330개월)에 기인
- 평균 R²≈ 3% 는 횡단면 개별 종목 회귀에서 정상 수준

> 자세한 해석: [`겨울방학분석플젝/REGRESSION_RESULTS.md`](겨울방학분석플젝/REGRESSION_RESULTS.md)

---

## 데이터 출처

| 데이터 | 출처 |
|-------|------|
| 개별 종목 시가총액·종가 | 공공데이터포털 금융위원회_주식시세정보 |
| 시장지수 (시장수익률 계산용) | KRX 정보시스템 — 개별지수시세추이 |
| BPS (BEME 계산용) | KRX 정보시스템 — PER·PBR·배당수익률(개별종목) |
| 무위험수익률 | 통안증권 91일물 |

---

## 실행 순서

```bash
# 전처리
python 겨울방학분석플젝/preprocessing/making_mkt_return.py
python 겨울방학분석플젝/preprocessing/making_mktcap_and_excessreturn.py
python 겨울방학분석플젝/preprocessing/making_beta.py
python 겨울방학분석플젝/preprocessing/making_BEME.py

# 패널 데이터 생성
python 겨울방학분석플젝/final_monthly_panel_data/making_final.py

# 분석
python 겨울방학분석플젝/cross_sectional_regression.py            # 기본
python 겨울방학분석플젝/cross_sectional_regression_winsorized.py # 윈저라이제이션 적용
python 겨울방학분석플젝/check_with_table.py                      # Size-BEME 더블소팅
```

> 파이프라인 상세: [`겨울방학분석플젝/DATA_PIPELINE.md`](겨울방학분석플젝/DATA_PIPELINE.md)
