# Revisiting a Korean ASR Benchmark

Status: draft
Project: `job-transcribe`
Source analysis: `analysis/analyze_asr_benchmarks.py`

## Summary

In 2023, I designed and ran a Korean ASR/STT benchmark using publicly available products and open models. This draft revisits the same repository data without creating mock CSV files. The goal is to read the experiment through distributions, thresholds, paired comparisons, worst cases, and call-center notation sensitivity rather than a single average CER.

The scope is important. These results reflect a personal 2023 experiment using public products and public/open models. They do not represent current Microsoft/Azure, AWS, Clova, GCP, or OpenAI/Whisper performance. They are not official benchmarks or internal performance data from any company.

## Reading The Experiment As A Story

The original question seemed simple: if Korean speech-to-text were attached to a practical workflow, which model would transcribe it well enough? The harder question appeared once testing started: what does "well enough" mean, and under which reference-text policy should it be measured?

The original Korean columns are available at [ITDaily](https://www.itdaily.kr/news/articleView.html?idxno=213297) and [ComputerWorld](https://www.comworld.co.kr/news/articleView.html?idxno=50818).

STT output is not simply right or wrong. One model may preserve meaning but change spacing. Another may write spoken numbers as digits. Another may fail on proper nouns, loanwords, or domain-specific expressions. In financial conversations, this gets even more sensitive: "오육칠팔" and "5678" may be close in meaning but different at the character level.

That is why I built a separate measurement tool for this test: Compute STT Error Rate, published as [`computing-Korean-STT-error-rates`](https://github.com/hyeonsangjeon/computing-Korean-STT-error-rates). The benchmark scripts import it as the `nlptutti` package. Nlptutti provides `get_cer`, `get_wer`, `get_crr`, and Korean keyword-pattern utilities. Internally, it uses Levenshtein edit distance to count substitutions, deletions, and insertions, while fixing whitespace and punctuation handling in code.

I built it because the denominator mattered. If CER is computed only against the reference length, transcripts with many insertions can exceed 1 or move outside the 0-1 range I wanted for repeated comparison. Nlptutti uses `S+D+I` as the error numerator and `S+D+I+C` as the denominator, including insertions in the normalized error rate. That small rule made the results easier to compare across thousands of Korean transcripts.

The experiment had two surfaces. The first was the main single-speaker benchmark: 3,922 utterances sharing the same `file_name` and `ground_truth` across AWS Transcribe and Whisper base, medium, and large. The core 3,922 utterances were my own voice data. I read and recorded them one by one as WAV files in a low-reflection environment. The accumulated reading and recording time was close to eight hours, and the full experiment design, recording, STT runs, result collection, and metric stabilization took roughly three months.

The second surface was a small financial call-center persona test: PB bond ordering, startup loan guidance, and an auto-insurance premium inquiry. The team used these as short practical checks, around 30 minutes in scale. They are not a provider ranking dataset. They are a case analysis for numeric notation, domain vocabulary, and reference-text policy.

The hardest work was not running one model. It was putting the different outputs on the same analytical surface. Providers returned different file formats and transcript structures, and Korean evaluation is sensitive to spacing, punctuation, and number notation. That is why this benchmark should be read as a measurement-rule story, not a leaderboard.

## Data

The experiment has two parts.

The first part is a 3,922-utterance single-speaker benchmark. It compares AWS Transcribe, Whisper base, Whisper medium, and Whisper large on the same sentence set. This is the main dataset for mean CER, distribution, threshold pass rate, paired comparison, and worst-case analysis.

The second part is a three-scenario financial call-center case analysis. It compares AWS, Azure, Clova, and GCP transcripts against both Hangul-written and numeric-written references.

| Area | Source files |
|---|---|
| Single speaker | `meta_voice_data_3922.csv`, `result/result_3922.csv`, `result/openai_whisper_base_result_3922.csv`, `result/openai_whisper_medium_result_3922.csv`, `result/openai_whisper_large_result_3922.csv` |
| Call center | `preprocess/cs_hangul_data.csv`, `preprocess/cs_num_data.csv`, `result/cs_hangul_result.csv`, `result/cs_number_result.csv` |
| Raw/intermediate call-center outputs | `tmp_data/aws/*`, `tmp_data/azure/*`, `tmp_data/clova/*`, `tmp_data/gcp/*`, `tmp_data/groundtruth/*` |

## Measurement Method

The primary metric is CER, Character Error Rate. CER measures how different the transcript is from the reference at the character level. In Korean STT, CER is sensitive to spacing, numeric notation, English words, proper nouns, and punctuation.

The original experiment calculated CER through Nlptutti. The AWS single-speaker results were measured in `measure_nlp_cer_job.py` with `nlptutti.get_cer(ground_truth_sentence, transcribe_sentence)["cer"]`. Whisper transcripts were generated in `oepnai_job.py` and measured through the same function. The call-center results were measured in `measure_cs_job.py` against both Hangul and numeric references.

This reanalysis uses the stored `cer` values from the existing result CSV files. It does not recalculate CER with a new normalization policy for the blog.

## Single-Speaker Results

On the 3,922 single-speaker utterances, Whisper large had the lowest mean CER at 2.22%. Whisper medium followed at 2.64%, AWS Transcribe at 3.73%, and Whisper base at 9.35%.

| Model | Mean CER | Median CER | Perfect | <=5% CER | >10% CER |
|---|---:|---:|---:|---:|---:|
| Whisper large | 2.22% | 0.00% | 70.27% | 83.20% | 5.69% |
| Whisper medium | 2.64% | 0.00% | 65.12% | 79.50% | 7.24% |
| AWS Transcribe | 3.73% | 0.00% | 56.12% | 71.01% | 12.32% |
| Whisper base | 9.35% | 6.94% | 29.12% | 41.13% | 37.33% |

The threshold view changes the reading. At a 5% CER pass threshold, Whisper large passed 83.20% of utterances, Whisper medium 79.50%, AWS Transcribe 71.01%, and Whisper base 41.13%. At a 10% threshold, Whisper large reached 94.31%, Whisper medium 92.76%, AWS Transcribe 87.68%, and Whisper base 62.67%.

This is why the tail matters. A low mean can still hide outputs that need review, fallback, or manual correction.

## Call-Center Case Analysis

The call-center data should not be read as a provider ranking because it has only three scenarios. Its value is in showing how reference notation changes CER.

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

The insurance persona makes the point clearly. Azure moved from 11.54% CER under the Hangul reference to 8.79% under the numeric reference, while AWS moved from 11.99% to 14.51%. The same conversation can be scored differently depending on whether the reference expects Korean-written numbers or digit-style numbers.

## Lessons Learned

First, mean CER is not enough for operational decisions. A mean shows the broad trend, but threshold pass rate and tail risk are closer to the decisions made in real workflows.

Second, reference-text policy matters as much as model behavior. Korean spacing, punctuation, number notation, loanwords, and proper nouns can all move CER materially.

Third, a measurement tool is part of the experiment. Nlptutti made it possible to measure 3,922 utterances and call-center transcripts through the same rule. The `S+D+I+C` denominator kept insertion-heavy transcripts comparable within a normalized CER scale.

Fourth, a small case analysis is not a leaderboard. The three call-center scenarios explain how domain language and number notation affect error rate, but they should not be generalized into current provider rankings.

Finally, a reproducible repository can bring an old experiment back to life. Because the recordings, result files, preprocessing CSVs, scripts, JSON, and PNG outputs were preserved, this three-month 2023 experiment could be revisited without inventing mock data.

## Conclusion

The single-speaker data shows strong 2023 results from Whisper large and medium, and AWS Transcribe was more stable than Whisper base in this dataset. But the most important result is the method, not the model order.

Korean ASR evaluation should publish reference-text policy, thresholds, tail risk, and disagreement examples alongside average CER. Otherwise, the number is too easy to overread.
