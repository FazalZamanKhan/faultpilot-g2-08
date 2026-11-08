"""Render a factual, non-submission brief from the frozen Phase 2 result files."""

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate, Frame, KeepTogether, PageTemplate, Paragraph, Spacer, Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUTPUT = ROOT / "output" / "pdf" / "Phase2_G2-08_22I-2362_ResultsEvidence.pdf"


def read(name):
    return json.loads((RESULTS / name).read_text())


def page(canvas, doc):
    canvas.saveState()
    width, height = doc.pagesize
    canvas.setFillColor(colors.HexColor("#15324f"))
    canvas.rect(0, height - 0.13 * inch, width, 0.13 * inch, fill=1, stroke=0)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#586575"))
    canvas.drawString(0.68 * inch, 0.42 * inch, "FaultPilot | G2-08 | Frozen Phase 2 evidence")
    canvas.drawRightString(width - 0.68 * inch, 0.42 * inch, str(doc.page))
    canvas.restoreState()


def make_table(rows, widths, *, header=True):
    table = Table(rows, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, colors.HexColor("#dce3ea")),
    ]
    if header:
        commands += [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#15324f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f7fa")]),
        ]
    table.setStyle(TableStyle(commands))
    return table


def main():
    diagnosis = read("diagnostic_evaluation.json")
    aggregate = read("repair_aggregate.json")
    failures = read("failure_analysis.json")
    gate = read("gate_evaluation.json")
    validation = read("repair_validation.json")
    if validation["status"] != "passed" or validation["test_cases"] != 234:
        raise ValueError("Frozen result validation did not pass")
    if aggregate["preflight"]["repair_eligible"] != 198:
        raise ValueError("Unexpected repair denominator")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleFP", parent=styles["Title"], fontName="Helvetica-Bold",
                              fontSize=18, leading=22, textColor=colors.HexColor("#15324f"),
                              spaceAfter=5))
    styles.add(ParagraphStyle(name="SubFP", parent=styles["Normal"], fontSize=9, leading=13,
                              textColor=colors.HexColor("#586575"), spaceAfter=13))
    styles.add(ParagraphStyle(name="HFP", parent=styles["Heading2"], fontSize=11, leading=14,
                              textColor=colors.HexColor("#15324f"), spaceBefore=13,
                              spaceAfter=5))
    styles.add(ParagraphStyle(name="BodyFP", parent=styles["Normal"], fontSize=9, leading=13,
                              spaceAfter=5))
    styles.add(ParagraphStyle(name="SmallFP", parent=styles["Normal"], fontSize=7.5, leading=10,
                              spaceAfter=5))
    styles.add(ParagraphStyle(name="TableFP", parent=styles["Normal"], fontSize=8, leading=10))
    styles.add(ParagraphStyle(name="TableHeadFP", parent=styles["TableFP"], fontName="Helvetica-Bold",
                              textColor=colors.white))
    p = lambda text, style="BodyFP": Paragraph(text, styles[style])
    cell = lambda text, head=False: p(text, "TableHeadFP" if head else "TableFP")

    doc = BaseDocTemplate(str(OUTPUT), pagesize=(8.27 * inch, 11.69 * inch),
                          leftMargin=0.68 * inch, rightMargin=0.68 * inch,
                          topMargin=0.50 * inch, bottomMargin=0.56 * inch,
                          title="FaultPilot Phase 2: measured results and limits",
                          author="FaultPilot project evidence")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates(PageTemplate(id="report", frames=[frame], onPage=page))

    story = [
        p("FaultPilot: measured results and limits", "TitleFP"),
        p("Fazal Zaman Khan | 22I-2362 | Solo project G2-08 | 8 November 2026", "SubFP"),
        p("This brief transcribes the frozen repository results for paper preparation. It is not the required 8-10 page research paper and is not a Turnitin report.", "BodyFP"),
        p("Evaluation set", "HFP"),
        p("MLDebugging has 1,175 records. The source-task-grouped split contains 941 development records and 234 held-out test records. Original-code preflight found 198 reproducible failures, 30 setup errors, five timeouts, and one already passing case. Repair rates below use the fixed 198-case eligible denominator; all 234 records have traces.", "BodyFP"),
        p("Diagnosis", "HFP"),
    ]
    dmetrics = diagnosis["metrics"]
    drows = [[cell("Method", True), cell("Macro F1", True), cell("Exact match", True)]]
    for label, key in [
        ("Phase 1 rules", "E1_phase1_rule_baseline"),
        ("Learned classifier", "trained_diagnosis_no_retrieval"),
        ("Full evidence + retrieval", "full_evidence_retrieval"),
        ("Retrieval score fusion (alpha 0.2)", "retrieval_score_fusion_alpha_0_2_ablation"),
    ]:
        item = dmetrics[key]
        drows.append([cell(label), cell(f"{item['macro_f1']:.5f}"), cell(f"{item['exact_match']:.5f}")])
    story += [make_table(drows, [3.25 * inch, 1.2 * inch, 1.35 * inch]),
              Spacer(1, 4),
              p("The learned classifier improved macro F1 by 0.26973 over Phase 1 rules (task-group bootstrap 95% interval 0.18266 to 0.35415). Retrieval examples were available for all 234 cases and local code-line evidence for 194, but availability does not establish fault localization accuracy.", "BodyFP"),
              p("Repair experiment", "HFP")]
    runs = aggregate["runs"]
    rrows = [[cell("Mode", True), cell("Passes / 198", True), cell("Mean loop time", True), cell("Key outcome", True)]]
    for label, key, note in [
        ("E2 Python base-paper adaptation", "E2_repairagent_style", "0 verified"),
        ("E3 full FaultPilot", "E3_full", "33 evidence abstentions"),
        ("E5 no retrieval", "E5_no_retrieval", "One supplied-test pass"),
        ("E5 no verification", "E5_no_verification", "123 proposals; 0 audit passes"),
        ("E5 no evidence gate", "E5_no_gate", "0 verified"),
    ]:
        item = runs[key]
        rrows.append([cell(label), cell(f"{item['verified_passes']} / 198"),
                      cell(f"{item['mean_agent_wall_s_excluding_offline_audit']:.3f} s"), cell(note)])
    story += [make_table(rrows, [2.02 * inch, 0.86 * inch, 1.13 * inch, 1.79 * inch]),
              Spacer(1, 4),
              p("E2 is an adaptation of RepairAgent's inspect-edit-test loop to the same Python cases as E3. The original RepairAgent paper's reported 164 correct Java/Defects4J fixes are contextual and cannot be compared directly with these Python pass rates.", "BodyFP"),
              p("Ablation and failure accounting", "HFP"),
              p("Removing retrieval produced one supplied-test pass where E3 produced none. The paired pass-rate difference E3 minus no retrieval was -0.00505 (task-group bootstrap 95% interval -0.01596 to 0). Removing verification produced 123 proposals, none of which passed the separate offline test audit. The full system had 70 candidate load failures, 54 loaded candidates that failed tests, 40 rejected-edit cases, and 33 evidence abstentions. There were no successful E3 repairs to use as success examples.", "BodyFP"),
              p("Interpretation and limits", "HFP"),
              p("The diagnosis component improved category prediction; the repair loop did not fix a reproduced failure under the frozen budget and local 0.5B model. The evidence gate's conditional exact-match gain was only 0.00128, below the Phase 1 target of +0.10. A supplied-test pass does not prove semantic correctness. The benchmark supplies no independent regression suite; missing packages and timeouts restrict executable coverage. Mean loop times omit precomputed diagnosis and preflight and represent between-case, single-run measurements.", "BodyFP"),
              p("Repository evidence", "HFP"),
              p("Public repository: github.com/FazalZamanKhan/faultpilot-g2-08<br/>Frozen release: github.com/FazalZamanKhan/faultpilot-g2-08/releases/tag/phase2-final", "SmallFP"),
    ]
    if failures["representative_successes"]:
        raise ValueError("Frozen failure analysis unexpectedly contains successful E3 repairs")
    if gate.get("test_count") not in (None, 234):
        raise ValueError("Gate evaluation count changed")
    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    main()
