# Phase 2 reproducibility protocol

## Data and split

The published [MLDebugging JSONL](https://github.com/hjyTsuki/MLDebugging) is pinned by commit and SHA-256 in `faultpilot/data.py`. Download it with `python3 -m faultpilot.data --download`. The raw source is ignored by Git. The code rejects a checksum mismatch. All variants of a source `task_id` are assigned together using SHA-256 of the task ID modulo five. Remainder zero gives 234 held-out test records; the other 941 are development records. The development set is divided into 643 training and 298 validation records by hash remainder. No test label is used for threshold or prompt selection.

The published `golden_code` fields are often snippets rather than runnable files. They are never included in an agent prompt. The agent receives the buggy code, runtime feedback, and supplied unit tests. The benchmark labels are used only for diagnosis scoring.

## Execution

The harness concatenates each code candidate with its supplied `TestCases` unit test and runs it with `/usr/bin/python3 -I` inside `bubblewrap`. The sandbox has no network namespace, no home-directory bind, a temporary writable work directory, and read-only system code and configuration binds. Original-code preflight status is recorded for every test record before repair. A `setup_error` means a missing host dependency or another failure before tests ran; a `timeout` means the supplied program exceeded the configured limit. Neither is silently removed from the 234-record coverage count. Repair eligibility requires a reproduced failing test; already passing and environment-blocked examples are accounted for separately.

## Models and settings

The diagnosis classifier is TF-IDF character 3–5 grams and one-vs-rest class-balanced logistic regression. A development-validation grid selected score-fusion weight 0.0 and label threshold 0.45. A separate development-validation rule selected evidence-gate confidence floor 0.40 subject to at least 50% validation coverage. The repair model is local Ollama `qwen2.5-coder:0.5b`, digest `4ff64a7f502a08b7616edb8ca0a79eb1853fc363d842b7df4b46915d11a3fb09`, JSON schema output, temperature zero, seed 17, maximum 420 generated tokens, and at most two edit attempts. The frozen prompt is `line-json-v2`. Its output must identify a numbered source line and supply one replacement line; the validator also accepts the earlier exact one-occurrence old/new contract. Every candidate is tested in a fresh isolated process. A passing patch is labelled **verified by supplied tests**, which does not imply general correctness.

The measured server used Ollama 0.40.14's 4,096-token default context on CPU. Model calls are kept on the same local server throughout the paired comparison. `results/environment.json` records the remaining software versions. The repair wall clock in each trace excludes the separately precomputed diagnosis and preflight; E6 should label it as model/patch/test time, not complete end-to-end latency.

E6 summaries include mean, median and standard deviation of latency across held-out cases. This is between-case spread, not standard deviation across repeated stochastic runs. The model uses temperature zero and a fixed seed; one development prompt was repeated three times as a limited stability check.

The prompt builder limits runtime feedback to 1,700 characters, buggy code to 8,000 characters and supplied tests to 2,300 characters, and passes no gold code. Long inputs may lose relevant context; this is a stated threat to validity. The development pilot compared the old/new and numbered-line contracts, then froze `line-json-v2` before the reported run.

For the Phase 1 evidence-relevance target, `experiments.evidence_audit` selects the first 50 held-out case IDs in SHA-256 order and writes the code, runtime feedback, predicted categories, and extracted spans to a CSV. It leaves human yes/no judgments blank; `--score` refuses incomplete sheets and counts missing spans as non-relevant. The generated sheet has 39 spans present out of 50, which is an availability upper bound, not a relevance score.

## Required comparisons

| Experiment | Implementation and saved result |
| --- | --- |
| E1 | `python3 -m experiments.run_diagnostics`; `results/diagnostic_evaluation.json` contains Phase 1 rule baseline, learned diagnosis, and retrieval-fusion ablation over all 234 test records. |
| E2 | `python3 -m experiments.run_repairs --mode E2_repairagent_style`; output under `results/repairs/`. This is a Python adaptation of RepairAgent's bounded inspect/edit/test loop, not the original Java implementation. |
| E3 | `python3 -m experiments.run_repairs --mode E3_full`; same eligible cases, model, attempts, and tests as E2. |
| E4 | Compare E3 with the three one-component removals using the metrics defined below. Retrieval evidence coverage and diagnosis macro F1 address Gap 1; test-gated versus unverified proposals address Gap 2; gate coverage and conditional success address Gap 3. |
| E5 | `python3 -m experiments.run_repairs --mode all` runs `E5_no_retrieval`, `E5_no_verification`, and `E5_no_gate` as paired ablations. |
| E6 | Every mode saves wall time, prompt/output tokens, tool calls, provider errors, and test outcomes. Local inference has no per-call API fee; electricity and hardware cost are unmeasured. |

For the repair modes, `--limit N` selects the first N eligible case IDs in a fixed SHA-256 order. Without a limit, all 234 held-out records receive a trace: the agent attempts model repair on reproduced failures and records explicit blocked or already-passing states for the others. Any limited pilot must disclose N and must not be presented as a full test-set result. Outputs are line-oriented JSON and resumable by case ID. The model is deterministic by configuration, so three-run averaging is required only if a stochastic configuration is introduced; actual repeatability must still be checked before making a determinism claim.

`experiments.export_trace_samples` reconstructs the exact prompt and full candidate source for the final-system representative cases from the pinned input and saved edit trajectory. The proposal and test outcome fields are copied from the original trace, and reconstruction is labelled in the exported JSON. The export is a reviewer aid, not a new model run.

## Base-paper comparison boundary

[RepairAgent](https://github.com/sola-st/RepairAgent) was published for Java Defects4J. Its reported 164 correct fixes are from that setting and are **not** a directly comparable result on these Python MLDebugging tasks. The E2 code transfers the inspect/edit/test idea to the same local Python cases and budget as E3. Label E2 as a reproduced *adaptation*; never attribute its score to the original authors or equate the original reported count with Python pass rate.

## Threats and constraints

The benchmark supplies no independent regression suite, gold faulty line, or uniform dependency environment. Therefore code-line evidence availability is measurable, while line-localization correctness and semantic repair correctness cannot be established from these files alone. Missing dependencies and unsupported patches remain explicit failure categories. The selected local model is small because this machine has no GPU; results may not transfer to stronger models. The original Java RepairAgent cannot be evaluated here without a separate Java/Defects4J setup.
