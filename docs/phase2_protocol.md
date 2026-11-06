# Phase 2 reproducibility protocol

## Data and split

The published [MLDebugging JSONL](https://github.com/hjyTsuki/MLDebugging) is pinned by commit and SHA-256 in `faultpilot/data.py`. Download it with `python3 -m faultpilot.data --download`. The raw source is ignored by Git. The code rejects a checksum mismatch. All variants of a source `task_id` are assigned together using SHA-256 of the task ID modulo five. Remainder zero gives 234 held-out test records; the other 941 are development records. The development set is divided into 643 training and 298 validation records by hash remainder. No test label is used for threshold or prompt selection.

The published `golden_code` fields are often snippets rather than runnable files. They are never included in an agent prompt. The agent receives the buggy code, runtime feedback, and supplied unit tests. The benchmark labels are used only for diagnosis scoring.

## Execution

The harness concatenates each code candidate with its supplied `TestCases` unit test and runs it with `/usr/bin/python3 -I` inside `bubblewrap`. The sandbox has no network namespace, no home-directory bind, a temporary writable work directory, and read-only system code and configuration binds. Original-code preflight status is recorded for every test record before repair. A `setup_error` means a missing host dependency or another failure before tests ran; a `timeout` means the supplied program exceeded the configured limit. Neither is silently removed from the 234-record coverage count. Repair eligibility requires a reproduced failing test; already passing and environment-blocked examples are accounted for separately.

## Models and settings

The diagnosis classifier is TF-IDF character 3–5 grams and one-vs-rest class-balanced logistic regression. A development-validation grid selects score-fusion weight and label threshold. The evidence gate also uses a development-validation selection rule. The repair model is local Ollama `qwen2.5-coder:0.5b`, JSON output, temperature zero, seed 17, maximum 420 generated tokens, and at most two edit attempts. Its output must identify a numbered source line and supply one replacement line; the validator also accepts the earlier exact one-occurrence old/new contract. Every candidate is tested in a fresh isolated process. A passing patch is labelled **verified by supplied tests**, which does not imply general correctness.

## Required comparisons

| Experiment | Implementation and saved result |
| --- | --- |
| E1 | `python3 -m experiments.run_diagnostics`; `results/diagnostic_evaluation.json` contains Phase 1 rule baseline, learned diagnosis, and retrieval-fusion ablation over all 234 test records. |
| E2 | `python3 -m experiments.run_repairs --mode E2_repairagent_style`; output under `results/repairs/`. This is a Python adaptation of RepairAgent's bounded inspect/edit/test loop, not the original Java implementation. |
| E3 | `python3 -m experiments.run_repairs --mode E3_full`; same eligible cases, model, attempts, and tests as E2. |
| E4 | Compare E3 with the three one-component removals using the metrics defined below. Retrieval evidence coverage and diagnosis macro F1 address Gap 1; test-gated versus unverified proposals address Gap 2; gate coverage and conditional success address Gap 3. |
| E5 | `python3 -m experiments.run_repairs --mode all` runs `E5_no_retrieval`, `E5_no_verification`, and `E5_no_gate` as paired ablations. |
| E6 | Every mode saves wall time, prompt/output tokens, tool calls, provider errors, and test outcomes. Local inference has no per-call API fee; electricity and hardware cost are unmeasured. |

For the repair modes, `--limit N` selects the first N eligible case IDs in a fixed SHA-256 order. Any limited pilot must disclose N and must not be presented as a full test-set result. Outputs are line-oriented JSON and resumable by case ID. The model is deterministic by configuration, so three-run averaging is required only if a stochastic configuration is introduced; actual repeatability must still be checked before making a determinism claim.

## Base-paper comparison boundary

[RepairAgent](https://github.com/sola-st/RepairAgent) was published for Java Defects4J. Its reported 164 correct fixes are from that setting and are **not** a directly comparable result on these Python MLDebugging tasks. The E2 code transfers the inspect/edit/test idea to the same local Python cases and budget as E3. Label E2 as a reproduced *adaptation*; never attribute its score to the original authors or equate the original reported count with Python pass rate.

## Threats and constraints

The benchmark supplies no independent regression suite, gold faulty line, or uniform dependency environment. Therefore code-line evidence availability is measurable, while line-localization correctness and semantic repair correctness cannot be established from these files alone. Missing dependencies and unsupported patches remain explicit failure categories. The selected local model is small because this machine has no GPU; results may not transfer to stronger models. The original Java RepairAgent cannot be evaluated here without a separate Java/Defects4J setup.
