# Evaluation protocol

The four synthetic fixtures are plumbing checks only. Reproduce their result with `python -m faultpilot.evaluation --cases cases --output outputs/smoke_evaluation.json`; do not present 4/4 as research accuracy.

The primary research data is the pinned MLDebugging JSONL in `faultpilot/data.py`. The verified source has 1,175 records. Group by `task_id`, then apply the committed SHA-256 modulo-five rule: 941 development and 234 held-out records. Preserve the 31 records with multiple recognizable category mentions and account for two without runtime feedback. Document any excluded executable cases and dependency failures.

Compare a mapped seven-class deterministic baseline, one-shot model diagnosis, conditional retrieval, bounded read/edit/test, and evidence-gated abstention on the same cases and model budget. Report macro-F1, repair-test pass, regression, abstention coverage and selective accuracy, wall time, tool calls, and token/provider cost. Use grouped bootstrap intervals and record failures. The model adapter has passed a mock HTTP contract test only; no live model or held-out benchmark result has been run.
