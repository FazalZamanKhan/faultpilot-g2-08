# Factual evidence for Fazal's paper writing

This is a data and source checklist, not paper prose. The Phase 2 brief requires Fazal to write the assessed manuscript in his own words and to verify every claim against the cited source or saved result.

| Item | Reproducible evidence |
| --- | --- |
| Identity | Fazal Zaman Khan, 22I-2362, solo, G2-08. Confirm the email in `main.tex`. |
| Fixed base paper | RepairAgent, DOI <https://doi.org/10.1109/ICSE55347.2025.00157>; original Java/Defects4J study, reported 164 correct fixes. Do not compare that count directly with Python MLDebugging rates. |
| Benchmark | MLDebugging, DOI <https://doi.org/10.18653/v1/2025.findings-acl.305>; pinned source commit and SHA-256 in `faultpilot/data.py`. |
| Split | 1,175 records; source-task-grouped 941 development and 234 held-out test. Development training 643, validation 298. `results/test_manifest.json`, `experiments/diagnostic_config.json`. |
| Multi-label policy | Preserve all recognized labels. There are 31 multi-label records in the full source and five in test. `outputs/mldebugging_profile.json`, `results/test_manifest.json`. |
| Original execution | On the 234 held-out cases at 12 seconds: 198 reproduced failing tests, 30 setup errors, five timeouts, one original pass. `results/test_preflight.jsonl`. |
| E1 diagnosis | Phase 1 mapped rules macro F1 0.04082, exact match 0.00427. Learned classifier macro F1 0.31054, exact match 0.08120. Retrieval score fusion weight 0.2 macro F1 0.29062. `results/diagnostic_evaluation.json`. |
| Diagnosis uncertainty | Learned minus rules macro F1 0.26973, task-group bootstrap 95% interval [0.18266, 0.35415], 2,000 resamples, seed 17. `results/diagnostic_ci.json`; figure `diagnosis_macro_f1.png`. |
| Evidence availability | Local source-line evidence for 194/234; retrieved development examples for 234/234. Availability does not establish localization correctness because no gold faulty line exists. `results/diagnostic_evaluation.json`. |
| Fixed 50-case audit | `results/evidence_audit_50.csv` has 39 cases with any source span and 11 without. Even perfect relevance among available spans would be 39/50 = 78%, below the Phase 1 80% target. The relevance column is blank pending a manual review; do not claim a completed relevance audit. |
| Gap 3 diagnosis gate | Development-selected floor 0.40; answered 194/234 (82.906% coverage). Exact match 0.08247 on answered cases versus 0.08120 always-answer, gain 0.00128. This misses the Phase 1 +0.10 target. `results/gate_evaluation.json`. |
| E1 repair scale | The Phase 1 baseline makes no edit and therefore has zero verified repair passes by design. `results/E1_baseline_repair.json`. |
| Frozen repair settings | `qwen2.5-coder:0.5b`, digest `4ff64a7f502a08b7616edb8ca0a79eb1853fc363d842b7df4b46915d11a3fb09`, Ollama 0.40.14 CPU, temperature 0, seed 17, JSON schema, at most two attempts, `line-json-v2` prompt, 12-second sandbox tests. `results/environment.json`, `faultpilot/agent.py`. |
| Development choice | Ten development-validation cases: one supplied-test pass, eight exhausted, one abstained, mean wall 26.78 seconds. The 1.5B model exhausted the same first case in 132.25 seconds; the 0.5B model was selected for the full run. `results/development_pilot_schema_0_5b.jsonl`, `results/development_pilot_schema_1_5b.jsonl`. |
| Determinism check | Three repeated calls on one fixed development prompt gave identical proposals; this does not prove global determinism. `results/determinism_check.json`. |
| Repair experiment | E2 adaptation, E3 full, three one-switch ablations and E6 metrics are recorded in `results/repairs/` after the frozen run completes. Use `results/repair_aggregate.json` and `results/failure_analysis.json` for final numbers. Do not write a result before those files exist. |

## Required interpretation boundaries

- A patch passing supplied tests is **verified by supplied tests**, not proven semantically correct. The benchmark lacks an independent regression suite.
- Missing system packages and timeouts limit executable coverage. Retain all 234 in the accounting and use 198 as the fixed repair-eligible denominator.
- Retrieval score fusion and the diagnosis evidence gate have weak or negative results so far; report them without changing the frozen test design.
- The E2 Python adaptation is not the original RepairAgent Java implementation. State reported versus reproduced results separately.
- Model inference has zero billed API fees locally; electricity and hardware cost are unmeasured.
- Every figure/table number must match repository results. The 8–10 page paper, all prose and captions, and both Turnitin reports remain the student's responsibility under the course brief.
