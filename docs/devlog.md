# Phase 2 development log

All dates are Pakistan Standard Time. The held-out split was fixed by the Phase 1 SHA-256 task rule before Phase 2 experiments. The benchmark source and checksum are pinned in `faultpilot/data.py`.

| Date | Observed limitation | Change | Measured effect |
| --- | --- | --- | --- |
| 2026-11-06 | The Phase 1 baseline had only four synthetic smoke cases and no benchmark score. | Added a checksum-verified loader, the 941/234 grouped development/test split, a seven-category mapping, and a sandboxed evaluator. | The first held-out diagnosis run measured Phase 1 rules at macro F1 0.04082 on 234 records. This is a new measurement, not a Phase 1 claim. |
| 2026-11-06 | The proposed retrieval score fusion might be unhelpful. | Tuned classifier threshold and fusion weight on 298 development-validation records; trained on the remaining 643. | Selected threshold 0.45 and weight 0.0 with validation macro F1 0.42886. Weight 0.2 at threshold 0.45 scored 0.39819. This decision preceded held-out scoring. |
| 2026-11-06 | The initial preflight counted many setup errors. | Inspected the first failure: Debian Matplotlib needed `/etc/matplotlibrc`, which the isolated runner had hidden. Added read-only bindings for that file and font configuration. Aligned the preflight and repair timeouts at 12 seconds. | On 234 held-out records, the corrected preflight has 198 reproduced failures, 30 setup errors, five timeouts and one already passing record. The earlier 98-setup-error count is invalid. |
| 2026-11-06 | The Phase 1 rule baseline covered very few of the seven published fault categories. | Trained a character n-gram multi-label classifier on development cases; retained retrieval as provenance evidence and measured score fusion separately. | On 234 held-out records, macro F1 was 0.31054 for the classifier versus 0.04082 for Phase 1 rules. Retrieval score fusion at weight 0.2 reduced macro F1 to 0.29062. The evidence output does not have a gold localization score. |
| 2026-11-06 | The first local 0.5B repair pilot returned invalid old/new edits and spent 33–83 seconds per case on three development-validation cases. | Switched to a numbered source-line contract, reduced prompt length, and constrained Ollama with a JSON schema. | On those same three development cases, the schema pilot took 5–7 seconds each and returned structured proposals, but zero passed the supplied tests. This is a format and speed improvement, not a repair-quality gain. |

## Integrity notes

- Validation uses only development records. The held-out test set is for frozen comparisons and failure accounting.
- The base paper's original Java/Defects4J implementation cannot be directly run on MLDebugging Python tasks; the Python adaptation must be labelled as such.
- A passing supplied test is evidence limited to that test. The dataset does not provide an independent regression suite or gold fault-line annotations.
- This log records technical observations and generated measurements. The assessed paper must be written by Fazal in his own words under the Phase 2 instructions.
