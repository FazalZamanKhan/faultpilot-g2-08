# FaultPilot Phase 2 frozen evaluation

This release contains the implementation, reproducible experiment scripts, pinned dataset loader, held-out traces, validated summaries, figures, and an IEEE paper source scaffold for project G2-08. The assessed paper text and Turnitin reports are separate student-authored submission items.

The evaluation uses 234 held-out MLDebugging records, including 198 reproduced failures eligible for repair. The same local `qwen2.5-coder:0.5b` model digest, two-attempt limit, and 12-second isolated-test limit were used for the paired repair modes.

## Measured outcomes

| Mode | Supplied-test passes / 198 eligible | Note |
| --- | ---: | --- |
| E1 Phase 1 rules | 0 | Diagnosis-only; makes no edit. |
| E2 Python RepairAgent-style adaptation | 0 | Not the original authors' Java implementation. |
| E3 FaultPilot full | 0 | One provider interruption was retried with unchanged settings. |
| E5 no retrieval | 1 | Supplied-test pass, not proven semantic correctness. |
| E5 no verification | 0 verified; 0 offline audit passes | 123 unverified proposals; agent made no test-tool calls. |
| E5 no evidence gate | 0 | No abstentions; 0.979 mean tool calls versus 0.838 in E3. |

Diagnosis, failure, latency, token, and tool-call figures are in `README.md` and `results/`. All five modes passed `experiments.validate_results`. The original RepairAgent paper's Java result is context only and is not numerically comparable to these Python results. See `docs/phase2_protocol.md`, `docs/rubric_evidence.md`, and `docs/phase2_submission.md` for reproduction and submission boundaries.
