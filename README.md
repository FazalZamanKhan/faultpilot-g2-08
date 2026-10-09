# FaultPilot — Phase 1 workspace (G2-08)

**Status: Phase 1 technical foundation and research preparation. This is not the final academic submission.**

The course instructions prohibit AI-generated prose in the submitted literature review and proposal. The group must write those sections after reading the papers. This repository supplies a research reading shortlist, technical scaffolding, a deterministic working baseline, and a checklist. It does not claim a completed ten-paper review, an LLM provider integration, or repair functionality.

## Run the baseline

Requires Python 3.10+; no pip packages needed.

```bash
python -m faultpilot.cli --case cases/shape_mismatch.json --output outputs/demo.json
python -m faultpilot.evaluation --cases cases --output outputs/smoke_evaluation.json
python -m unittest discover -s tests -v
```

## Scope
Proposed scope: Python AI/ML fault diagnosis, taxonomy-grounded retrieval, controlled diagnosis, reproducible checks, later optional LLM integration and IDE extension. Four synthetic fixtures exercise the current pipeline. Their smoke-evaluation score is not a research result. `reproducer` commands execute local Python code, so run only trusted cases.

## GitHub
The public repository link, once published, must be added to the same Google Classroom submission as the PDF. The group head is responsible for submission.

## Submission
Course requires ONE PDF with A (literature review and gaps) then B (proposal), plus GitHub URL. File name `Phase1_G2-08_<GroupHeadRollNo>.pdf`. Include the project code, title, all member names and roll numbers on page one. The assessed prose must be written by the group.
