# Phase 1 — student-authored submission worksheet

> NOT FOR DIRECT SUBMISSION. The course prohibits AI-generated writing in the submitted literature review and proposal. Fill these prompts in your own words after reading each paper.

Project: G2-08 — FaultPilot: A Taxonomy-Grounded Agentic Debugging Assistant for Python AI Applications
Group head name / roll number: Fazal Zaman Khan / 22I-2362
Other group members' names / roll numbers: None — solo project
Supervisor: Meemon Khan (listed for G2 projects in the course brief)
GitHub URL: https://github.com/FazalZamanKhan/faultpilot-g2-08
Required final PDF filename: `Phase1_G2-08_22I-2362.pdf`

## Deliverable A: Literature review and research gaps

### Papers 1–10 (2025/2026 peer-reviewed only)
For **each** paper write 150–250 words of your own critical analysis: full IEEE reference; problem; method/agent architecture; dataset/benchmark; exact quantitative results and metrics; authors' limitations; your own limitations; relation to FaultPilot. Provide DOI/proceedings URL and evidence of peer review.

### Base paper
Proposed base: RepairAgent (ICSE 2025 Research Track). Its [publication record](https://conf.researchr.org/details/icse-2025/icse-2025-research-track/160/RepairAgent-An-Autonomous-LLM-Based-Agent-for-Program-Repair) and [CORE 2023 A* listing for ICSE](https://portal.core.edu.au/conf-ranks/?by=all&page=1&search=&sort=arank&source=CORE2023) are linked in `research/source_shortlist.md`. The group still needs to read the full paper, report the exact benchmark and metrics, and justify a fair comparison with its Python setting.

### Comparison matrix
| Paper | Year/venue | Data | Method | Metrics | Exact results | Limitation |
|---|---|---|---|---|---|---|
| [1–10] | | | | | | |

### Three provisional gaps — confirm against named papers
1. Taxonomy-grounded diagnosis vs ungrounded diagnosis. Accuracy / macro-F1 on labeled faults.
2. Verified repair vs one-shot suggestion. Reproduction-test pass rate and regression rate.
3. Evidence-aware abstention vs always-answer. Selective accuracy / coverage / unsafe suggestion rate.

**Do not claim these are evidence-backed until supported by your ten paper reviews.**

## Deliverable B: proposal — write in your own words
1. Project seed, title, motivation and target users.
2. Base paper, its limits, and three literature-grounded gaps.
3. Final product: local Python debugging CLI with optional VS Code integration.
4. Why the final design needs tool-using iterative agent behavior rather than just a static lookup.
5. Three research questions, one per gap, and testable hypotheses.
6. Confirmed data/environment: local, reproducible Python failure cases in `cases/`; expand using documented real AI/ML failures with licenses/provenance.
7. Architecture: input -> taxonomy retrieval -> diagnosis -> proposed repair -> isolated verification -> retry/abstain -> report.
8. Baselines: deterministic taxonomy baseline (provided); plain LLM; taxonomy-assisted LLM; verified agent; full agent with abstention.
9. Metrics: fault accuracy, repair success, regression rate, coverage, runtime, model cost.
10. Milestones, risk/fallback, solo responsibilities, publication direction.

## Integrity and completion gates
- [ ] 10 verified 2025–2026 peer-reviewed papers read and critically summarized by student
- [x] proposed qualifying base paper and official ranking links identified
- [ ] base paper read and analyzed by group
- [ ] paper comparison matrix with exact results
- [ ] 3 named-paper-supported research gaps
- [ ] student-authored proposal and IEEE references
- [ ] benchmark beyond synthetic demo with provenance
- [ ] actual model integration demonstrated (currently absent)
- [x] deterministic end-to-end local baseline and unit tests
- [x] public GitHub repository published and accessible to supervisor
- [ ] final PDF formatted and named with roll number
