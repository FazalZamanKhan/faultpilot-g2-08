"""Build and check Fazal's completed, original Phase 2 manuscript and source ZIP."""

import re
import shutil
import subprocess
import zipfile
from pathlib import Path


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
DEST = ROOT / "submission"
STEM = "Phase2_G2-08_22I-2362"
SOURCE_FILES = ("main.tex", "tables.tex", "references.bib", "IEEEtran.cls",
                "IEEEtran.bst", "architecture.dot", "architecture.png",
                "diagnosis_macro_f1.png")


def run(*args):
    return subprocess.run(args, cwd=PAPER, check=True, capture_output=True, text=True)


def main():
    source = (PAPER / "main.tex").read_text()
    if "[Author:" in source or "[Author to" in source:
        raise SystemExit("Write the original title and all captions before finalizing.")
    abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", source, re.S)
    if not abstract:
        raise SystemExit("Missing abstract.")
    abstract_text = re.sub(r"\\[a-zA-Z]+(?:\{[^}]*\})?", " ", abstract.group(1))
    abstract_words = len(abstract_text.split())
    if not 150 <= abstract_words <= 250:
        raise SystemExit(f"Abstract has {abstract_words} words; required range is 150–250.")
    missing = [name for name in SOURCE_FILES if not (PAPER / name).exists()]
    if missing:
        raise SystemExit(f"Missing source assets: {missing}")
    for args in (("pdflatex", "-halt-on-error", "-interaction=nonstopmode", "main.tex"),
                 ("bibtex", "main"),
                 ("pdflatex", "-halt-on-error", "-interaction=nonstopmode", "main.tex"),
                 ("pdflatex", "-halt-on-error", "-interaction=nonstopmode", "main.tex")):
        try:
            run(*args)
        except subprocess.CalledProcessError as error:
            print(error.stdout[-3000:])
            print(error.stderr[-1000:])
            raise SystemExit("LaTeX build failed; correct the source and try again.") from error
    log = (PAPER / "main.log").read_text()
    if "undefined references" in log.lower() or "citation" in log.lower() and "undefined" in log.lower():
        raise SystemExit("LaTeX reports unresolved citations or references.")
    reference_count = len(re.findall(r"\\bibitem\b", (PAPER / "main.bbl").read_text()))
    if not 25 <= reference_count <= 30:
        raise SystemExit(f"Bibliography has {reference_count} cited works; required range is 25–30.")
    metadata = run("pdfinfo", "main.pdf").stdout
    match = re.search(r"^Pages:\s+(\d+)", metadata, re.M)
    pages = int(match.group(1)) if match else -1
    if not 8 <= pages <= 10:
        raise SystemExit(f"Paper has {pages} pages including references; required range is 8–10.")
    DEST.mkdir(exist_ok=True)
    pdf = DEST / f"{STEM}_Paper.pdf"
    archive = DEST / f"{STEM}_Source.zip"
    shutil.copy2(PAPER / "main.pdf", pdf)
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
        for name in SOURCE_FILES:
            output.write(PAPER / name, name)
    print(f"Created {pdf} ({pages} pages; {reference_count} cited references)")
    print(f"Created {archive}")
    print("Generate both Turnitin reports from this exact PDF before Classroom submission.")


if __name__ == "__main__":
    main()
