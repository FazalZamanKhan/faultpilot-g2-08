# Paper writing map for Fazal

This is an outline and source locator. Write the assessed manuscript, title, captions, and interpretation in your own words. Check the published articles before citing them; a bibliography entry alone does not support a claim.

| Section | Evidence to inspect and questions to answer |
| --- | --- |
| Abstract (150–250 words) | State the problem, three gap components, fixed evaluation set, E1/E2/E3 main numbers, honest direction of effects, and limits. Use only saved final results. |
| Introduction | Why Python AI code debugging is hard; fixed Phase 1 gaps and research questions; what this implementation contributes. Distinguish the original Java base paper from its Python adaptation. |
| Related Work | Synthesize the papers below by repair loops, debugging benchmarks, retrieval/grounding, test execution, and stopping/agents. Explain relationships rather than listing titles. |
| Problem Formulation | Input: buggy Python program, runtime feedback, supplied tests; output: bounded candidate edit or abstention. Define label prediction and supplied-test verification separately. |
| Proposed System | Use `architecture.png`, `faultpilot/agent.py`, `faultpilot/diagnostics.py`, and the three switches. Explain state transitions and recorded tool calls. |
| Experimental Setup | Use `docs/phase2_protocol.md`, `results/environment.json`, `results/test_manifest.json`, and the model digest. Describe grouped split, sandbox, budgets and development-only selection. |
| Evaluation Methodology | Define macro F1 and exact match for diagnosis; verified pass rate with 198 eligible and 234 total accounted for; selective accuracy/coverage; latency, tokens, tool calls; paired task-group bootstrap. Explain why original Java counts are context only. |
| Results | Use `results/diagnostic_evaluation.json`, `results/gate_evaluation.json`, `results/repair_aggregate.json`, and generated `tables.tex`. Organize by each gap and give the README gap-resolution table's conclusions. |
| Ablation and Comparative Analysis | Compare E3 with each E5 switch-off using paired cases. Include negative results and uncertainty intervals where computed. Report E6 trade-offs from saved traces. |
| Failure Analysis | Use `results/failure_analysis.json`; report frequencies on all 234 and two saved successes and two saved failures if present. State honestly if fewer than two successes occur. Cite case IDs and explain the trace steps. |
| Limitations and Threats | Supplied-test oracle only; missing packages and timeouts; small local model; single deterministic configuration; 4,096-token context and prompt truncation; no independent semantic correctness test; original Java versus Python mismatch. |
| Conclusion | Answer each research question using the actual measured outcomes, then name feasible future work. |

Plan roughly six to eight pages of body, one to two pages of references, and leave space for the architecture diagram, diagnosis figure, and generated tables. Check the final PDF itself: 8–10 pages including references, readable figures, every table and figure cited in the text, and 25–30 cited references. `python3 paper/finalize_submission.py` checks several mechanical requirements after you write.

## Bibliography leads by topic

- Base paper and agent trajectories: `ref01`, `ref02`, `ref03`, `ref07`, `ref34`.
- Debugging benchmarks and AI/data-science program faults: `ref05`, `ref08`, `ref09`, `ref10`, `ref25`.
- Classical and learned program repair: `ref11`, `ref12`, `ref13`, `ref14`, `ref15`, `ref16`, `ref18`, `ref20`, `ref22`, `ref26`, `ref28`.
- Retrieval and grounding: `ref06`, `ref17`, `ref27`.
- Test-driven repair and test generation: `ref19`, `ref24`, `ref29`, `ref30`, `ref31`.

These are 30 candidate references in `references.bib`, each with a DOI or official URL. Check each paper's actual methods and claims, then cite the 25–30 that you genuinely discuss. BibTeX lists cited entries only. There is no need to cite every candidate if a source does not serve the argument.
