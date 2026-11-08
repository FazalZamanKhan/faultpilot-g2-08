# Phase 2 rubric evidence map

This map points to inspectable artifacts. It does not predict a mark. The Phase 2 course brief awards 40 marks for code and reproducibility and 60 for the research paper; the supervisor determines the mark within each criterion. Both Turnitin reports are mandatory for any evaluation.

| Criterion | Evidence in this repository | Remaining limit or action |
| --- | --- | --- |
| A1: end-to-end agent | `faultpilot/agent.py`, `faultpilot/sandbox.py`, `faultpilot/repair_cli.py`, `results/repairs/*.jsonl` | Saved held-out repairs did not pass the supplied tests. |
| A2: gap components | `faultpilot/diagnostics.py`, `AgentSettings.retrieval`, `AgentSettings.verification`, `AgentSettings.evidence_gate`, `experiments/run_repairs.py`, complete E5 traces | Components are switchable; their measured repair effects are weak or negative. |
| A3: robustness and iteration | `docs/devlog.md`, development pilots, edit rejection and sandbox outcomes in traces | No held-out successful repair to analyze. |
| A4: repository quality | `README.md`, `requirements.txt`, `tests/`, public Git history | Check final public release and absence of secrets. |
| A5: reproducibility | `docs/phase2_protocol.md`, pinned data loader, `results/environment.json`, `results/repair_validation.json`, `results/repair_aggregate.json` | Check the public `phase2-final` release URL. |
| B1: baseline and base paper | `results/E1_baseline_repair.json`, `results/diagnostic_evaluation.json`, E2 adaptation traces, `paper/evidence_notes.md` | Original RepairAgent Java result is reported context; the Python adaptation is the measured same-data comparison. |
| B2: gap experiments | Diagnosis, evidence, gate, repair and ablation files in `results/`; completed README gap table; separate AI-assisted 50-case evidence review | Independent regression correctness is not measured; AI-assisted relevance judgments do not replace human validation. |
| B3: ablation and efficiency | E5 JSONL files, `experiments/aggregate.py`, `experiments/measure_diagnosis_latency.py`, `results/determinism_check.json` | Report single-run and repeat-test limits honestly. |
| B4: failure analysis | `results/failure_analysis.json`, `results/trace_samples.json`, `paper/failure_categories.png` | Two successful held-out examples cannot be supplied because there were none. |
| B5–B7: research paper | `paper/main.tex`, `paper/author_plan.md`, `paper/evidence_notes.md`, generated figures and bibliography | Fazal must write original prose and captions, produce an 8–10 page PDF, and obtain both Turnitin reports. |

See `docs/phase2_submission.md` for the exact Classroom upload set and filenames.
