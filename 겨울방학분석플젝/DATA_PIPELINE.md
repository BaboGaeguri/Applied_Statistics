# 데이터 파이프라인 흐름

## 전체 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAW DATA (원천 데이터)                      │
├─────────────────────────────────────────────────────────────────┤
│  raw_data/공공데이터포털_주식시세정보/KOSPI_data_{year}.csv         │
│  raw_data/개별지수시세정보_KRX/KOSPI_{yy}to{yy}.csv                │
│  raw_data/개별지수시세정보_KRX/KOSDAQ_{yy}to{yy}.csv               │
│  raw_data/장부가시가비율/data_{year}.csv                          │
│  raw_data/통안증권91일_2020to2025.xls                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PREPROCESSING (전처리)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐    ┌──────────────────────┐          │
│  │ making_mkt_return.py │    │ making_mktcap_and_   │          │
│  │                      │    │ excessreturn.py      │          │
│  │ KOSPI+KOSDAQ 지수    │    │                      │          │
│  │ → 일별 시장수익률      │    │ 개별종목 일별 데이터   │          │
│  │ (시총가중평균)         │    │ → 월별 시가총액       │          │
│  │                      │    │ → 월별 초과수익률     │          │
│  └──────────┬───────────┘    └──────────┬───────────┘          │
│             │                           │                       │
│             ▼                           ▼                       │
│      mkt_return.csv              mkt_cap.csv                    │
│             │               monthly_excess_return.csv           │
│             │                           │                       │
│  ┌──────────┴───────────┐               │                       │
│  │   making_beta.py     │               │                       │
│  │                      │               │                       │
│  │ 개별수익률 + 시장수익률 │               │                       │
│  │ → 12개월 롤링 베타    │               │                       │
│  └──────────┬───────────┘               │                       │
│             ▼                           │                       │
│         beta.csv                        │                       │
│                                         │                       │
│  ┌──────────────────────┐               │                       │
│  │   making_BEME.py     │               │                       │
│  │                      │               │                       │
│  │ BPS × 상장주식수      │               │                       │
│  │ → bookvalue          │               │                       │
│  │ → 월별 BEME          │               │                       │
│  └──────────┬───────────┘               │                       │
│             ▼                           │                       │
│      monthly_BEME.csv                   │                       │
│                                         │                       │
└─────────────┬───────────────────────────┴───────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│              FINAL PANEL DATA (최종 패널 데이터)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                   making_final.py                      │    │
│  │                                                        │    │
│  │   beta.csv ──────┐                                     │    │
│  │   mkt_cap.csv ───┼──→ MERGE (year_month, ticker)       │    │
│  │   monthly_BEME.csv──┤                                  │    │
│  │   monthly_excess_return.csv ──┘                        │    │
│  │                                                        │    │
│  │   → final_panel.csv                                    │    │
│  │     (year_month, ticker, name, beta, mkt_cap,          │    │
│  │      BEME, excess_return)                              │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ANALYSIS (분석)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────┐  ┌────────────────────────┐        │
│  │ cross_sectional_       │  │ cross_sectional_       │        │
│  │ regression.py          │  │ regression_winsorized  │        │
│  │                        │  │ .py                    │        │
│  │ Fama-MacBeth 회귀      │  │                        │        │
│  │ (lag 변수 사용)        │  │ Fama-MacBeth 회귀      │        │
│  │                        │  │ + 월별 횡단면           │        │
│  │                        │  │   윈저라이제이션        │        │
│  │                        │  │ (lag_beta, lag_BEME    │        │
│  │                        │  │  각 1%/99%)            │        │
│  └────────────────────────┘  └────────────────────────┘        │
│                                                                 │
│  ┌────────────────────────┐                                     │
│  │ check_with_table.py    │                                     │
│  │                        │                                     │
│  │ Size-BEME 10분위       │                                     │
│  │ 더블소팅 매트릭스       │                                     │
│  │ SMB, HML 효과 확인     │                                     │
│  └────────────────────────┘                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 스크립트 실행 순서

```bash
# 1. 시장 수익률 계산
python 겨울방학분석플젝/preprocessing/making_mkt_return.py

# 2. 시가총액 및 초과수익률 계산
python 겨울방학분석플젝/preprocessing/making_mktcap_and_excessreturn.py

# 3. 베타 계산
python 겨울방학분석플젝/preprocessing/making_beta.py

# 4. BEME 계산
python 겨울방학분석플젝/preprocessing/making_BEME.py

# 5. 최종 패널 데이터 생성
python 겨울방학분석플젝/final_monthly_panel_data/making_final.py

# 6. 분석 실행
python 겨울방학분석플젝/cross_sectional_regression.py           # 기본 (윈저라이제이션 없음)
python 겨울방학분석플젝/cross_sectional_regression_winsorized.py # 윈저라이제이션 적용
python 겨울방학분석플젝/check_with_table.py
```

---

## 주요 시차(Lag) 처리

| 단계 | 변수 | 시차 처리 |
|-----|-----|----------|
| Beta 계산 | t월 베타 | t-11 ~ t월 12개월 일별 데이터 사용 |
| BEME 계산 | t월 BEME | t-1년 bookvalue / t월 mkt_cap |
| 횡단면 회귀 | 독립변수 | t-1월 변수 → t월 수익률 예측 |

---

## 분석 기간

- **최종 분석 기간**: 2021-07 ~ 2025-12
- **베타 계산 시작**: 2021-01 (2020년 데이터부터 필요)

---

## 생성되는 CSV 파일

| 파일명 | 경로 | 설명 |
|-------|-----|------|
| mkt_return.csv | preprocessing/ | 일별 시장수익률 (KOSPI+KOSDAQ 시총가중평균) |
| mkt_cap.csv | preprocessing/ | 월별 개별종목 시가총액 |
| monthly_excess_return.csv | preprocessing/ | 월별 개별종목 초과수익률 |
| beta.csv | preprocessing/ | 월별 12개월 롤링 베타 |
| monthly_BEME.csv | preprocessing/ | 월별 BEME (Book-to-Market Equity) |
| final_panel.csv | final_monthly_panel_data/ | 최종 병합 패널 데이터 |
| monthly_gamma_coefficients.csv | 겨울방학분석플젝/ | Fama-MacBeth 회귀 월별 계수 (기본) |
| monthly_gamma_coefficients_winsorized.csv | 겨울방학분석플젝/ | Fama-MacBeth 회귀 월별 계수 (윈저라이제이션 적용) |

---

## 분석 대상 종목 필터링

1. **보통주만**: 종목코드 끝자리가 0인 종목
2. **금융주 제외**: 리츠, REITs, 지주, 홀딩스, 금융, 증권, 보험, 화재, 은행, 카드, 생명

---

## 횡단면 회귀 모형

```
excess_return(t) = α + γ₁·beta(t-1) + γ₂·log(mkt_cap)(t-1) + γ₃·BEME(t-1) + ε
```

- **Fama-MacBeth 방법**: 매월 횡단면 회귀 → γ 시계열 평균 및 t-통계량 계산

---

## 윈저라이제이션 설계 원칙

윈저라이제이션은 `final_panel.csv` 생성 단계가 아닌 **분석 스크립트 내 월별 루프에서** 적용된다.

**이유**:
- 윈저라이제이션 기준(P1, P99)이 **각 월의 횡단면 분포**에서 결정되므로, 전처리 단계에서 일괄 적용하는 것은 원리적으로 불가
- `final_panel.csv`는 `check_with_table.py`와 공유되므로, 분석 목적에 중립적인 원본 상태를 유지해야 함

**적용 변수 및 기준** (`cross_sectional_regression_winsorized.py`):

| 변수 | 윈저라이제이션 | 이유 |
|------|-------------|------|
| lag_beta | 1% / 99% | 롤링 베타 추정 오차로 인한 극단값 통제 |
| lag_BEME | 1% / 99% | 시총 급락 시 폭등하는 회계 지표 특성 |
| lag_log_mkt_cap | 미적용 | log 변환으로 극단값 영향 이미 완화 |
| excess_return | 미적용 | 종속변수 윈저라이제이션은 OLS 추정량 편의 유발 가능 |
