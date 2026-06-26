# ASR Benchmark Summary

Generated from repository data by `analysis/analyze_asr_benchmarks.py`.

## Single-speaker 3,922 utterances

| Model | Mean CER | Median CER | Perfect | <=5% CER | >10% CER |
|---|---:|---:|---:|---:|---:|
| Whisper large | 2.22% | 0.00% | 70.27% | 83.20% | 5.69% |
| Whisper medium | 2.64% | 0.00% | 65.12% | 79.50% | 7.24% |
| AWS Transcribe | 3.73% | 0.00% | 56.12% | 71.01% | 12.32% |
| Whisper base | 9.35% | 6.94% | 29.12% | 41.13% | 37.33% |

## Single-speaker best/worst counts

| Model | Sole-best count | Best-or-tied count | Sole-worst count |
|---|---:|---:|---:|
| Whisper large | 275 | 3351 | 49 |
| AWS Transcribe | 262 | 2648 | 418 |
| Whisper medium | 147 | 3089 | 70 |
| Whisper base | 25 | 1341 | 1981 |

## Financial call-center samples

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

## Balanced quality gate policy

Pass: CER <= 5%, review: 5% < CER <= 15%, block: CER > 15%.

| Model | Pass | Review | Block |
|---|---:|---:|---:|
| Whisper large | 83.20% | 14.86% | 1.94% |
| Whisper medium | 79.50% | 17.75% | 2.75% |
| AWS Transcribe | 71.01% | 23.66% | 5.33% |
| Whisper base | 41.13% | 36.64% | 22.23% |
