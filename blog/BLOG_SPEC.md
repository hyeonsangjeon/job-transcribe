# Korean ASR Benchmark Blog Spec

## 1. Goal

이 문서는 `job-transcribe` 레포에 남아 있는 한국어 ASR/STT 실험 데이터를 다시 정리해, 내가 직접 설계하고 수행한 벤치마크 프로젝트를 기술 회고와 데이터 분석 관점에서 공표하기 위한 블로그 스펙이다.

핵심 목표는 단순한 모델 순위표가 아니다. 실제 음성 인식 결과를 기반으로 다음 질문에 답하는 블로그와 시각화 경험을 만든다.

- 어떤 데이터셋으로 테스트했는가?
- 어떤 모델과 클라우드 STT 서비스를 비교했는가?
- 한국어 STT에서 CER는 어떤 의미를 가지는가?
- 단일 화자 데이터와 금융 콜센터 데이터에서 성능이 어떻게 달라지는가?
- 평균 CER 외에 분포, worst case, threshold, 숫자 표기 민감도는 어떤 이야기를 하는가?
- 이 분석을 블로그, 정적 차트, D3.js 인터랙티브 UI로 어떻게 읽기 쉽게 보여줄 것인가?

Guardrails AI 사이트는 이 글의 개념적 프레임이 아니라 UI/UX 레퍼런스로만 사용한다.

참고 UI:

- Guardrails Docs: <https://guardrailsai.com/guardrails/docs>
- Guardrails Blog: <https://guardrailsai.com/blog>
- Guardrails Home: <https://guardrailsai.com/>

## 2. Scope And Public-data Disclaimer

이 블로그에는 다음 면책 문장을 서론 또는 데이터셋 섹션 초반에 명확히 포함한다.

> 이 분석은 2023년에 공개적으로 접근 가능한 제품과 오픈소스 모델을 사용해 수행한 개인 프로젝트성 실험 결과를 재정리한 것이다. 이 결과는 현재 시점의 Microsoft/Azure, AWS, Clova, GCP, OpenAI/Whisper 제품 성능을 대표하지 않으며, 각 회사의 공식 벤치마크나 내부 성능 데이터가 아니다.

명시할 범위:

- 이 실험은 2023년 당시의 모델/서비스 상태, 데이터셋, 설정, 평가 스크립트에 묶여 있다.
- Microsoft/Azure, AWS, Clova, GCP, OpenAI/Whisper 이름은 비교 대상 라벨로만 사용한다.
- 결과는 현재 제품 성능, SLA, vendor capability, procurement decision을 대표하지 않는다.
- 내부 문서, 내부 로그, 비공개 성능 데이터, 고객 데이터 유출이 아니다.
- 공개 제품 또는 공개 모델을 대상으로 한 실험 결과와 레포에 남아 있는 실제 결과 파일만 다시 분석한다.
- 새로운 글에서는 "A가 B보다 항상 좋다"가 아니라 "이 데이터와 당시 설정 기준으로는"이라는 표현을 사용한다.

## 3. Editorial Position

이 글은 세 가지 성격을 동시에 가진다.

1. 기술 회고
   - 2023년에 수행했던 Whisper 기반 한국어 STT 실험을 현재 시점에서 다시 정리한다.

2. 데이터 분석 리포트
   - 레포에 남아 있는 실제 결과 CSV, JSON, TXT만 사용해 모델 성능을 다시 계산하고 시각화한다.

3. UI/UX가 있는 기술 블로그
   - Guardrails 사이트의 문서형 탐색 UX와 블로그형 비주얼 톤을 참고해, 읽기 쉬운 원페이지 리포트로 만든다.

쓰지 않을 것:

- 전 직장 내부 이야기
- 특정 개인이나 조직에 대한 평가
- 감정적 서사
- 목업 데이터
- 실제 데이터에서 계산하지 않은 지표
- 내부 성능 데이터 유출로 오해될 수 있는 표현
- 현재 Microsoft/Azure, AWS, Clova, GCP, OpenAI/Whisper 성능을 대표한다는 표현

자연스럽게 드러낼 것:

- 이 프로젝트의 실험 설계, 데이터 생성, 모델 결과 수집, CER 분석을 내가 수행했다는 점
- 2023년 당시 기고했던 실험 자산을 지금 다시 정리한다는 점
- 모델 성능 평가는 평균 하나로 끝나지 않는다는 점

좋은 서론 문장 예:

> 이 실험은 2023년에 내가 직접 설계하고 수행했던 한국어 STT 벤치마크다. 당시 공개 제품과 공개 모델을 기준으로 Whisper 모델의 한국어 인식률을 확인하는 것이 목적이었다면, 이번에는 같은 데이터를 더 재현 가능한 분석과 시각화로 다시 정리하는 것이 목적이다. 이 결과는 현재 각 vendor의 제품 성능이나 내부 성능 데이터를 대표하지 않는다.

## 4. Audience

주요 독자:

- ASR/STT 모델 평가에 관심 있는 엔지니어
- Whisper, AWS Transcribe, Azure, Clova, GCP STT 결과를 비교하려는 사람
- 한국어 음성 데이터 평가 방법을 알고 싶은 AI/ML 실무자
- 모델 성능을 제품이나 운영 관점에서 해석해야 하는 PM, 기술 리더
- 데이터 시각화와 인터랙티브 분석 UI에 관심 있는 독자

독자가 읽고 나서 이해해야 할 것:

- 이 실험의 데이터셋 구성
- 모델별 CER 결과
- 단일 화자와 콜센터 환경의 차이
- 숫자 표기 정답지와 한글 표기 정답지의 차이
- 평균 CER 외에 봐야 할 지표
- 오류 사례를 어떻게 해석할지
- D3 기반 탐색 UI가 어떤 질문을 풀어야 하는지

## 5. Source Data Policy

### 5.1 No Mock Data

새로운 mock CSV를 만들지 않는다. 모든 분석은 레포에 존재하는 실제 데이터만 사용한다.

파생 요약 CSV, JSON, PNG는 허용한다. 단, 반드시 실제 원천 파일에서 계산된 결과여야 하며, 출처를 문서와 caption에 남긴다.

이 데이터는 공개 제품/공개 모델 실험 결과를 저장한 레포 데이터다. 내부 vendor 성능 데이터, 고객 운영 데이터, 비공개 benchmark 데이터로 표현하지 않는다.

### 5.2 Source Data

단일 화자 데이터:

- `meta_voice_data_3922.csv`
- `result/result_3922.csv`
- `result/openai_whisper_base_result_3922.csv`
- `result/openai_whisper_medium_result_3922.csv`
- `result/openai_whisper_large_result_3922.csv`

콜센터 데이터:

- `preprocess/cs_hangul_data.csv`
- `preprocess/cs_num_data.csv`
- `result/cs_hangul_result.csv`
- `result/cs_number_result.csv`

원문 및 중간 결과:

- `tmp_data/aws/*`
- `tmp_data/azure/*`
- `tmp_data/clova/*`
- `tmp_data/gcp/*`
- `tmp_data/groundtruth/*`

### 5.3 Derived Outputs

분석을 위해 생성되는 파일은 파생 산출물로 취급한다.

- `analysis/outputs/*`
- `blog/assets/*`
- `blog/interactive/*`

파생 데이터에는 다음 정보를 명시한다.

- source file
- generation script
- generated date if needed
- metric definition
- caveat

## 6. Dataset Design

### 6.1 Single-speaker Dataset

기본 벤치마크 데이터셋이다.

- 총 3,922문장
- 한국어 문장 기반
- 단일 화자 녹음
- 목표: 모델별 한국어 인식 성능을 통계적으로 비교

비교 모델:

- AWS Transcribe
- Whisper base
- Whisper medium
- Whisper large

분석 질문:

- 평균 CER이 가장 낮은 모델은 무엇인가?
- 완전 인식률은 모델별로 얼마나 차이 나는가?
- CER 분포는 zero-heavy인지, long-tail인지?
- threshold를 3%, 5%, 10%로 바꾸면 pass rate가 어떻게 변하는가?
- paired comparison에서 누가 더 자주 이기는가?
- worst case는 어떤 문장에서 발생하는가?

현재 파생 분석 기준 핵심 수치:

| Model | Mean CER | Median CER | Perfect | <=5% CER | >10% CER |
|---|---:|---:|---:|---:|---:|
| Whisper large | 2.22% | 0.00% | 70.27% | 83.20% | 5.69% |
| Whisper medium | 2.64% | 0.00% | 65.12% | 79.50% | 7.24% |
| AWS Transcribe | 3.73% | 0.00% | 56.12% | 71.01% | 12.32% |
| Whisper base | 9.35% | 6.94% | 29.12% | 41.13% | 37.33% |

Source: `analysis/outputs/model_performance_summary.md`

### 6.2 Financial Call-center Dataset

실제 통화 품질과 고객 상담 흐름을 가정한 작은 case analysis 데이터셋이다.

시나리오:

1. PB 채권 주문 상담
2. 신생기업 대출 안내 상담
3. 자동차 보험료 할증 문의 상담

비교 provider:

- AWS
- Azure
- Clova
- GCP

정답지 기준:

- 한글 표기 정답지
- 숫자 표기 정답지

분석 질문:

- 시나리오별 raw CER은 어떻게 다른가?
- provider별 요약 CER은 보조적으로 어떤 패턴을 보이는가?
- 숫자 표기 기준으로 바꾸면 결과가 어떻게 변하는가?
- PB, 대출, 보험 시나리오 중 어떤 시나리오가 가장 어려운가?
- n=3인 콜센터 결과는 어떻게 조심스럽게 해석해야 하는가?

현재 파생 분석 기준 provider 요약 수치:

주의: 콜센터 데이터는 기준별 3개 시나리오뿐이므로 아래 표는 ranking 근거가 아니라 보조 요약이다. 본문에서는 scenario x provider raw CER와 heatmap을 주력으로 보여준다.

| Basis | Provider | Mean CER | Median CER | Max CER |
|---|---|---:|---:|---:|
| hangul ground truth | AWS | 10.77% | 11.99% | 13.04% |
| hangul ground truth | Azure | 14.24% | 11.54% | 24.72% |
| hangul ground truth | Clova | 26.01% | 30.80% | 33.91% |
| hangul ground truth | GCP | 32.20% | 29.67% | 49.18% |
| numeric ground truth | Azure | 10.59% | 8.79% | 17.43% |
| numeric ground truth | AWS | 15.71% | 14.51% | 23.64% |
| numeric ground truth | Clova | 20.56% | 23.33% | 27.10% |
| numeric ground truth | GCP | 29.06% | 28.58% | 42.32% |

Source: `analysis/outputs/model_performance_summary.md`

## 7. Evaluation Metrics

### 7.1 CER

CER(Character Error Rate)는 정답 문장과 모델 출력 문장 사이의 문자 단위 편집 거리 기반 오류율이다.

이 글에서는 CER를 모델 성능의 기본 지표로 사용하되, CER 하나만으로 모든 품질을 판단하지 않는다.

현재 레포의 결과 CSV는 기존 측정 스크립트의 CER 값을 보존한다. 블로그 본문에서는 다음 정규화 정책을 명시한다.

- 단일 화자 결과는 `result/*.csv`에 저장된 기존 `cer` 값을 그대로 사용한다.
- 기존 측정은 레포 스크립트에서 `nlptutti.get_cer(...)`를 호출해 산출된 값이다.
- 블로그 재분석 단계에서 공백, 문장부호, 영문 대소문자, 숫자를 새로 정규화해 재계산하지 않는다.
- 콜센터 데이터는 한글 표기 정답지와 숫자 표기 정답지를 별도 기준으로 두고 각각의 CER를 비교한다.
- 향후 새로운 정규화 정책을 도입하면 모든 결과를 재계산하고, 기존 2023 결과와 분리해 표시한다.

### 7.2 Metrics To Report

단일 화자 데이터:

- mean CER
- median CER
- standard deviation
- 95% bootstrap confidence interval
- perfect recognition rate
- threshold pass rate
- over-threshold failure rate
- paired model delta
- model win/loss count
- worst examples
- disagreement examples
- length-bin performance

콜센터 데이터:

- scenario별 CER
- provider별 평균 CER
- 한글 정답지 vs 숫자 표기 정답지 차이
- scenario x provider heatmap
- case-level interpretation

### 7.3 Interpretation Rules

- 단일 화자 3,922건은 모델 비교와 분포 분석에 사용한다.
- 단일 화자 3,922건은 같은 화자/녹음 조건 안에서의 비교다. 다른 화자, 억양, 장비, 소음 환경으로 일반화하지 않는다.
- 콜센터 3개 시나리오는 표본 수가 작으므로 일반화하지 않는다.
- 콜센터 결과는 provider ranking보다 오류 유형, 도메인 민감도, 숫자 표기 민감도 해석에 사용한다.
- 평균 CER가 낮아도 tail risk가 크면 운영 품질 관점에서 별도 경고가 필요하다.
- 숫자, 고유명사, 영문 표기, 금융/보험 도메인 용어는 별도 오류 유형으로 다룬다.

## 8. Limitations And Threats To Validity

본문에는 다음 한계를 별도 섹션으로 명시한다.

- Temporal validity: 결과는 2023년 당시 공개 제품/공개 모델 상태를 반영한다. 현재 Microsoft/Azure, AWS, Clova, GCP, OpenAI/Whisper 성능을 대표하지 않는다.
- Vendor representation: 이 글은 vendor 공식 benchmark가 아니며, 제품 우열을 일반화하기 위한 문서가 아니다.
- Data scope: 단일 화자 3,922건은 같은 화자/녹음 환경의 표본이다. 다른 화자군, 방언, 마이크, 배경소음, 실시간 스트리밍 환경을 대표하지 않는다.
- Call-center scope: 콜센터 데이터는 3개 시나리오의 case analysis다. 평균/중앙값은 보조 요약이며, ranking 근거로 사용하지 않는다.
- Metric scope: CER는 문자 단위 지표이므로 의미 보존, 화자 분리, 타임스탬프, punctuation quality, downstream task utility를 직접 평가하지 않는다.
- Normalization sensitivity: 한국어 숫자 표기, 띄어쓰기, 문장부호, 영문/고유명사 표기에 따라 CER가 달라질 수 있다.

## 9. Reproducibility

분석 재생성 기준:

- 분석 스크립트: `analysis/analyze_asr_benchmarks.py`
- 의존성 파일: `analysis/requirements.txt`
- 고정 seed: `RNG_SEED = 20260625`
- 실행 예:

```bash
uv run --python /usr/bin/python3 --with pandas --with numpy --with matplotlib python analysis/analyze_asr_benchmarks.py
```

재생성되어야 하는 대표 산출물:

- `analysis/outputs/single_speaker_model_summary.csv`
- `analysis/outputs/single_speaker_threshold_pass_rates.csv`
- `analysis/outputs/single_speaker_paired_deltas.csv`
- `analysis/outputs/call_center_long.csv`
- `analysis/outputs/call_center_provider_summary.csv`
- `analysis/outputs/quality_gate_policy_simulation.csv`
- `blog/assets/single_speaker_mean_cer.png`
- `blog/assets/call_center_scenario_heatmap.png`
- `blog/assets/quality_gate_balanced.png`

## 10. Blog Agenda

### 10.1 Opening

제목 후보:

- 한국어 ASR 벤치마크 다시 보기
- 3,922문장과 3개의 콜센터 시나리오로 본 한국어 STT 성능
- Whisper와 클라우드 STT의 한국어 음성 인식 결과를 다시 분석하다

서론에서 말할 것:

- 2023년에 수행했던 Whisper 기반 한국어 STT 실험을 다시 정리한다.
- 당시에는 모델 성능 비교와 CER 계산이 중심이었다.
- 지금은 같은 데이터를 더 재현 가능한 분석과 시각화로 정리한다.
- 이 글은 레포의 실제 데이터만 사용한다.

### 10.2 Dataset

포함할 내용:

- 단일 화자 3,922문장
- 금융 콜센터 3개 시나리오
- 한글 정답지와 숫자 표기 정답지 차이
- provider/model 목록
- 데이터 해석 시 주의점

### 10.3 Evaluation Method

포함할 내용:

- CER 정의
- CER의 장점
- CER의 한계
- 한국어에서 띄어쓰기, 숫자, 고유명사가 주는 영향
- 평균값과 분포를 함께 봐야 하는 이유

### 10.4 Single-speaker Model Performance

포함할 내용:

- AWS Transcribe vs Whisper base/medium/large
- 평균 CER
- 중앙값
- 완전 인식률
- threshold별 pass rate
- paired delta
- worst examples

핵심 메시지:

- Whisper large와 medium이 전체적으로 강하다.
- Whisper base는 tail risk가 크다.
- AWS Transcribe는 Whisper base보다 안정적이지만 Whisper medium/large보다는 평균 CER이 높다.
- 평균값보다 threshold와 worst case를 같이 봐야 한다.

### 10.5 Call-center Scenario Analysis

포함할 내용:

- provider별 CER
- scenario별 차이
- 숫자 표기 정답지에서 결과가 어떻게 변하는지
- n=3이므로 일반화하지 않고 case analysis로 해석

핵심 메시지:

- 콜센터 데이터는 단일 화자 벤치마크보다 어렵다.
- 도메인 용어, 숫자, 전화 품질, 화자 전환이 성능에 영향을 준다.
- provider ranking보다 오류 유형을 보는 것이 중요하다.

### 10.6 Error Analysis

포함할 내용:

- worst CER examples
- 모델 간 disagreement examples
- 특정 모델만 틀리는 문장
- 모든 모델이 어려워하는 문장
- 숫자, 영문, 고유명사, 도메인 용어 오류

### 10.7 Visualization And Interactive UI

포함할 내용:

- 정적 PNG 차트
- D3.js explorer
- 독자가 직접 threshold를 바꿔볼 수 있는 UI
- GitHub Pages 기반 정적 배포

### 10.8 Conclusion

결론 메시지:

- 한국어 ASR 평가는 평균 CER 하나로 끝나지 않는다.
- 실제 적용을 생각하면 분포, threshold, worst case, 도메인별 취약점을 함께 봐야 한다.
- 이 레포는 한국어 ASR 성능을 재현 가능하게 분석하고 보여주는 프로젝트로 다시 정리된다.

## 11. UI/UX Spec

### 11.1 Page Type

최종 페이지는 리포트형 원페이지로 구성한다.

Desktop layout:

- top sticky navigation
- left section navigation
- center article content
- right "On this page" anchor navigation

Mobile layout:

- single column
- top navigation only
- section navigation은 접힘
- D3 controls는 세로 배치
- 표와 차트는 overflow 없이 responsive 처리

### 11.2 Borrow From Guardrails Docs

차용할 것:

- 문서형 좌측 네비게이션
- 우측 on-page 목차
- 검색/quick jump 느낌의 compact control
- 본문 중심의 안정적인 reading column
- 현재 섹션 highlight
- 코드, 표, 차트가 자연스럽게 섞이는 구조

### 11.3 Borrow From Guardrails Blog/Home

차용할 것:

- 큰 H1
- 넓은 여백
- 크림톤 배경
- 강한 색의 태그 버튼
- 단순한 CTA
- 밝고 선명한 브랜드 톤
- 섹션 간 넓은 breathing room

### 11.4 Do Not Borrow

차용하지 않을 것:

- Guardrails 브랜드명, 로고, 문구
- 마케팅 랜딩 페이지 중심 CTA
- 과한 Framer식 긴 제품 홍보 섹션
- 분석 흐름을 방해하는 장식적 카드
- 의미 없는 pill/tag 남발

## 12. Design Tokens

### 12.1 Color

```css
--background: #f9f8f3;
--surface: #ffffff;
--text: #131210;
--muted: #565052;
--border: rgba(19, 18, 16, 0.12);

--accent-green: #109e60;
--accent-light-green: #d7fdce;
--accent-yellow: #ffc300;
--accent-magenta: #cc1757;

--chart-blue: #2f7fb7;
--chart-green: #2e7d32;
--chart-orange: #f08a24;
--chart-red: #c62828;
```

### 12.2 Typography

- font family: Inter, system sans-serif
- H1: 56-64px desktop, 36-42px mobile
- H2: 32-40px desktop, 26-30px mobile
- body: 17-18px desktop, 16px mobile
- caption: 13-14px
- chart labels: 12-14px

### 12.3 Layout

- article max width: 720-820px
- full shell max width: 1280px
- left nav width: 220-260px
- right TOC width: 220-260px
- section vertical padding: 72-112px
- card radius: 8px
- nav/search radius: 12px
- tag radius: 4px or 8px

## 13. Chart Plan

### 13.1 Static Charts

실제 레포 데이터에서 PNG 차트를 생성한다.

1. `single_speaker_mean_cer.png`
   - 평균 CER
   - 95% bootstrap CI
   - model comparison

2. `single_speaker_cer_distribution.png`
   - 모델별 CER histogram
   - zero-heavy distribution
   - long-tail 확인

3. `single_speaker_threshold_pass_rates.png`
   - threshold별 pass rate
   - 0%, 1%, 3%, 5%, 10%, 15%, 20%

4. `single_speaker_length_bins.png`
   - 문장 길이 구간별 CER
   - 길이가 오류율에 미치는 영향 확인

5. `call_center_provider_mean_cer.png`
   - provider별 평균 CER
   - 한글 정답지 vs 숫자 정답지 비교

6. `call_center_scenario_heatmap.png`
   - scenario x provider heatmap
   - 어려운 시나리오 확인

7. `quality_gate_balanced.png`
   - pass/review/block 형태의 threshold 운영 시뮬레이션
   - 특정 vendor나 프레임워크 개념 설명이 아니라 품질 임계값 UI로 표현

### 13.2 Chart Caption Format

모든 차트는 다음 형식을 따른다.

```md
![Chart title](./assets/chart-file.png)

Figure N. 한 줄 해석.  
Source: `result/...csv`, generated by `analysis/analyze_asr_benchmarks.py`.
```

## 14. D3.js Interactive Explorer

### 14.1 Location

블로그 중후반부에 배치한다.

섹션명:

`Model Performance Explorer`

### 14.2 Purpose

독자가 CER threshold를 바꾸면서 모델별 pass/review/fail 비율이 어떻게 변하는지 직접 확인하게 한다.

### 14.3 Controls

- dataset selector
  - single speaker
  - call center
- scoped model/provider selector
  - single speaker 선택 시: AWS Transcribe, Whisper base, Whisper medium, Whisper large
  - call center 선택 시: AWS, Azure, Clova, GCP
- CER threshold slider
- optional review band slider

### 14.4 Views

- pass rate bar chart
- model comparison bar chart
- threshold marker
- selected model summary
- tooltip with exact values

### 14.5 Data

D3는 mock data를 사용하지 않는다.

입력 후보:

- `analysis/outputs/single_speaker_threshold_pass_rates.csv`
- `analysis/outputs/single_speaker_model_summary.csv`
- `analysis/outputs/call_center_provider_summary.csv`
- 필요 시 위 CSV를 변환한 JSON

### 14.6 Deployment

- GitHub Pages 기준
- 정적 HTML/JS/CSS
- 출판 경로: `docs/index.html`
- 출판 스크립트: `docs/app.js`
- 출판 스타일: `docs/styles.css`
- 출판 데이터: `docs/data/asr-benchmark.json`
- 출판 차트 이미지: `docs/assets/*.png`
- 작업/초안용 D3 explorer는 `blog/interactive/*`에도 유지한다.

## 15. Writing Style

문체:

- 한국어
- 기술 회고 + 분석 리포트
- 감정적이지 않게
- 데이터와 실험 설계를 중심으로
- 프로젝트 오너십은 자연스럽게

피할 문장:

- 특정 회사, 조직, 개인을 평가하는 문장
- 내부 맥락에 기대는 문장
- 데이터로 증명하지 않은 주장
- 모델 순위를 과도하게 일반화하는 문장

좋은 표현:

- "이 실험에서"
- "이 데이터 기준으로"
- "2023년 공개 제품/공개 모델 실험 기준으로"
- "현재 vendor 성능을 대표하지 않는다"
- "단일 화자 데이터에서는"
- "콜센터 3개 시나리오에서는"
- "n=3이므로 일반화보다는 case analysis로 해석한다"
- "평균 CER와 함께 threshold별 pass rate를 보아야 한다"

## 16. Acceptance Criteria

`BLOG_SPEC.md`는 다음 조건을 만족해야 한다.

- 목표가 명확하다.
- Guardrails는 UI/UX 레퍼런스로만 언급된다.
- `guardrail`이라는 이름은 분석 파일명, 차트명, 본문 컨셉명에 사용하지 않는다. 품질 임계값 UI는 `quality gate`로 부른다.
- 전 직장 내부 이야기가 없다.
- 2023년 공개 제품/공개 모델 실험이며 현재 Microsoft/Azure, AWS, Clova, GCP, OpenAI/Whisper 성능을 대표하지 않는다는 면책이 있다.
- 내부 성능 데이터나 비공개 vendor benchmark처럼 보이는 표현이 없다.
- 실제 레포 데이터만 사용한다고 명시한다.
- 단일 화자 데이터와 콜센터 데이터가 분리되어 설명된다.
- 단일 화자 데이터의 일반화 한계가 명시된다.
- 콜센터 n=3 데이터는 ranking이 아니라 case analysis로 표현된다.
- CER 정규화/비정규화 정책이 명시된다.
- 분석 지표가 명확하다.
- 차트 목록이 구체적이다.
- D3.js explorer의 목적과 입력 데이터가 명확하다.
- 최종 블로그 구조가 바로 구현 가능하다.

## 17. Validation Plan

데이터 검증:

- 단일 화자 결과 CSV 4개가 각각 3,922 rows인지 확인
- 단일 화자 결과 CSV 4개의 `file_name` 집합이 동일한지 확인
- 콜센터 결과 CSV 2개가 각각 3 rows인지 확인
- mock/sample/fake CSV가 새로 생기지 않았는지 확인
- `analysis/outputs/quality_gate_policy_simulation.csv`가 생성되고 `guardrail_policy_simulation.csv`가 남지 않았는지 확인
- `blog/assets/quality_gate_balanced.png`가 생성되고 `guardrail_policy_balanced.png`가 남지 않았는지 확인

분석 검증:

- 평균 CER, median, perfect rate, threshold pass rate가 `analysis/outputs`와 블로그 표에서 일치해야 한다.
- chart caption에 source file을 명시한다.
- 콜센터 n=3 결과는 통계적 일반화나 vendor ranking이 아니라 case analysis로 표현한다.
- 2023년 공개 제품/공개 모델 실험이며 현재 vendor 성능을 대표하지 않는다는 문장이 본문 초반에 있어야 한다.
- CER 계산 정책이 본문에 있어야 한다.

UI 검증:

- desktop에서 좌측 nav, 본문, 우측 TOC가 겹치지 않아야 한다. 우측 TOC는 충분한 viewport 폭에서만 표시한다.
- mobile에서 본문, 표, 차트, D3 control이 overflow 없이 접혀야 한다.
- D3 explorer는 실제 파생 데이터만 읽어야 한다.
- D3 explorer는 dataset 선택에 따라 모델/provider 목록을 분리해야 한다.
- 차트는 색상만으로 의미를 전달하지 않고 label/caption을 포함해야 한다.

## 18. Next Steps

### 18.1 Completed In Current Pass

1. `README.md`를 이 스펙 기준으로 개편했다.
2. `analysis/analyze_asr_benchmarks.py`를 정리하고 재실행 경로를 문서화했다.
3. 실제 레포 데이터에서 `analysis/outputs/*`와 `blog/assets/*.png`를 재생성했다.
4. `blog/korean-asr-benchmark-draft.md`에 블로그 본문 초안을 작성했다.
5. D3.js explorer 정적 페이지를 `blog/interactive/`에 구현했다.
6. D3 explorer가 읽는 JSON을 `blog/interactive/data/asr-benchmark.json`으로 재현 가능하게 생성했다.
7. Browser/IAB와 headless browser로 desktop/mobile 기본 렌더링과 control interaction을 검증했다.
8. GitHub repo description/topics를 설정했다.
9. GitHub Pages 출판면을 `/docs`로 결정하고 `docs/index.html`, `docs/app.js`, `docs/styles.css`, `docs/assets/*`, `docs/data/asr-benchmark.json` 구조를 추가했다.

### 18.2 Remaining

1. GitHub Pages repository setting에서 source를 `main` branch `/docs`로 설정한다.
2. 최종 게시 전 문장 톤, 이미지 caption, SEO title/description을 한 번 더 다듬는다.
3. 게시 후 Pages URL에서 이미지/CDN/D3 로딩 상태를 확인한다.
