# FaultPilot — Phase 1 (G2-08)

Fazal Zaman Khan (22I-2362), solo project. FaultPilot studies evidence-grounded diagnosis and repair of Python AI application faults.

## Submission files

- [Phase 1 PDF](submission/Phase1_G2-08_22I-2362.pdf): literature review, three research gaps, and project proposal.
- [Editable manuscript](submission/Phase1_G2-08_22I-2362.md) and [architecture source](submission/architecture.dot).
- Public repository link for the same Classroom submission: <https://github.com/FazalZamanKhan/faultpilot-g2-08>.

The course brief says AI-generated writing is not allowed in the assessed review and proposal. The PDF in this repository is a research-backed draft; Fazal must review and rewrite the prose in his own words before submitting it under that rule. The technical results below are limited to the implemented baseline.

## Working baseline

Requires Python 3.10+ and no third-party packages. From the repository root:

```bash
python -m faultpilot.cli --case cases/shape_mismatch.json --output outputs/demo.json
python -m faultpilot.evaluation --cases cases --output outputs/smoke_evaluation.json
python -m unittest discover -s tests -v
```

The CLI reads a local case, assigns a traceback category with deterministic rules, runs a trusted five-second Python reproducer, and writes a JSON diagnosis report. Four synthetic cases reproduce their expected failures and match their labels. This is a smoke check, not a benchmark accuracy estimate. There is no live model invocation, candidate patch, or repair-quality result yet. Only run reproducer commands from trusted case files.

An optional [Ollama generate-API adapter](https://docs.ollama.com/api/generate) accepts a configured local model and returns an unverified structured diagnosis:

```bash
python -m faultpilot.provider --case cases/shape_mismatch.json --model YOUR_INSTALLED_MODEL --output outputs/model_diagnosis.json
```

Install and start Ollama and pull a model first; see the [official local setup guide](https://docs.ollama.com/quickstart). The HTTP contract is checked by a local mock-server test. No real model call or model accuracy is claimed here. The model response cannot execute commands or edit files.

## Confirmed research data

The MLDebugging source is pinned to a Git commit and SHA-256 in `faultpilot/data.py`. Download and profile it with:

```bash
python -m faultpilot.data --download --output outputs/mldebugging_profile.json
```

The verified profile contains 1,175 records, with a source-task-grouped 941/234 development/test split. Raw benchmark data is downloaded from the published source and is excluded from this repository. The profile is descriptive; the baseline has not been scored on those records. See [the paper list](research/source_shortlist.md) for the ten studies discussed in the manuscript.

## Rebuild the PDF

With Pandoc, LaTeX (`pdflatex`), and Graphviz installed:

```bash
cd submission
dot -Tpng architecture.dot -o architecture.png
pandoc Phase1_G2-08_22I-2362.md --pdf-engine=pdflatex --include-in-header=header.tex -o Phase1_G2-08_22I-2362.pdf
```
