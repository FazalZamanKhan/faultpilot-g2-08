# Phase 1 reading shortlist (research aid, not submission prose)

The course requires at least ten **2025–2026 peer reviewed research articles**. These ten 2025 proceedings records are a starting set for the group to read. Verify the full paper, its exact tables, and its fit to FaultPilot before including it in the submitted review. A proceedings entry confirms publication; it does not substitute for a critical reading.

| # | Candidate paper and primary publication record | Why it is relevant | Group reading status |
|---|---|---|---|
| 1 ★ | [RepairAgent: An Autonomous, LLM-Based Agent for Program Repair — ICSE 2025 Research Track](https://conf.researchr.org/details/icse-2025/icse-2025-research-track/160/RepairAgent-An-Autonomous-LLM-Based-Agent-for-Program-Repair) | Autonomous tool use and patch validation; proposed base comparison | Not yet read and summarized by group |
| 2 | [UniDebugger: Hierarchical Multi-Agent Framework for Unified Software Debugging — EMNLP 2025](https://aclanthology.org/2025.emnlp-main.921/) | Agent roles across debugging stages | Not yet read and summarized by group |
| 3 | [COAST: Enhancing the Code Debugging Ability of LLMs through Communicative Agent Based Data Synthesis — Findings of NAACL 2025](https://aclanthology.org/2025.findings-naacl.139/) | Multi-stage debugging evaluation and data synthesis | Not yet read and summarized by group |
| 4 | [SynFix: Dependency-Aware Program Repair via RelationGraph Analysis — Findings of ACL 2025](https://aclanthology.org/2025.findings-acl.252/) | Structured context and patch validation | Not yet read and summarized by group |
| 5 | [MLDebugging: Towards Benchmarking Code Debugging Across Multi-Library Scenarios — Findings of ACL 2025](https://aclanthology.org/2025.findings-acl.305/) | Python multi-library debugging benchmark | Not yet read and summarized by group |
| 6 | [Hierarchical Knowledge Injection for Improving LLM-based Program Repair — ASE 2025 Research Papers](https://conf.researchr.org/details/ase-2025/ase-2025-papers/56/Hierarchical-Knowledge-Injection-for-Improving-LLM-based-Program-Repair) | Repository context and BugsInPy evaluation | Not yet read and summarized by group |
| 7 | [Understanding Software Engineering Agents: A Study of Thought-Action-Result Trajectories — ASE 2025 Research Papers](https://conf.researchr.org/details/ase-2025/ase-2025-papers/40/Understanding-Software-Engineering-Agents-A-Study-of-Thought-Action-Result-Trajector) | Agent failure modes, tool use, and feedback | Not yet read and summarized by group |
| 8 | [Fixing Broken Graphs: LLM-Powered Automatic Code Optimization for DNN Programs — ASE 2025 Research Papers](https://conf.researchr.org/details/ase-2025/ase-2025-papers/183/Fixing-Broken-Graphs-LLM-Powered-Automatic-Code-Optimization-for-DNN-Programs) | Multi-agent work on DNN Python programs | Not yet read and summarized by group |
| 9 | [RepoDebug: Repository-Level Multi-Task and Multi-Language Debugging Evaluation of Large Language Models — Findings of EMNLP 2025](https://aclanthology.org/2025.findings-emnlp.1294/) | Repository-level benchmark beyond toy snippets | Not yet read and summarized by group |
| 10 | [Template-Guided Program Repair in the Era of Large Language Models — ICSE 2025 Research Track](https://conf.researchr.org/details/icse-2025/icse-2025-research-track/11/Template-Guided-Program-Repair-in-the-Era-of-Large-Language-Models) | A simpler structured-repair comparison | Not yet read and summarized by group |

★ Proposed base paper: *RepairAgent*. Its publication record identifies the ICSE 2025 **Research Track**. The [official CORE/ICORE ranking portal](https://portal.core.edu.au/conf-ranks/?by=all&page=1&search=&sort=arank&source=CORE2023) lists **International Conference on Software Engineering (ICSE)** as **A\*** in CORE 2023. The group should cite both records in the submitted base-paper discussion. Its Defects4J Java setting differs from FaultPilot's proposed Python AI/ML setting, so direct numerical comparison would be invalid without a shared evaluation set or reproduced method.

## Extraction sheet for each paper

Record the exact paper page or table for every claim. Write the assessed analysis yourself.

1. Full IEEE citation, DOI, publication URL, and evidence of peer review.
2. Research question and system/method architecture.
3. Dataset, language, number of cases, split, and reproducibility details.
4. Exact metric definitions, baselines, and numerical results with table/page numbers.
5. Limitations stated by the authors; then separately record your own concerns.
6. Specific link to one of FaultPilot's three proposed gaps.

Do not treat a benchmark paper's reported model failures as evidence that FaultPilot fixes them. The group must test that claim on a confirmed, provenance-tracked dataset.
