# Korean ASR Benchmark: Job Transcribe

한국어 ASR/STT 모델과 클라우드 STT 결과를 실제 실험 데이터로 비교한 벤치마크 프로젝트입니다. 단일 화자 3,922문장과 금융 콜센터 3개 시나리오를 대상으로 CER(Character Error Rate), 완전 인식률, threshold별 pass rate, worst/disagreement 사례를 분석합니다.

이 레포의 블로그 방향과 UI/UX 스펙은 [blog/BLOG_SPEC.md](blog/BLOG_SPEC.md)에 정리되어 있습니다.

## Scope

이 분석은 2023년에 공개적으로 접근 가능한 제품과 오픈소스 모델을 사용해 수행한 개인 프로젝트성 실험 결과를 재정리한 것입니다.

중요한 해석 범위:

- 현재 시점의 Microsoft/Azure, AWS, Clova, GCP, OpenAI/Whisper 제품 성능을 대표하지 않습니다.
- 각 회사의 공식 벤치마크, 내부 성능 데이터, 비공개 benchmark가 아닙니다.
- 공개 제품 또는 공개 모델을 대상으로 한 실험 결과와 이 레포에 남아 있는 실제 결과 파일만 재분석합니다.
- 단일 화자 3,922건은 같은 화자/녹음 조건의 비교이며, 다른 화자군이나 운영 환경으로 일반화하지 않습니다.
- 콜센터 3개 시나리오는 case analysis로만 해석합니다.

## Data

단일 화자 벤치마크:

- `meta_voice_data_3922.csv`
- `result/result_3922.csv`
- `result/openai_whisper_base_result_3922.csv`
- `result/openai_whisper_medium_result_3922.csv`
- `result/openai_whisper_large_result_3922.csv`

금융 콜센터 시나리오:

- `preprocess/cs_hangul_data.csv`
- `preprocess/cs_num_data.csv`
- `result/cs_hangul_result.csv`
- `result/cs_number_result.csv`
- `tmp_data/{aws,azure,clova,gcp,groundtruth}/*`

목업 CSV는 사용하지 않습니다. `analysis/outputs/*`, `blog/assets/*`, `docs/assets/*`, `blog/interactive/data/asr-benchmark.json`, `docs/data/asr-benchmark.json`은 위 원천 데이터에서 재생성되는 파생 산출물입니다.

## Current Results

단일 화자 3,922문장 기준:

| Model | Mean CER | Median CER | Perfect | <=5% CER | >10% CER |
|---|---:|---:|---:|---:|---:|
| Whisper large | 2.22% | 0.00% | 70.27% | 83.20% | 5.69% |
| Whisper medium | 2.64% | 0.00% | 65.12% | 79.50% | 7.24% |
| AWS Transcribe | 3.73% | 0.00% | 56.12% | 71.01% | 12.32% |
| Whisper base | 9.35% | 6.94% | 29.12% | 41.13% | 37.33% |

금융 콜센터 3개 시나리오 기준:

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

콜센터 결과는 표본 수가 작기 때문에 provider ranking이 아니라 시나리오별 오류 양상과 숫자 표기 민감도를 보기 위한 자료입니다.

## Reproduce

분석 의존성:

```bash
uv run --python /usr/bin/python3 --with pandas --with numpy --with matplotlib python analysis/analyze_asr_benchmarks.py
```

위 명령은 다음 파일을 재생성합니다.

- `analysis/outputs/single_speaker_model_summary.csv`
- `analysis/outputs/single_speaker_threshold_pass_rates.csv`
- `analysis/outputs/single_speaker_paired_deltas.csv`
- `analysis/outputs/single_speaker_worst_examples.csv`
- `analysis/outputs/single_speaker_disagreement_examples.csv`
- `analysis/outputs/call_center_long.csv`
- `analysis/outputs/call_center_provider_summary.csv`
- `analysis/outputs/quality_gate_policy_simulation.csv`
- `blog/interactive/data/asr-benchmark.json`
- `docs/data/asr-benchmark.json`
- `blog/assets/*.png`
- `docs/assets/*.png`

분석 스크립트는 다음 무결성 검사를 수행합니다.

- 단일 화자 4개 결과 CSV의 `file_name` 집합 일치
- 콜센터 결과 row count와 scenario count 일치
- 필수 컬럼 존재 여부

## Blog And UI

블로그는 Guardrails AI의 문서/블로그 UI를 레퍼런스로 삼습니다. 단, Guardrails 개념 프레임을 차용하는 것이 아니라 UI/UX만 참고합니다.

현재 산출물:

- GitHub Pages 출판 페이지: [docs/index.html](docs/index.html)
- 블로그 스펙: [blog/BLOG_SPEC.md](blog/BLOG_SPEC.md)
- 블로그 초안: [blog/korean-asr-benchmark-draft.md](blog/korean-asr-benchmark-draft.md)
- 정적 PNG 차트: [blog/assets](blog/assets)
- D3.js 기반 `Model Performance Explorer`: [blog/interactive/index.html](blog/interactive/index.html)
- D3 데이터: [blog/interactive/data/asr-benchmark.json](blog/interactive/data/asr-benchmark.json)
- Pages 데이터: [docs/data/asr-benchmark.json](docs/data/asr-benchmark.json)

로컬 미리보기:

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

브라우저에서 `http://127.0.0.1:8765/docs/`를 엽니다.

GitHub Pages는 repository settings에서 source를 `main` branch의 `/docs`로 설정하는 구조를 기준으로 합니다.

## Repository Layout

```text
analysis/
  analyze_asr_benchmarks.py
  outputs/
blog/
  BLOG_SPEC.md
  korean-asr-benchmark-draft.md
  assets/
  interactive/
docs/
  index.html
  app.js
  styles.css
  assets/
  data/
preprocess/
result/
tmp_data/
trans_util/
```

## Notes

- 기존 CER 값은 레포 결과 CSV의 `cer` 컬럼을 그대로 사용합니다.
- 블로그 재분석 단계에서 공백, 문장부호, 영문 대소문자, 숫자를 새로 정규화해 재계산하지 않습니다.
- 향후 별도 정규화 정책을 적용하면 기존 결과와 분리해 표시해야 합니다.
