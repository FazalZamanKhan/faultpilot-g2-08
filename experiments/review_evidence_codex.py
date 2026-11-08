"""Record a transparent AI-assisted review of the fixed evidence sample.

These judgments are a preliminary, item-by-item inspection of extracted spans
against buggy source, supplied tests, and runtime feedback. They do not stand in
for an independent human relevance assessment.
"""

import csv
import json
from pathlib import Path


SOURCE = Path("results/evidence_audit_50.csv")
DEST = Path("results/evidence_audit_50_codex_review.csv")

# A span is marked yes only if a highlighted line plausibly needs changing to
# address a recorded failure. Imports, signatures, and exception propagation
# alone do not qualify. The fixed sample and source rows remain unchanged.
REVIEW = {
    "MLDebug1051": ("no", "Import line does not locate the missing fixed random seed."),
    "MLDebug936": ("yes", "Line 44 calls misspelled b664encode, matching the NameError."),
    "MLDebug306": ("yes", "Line 12 calls nonexistent str.concat, matching the AttributeError."),
    "MLDebug568": ("yes", "Line 11 passes the unsupported fontname plotting argument."),
    "MLDebug922": ("yes", "Highlighted hash and print lines are directly involved in failed mock assertions."),
    "MLDebug479": ("no", "Fault is the tab replacement on line 5; highlighted return is downstream."),
    "MLDebug10": ("no", "Fault is the unencoded HMAC message on line 10, which is not highlighted."),
    "MLDebug1143": ("no", "Highlighted decomposition call propagates the short-series and negative-value errors; the input generation and handling need review."),
    "MLDebug746": ("yes", "The highlighted distplot call controls the absent plotted data collection."),
    "MLDebug1027": ("yes", "Highlighted transform line returns a 2D shape where tests expect 1D."),
    "MLDebug467": ("yes", "Highlighted pairplot passes hue='category' although the data has no such column."),
    "MLDebug810": ("yes", "Highlighted fixed-city loop and membership check cause the wrong output keys."),
    "MLDebug618": ("yes", "Highlighted to_numeric call rejects salary strings containing commas."),
    "MLDebug620": ("yes", "Highlighted groupby count loses the per-item matrix required by the chart test."),
    "MLDebug1066": ("no", "Highlighted signature, path join, and return do not locate the missing input validation and empty-metrics behavior."),
    "MLDebug871": ("yes", "Highlighted histogram call attempts to bin datetime values as numeric values."),
    "MLDebug27": ("yes", "Highlighted line 9 removes a hex digit before conversion, causing ValueError."),
    "MLDebug52": ("yes", "Highlighted reshape creates the (5,1) output shape rejected by tests."),
    "MLDebug198": ("no", "Highlighted import, guard, and return miss the incorrect x range on line 9."),
    "MLDebug777": ("yes", "Highlighted return adds num again after insertion, causing the list-length failure."),
    "MLDebug879": ("no", "Highlighted exception wrapper reports missing xlsxwriter; ExcelWriter engine selection is on line 15."),
    "MLDebug667": ("yes", "Highlighted results assignment preserves IPv4Address keys instead of required strings."),
    "MLDebug1029": ("no", "Highlighted raise is reached because the unhighlighted numeric predicate on line 20 is wrong."),
    "MLDebug830": ("no", "Highlighted function signature misses the absent numpy import and np use on line 14."),
    "MLDebug203": ("no", "Highlighted import and signature miss the unencoded HMAC key on line 14."),
    "MLDebug1163": ("yes", "Highlighted Countries indexing line directly raises KeyError for the test data."),
    "MLDebug164": ("no", "Highlighted output directory is unrelated to the wrong hash values."),
    "MLDebug1134": ("no", "Highlighted exception is caused by the unhighlighted isalpha guard on line 5 for empty strings."),
    "MLDebug383": ("yes", "Highlighted filter references nonexistent column, matching KeyError."),
    "MLDebug352": ("no", "Highlighted API URL and return miss the CSV row-writing error on line 17."),
    "MLDebug272": ("no", "Highlighted Counter is correct; cleaning on line 6 leaves spaces."),
    "MLDebug952": ("no", "Highlighted DataFrame construction receives NaNs created by unhighlighted zscore call."),
    "MLDebug1120": ("yes", "Highlighted empty-data return has the wrong DataFrame shape for one supplied test."),
    "MLDebug829": ("no", "Highlighted validation and import miss the one-cluster segmentation behavior."),
    "MLDebug842": ("no", "Highlighted function signature misses incompatible dot-product shapes on line 13."),
    "MLDebug424": ("no", "Highlighted generation and transform miss feature_range=(-1,1) on line 9."),
    "MLDebug292": ("yes", "Highlighted randint call has reversed endpoints, matching the empty-range error."),
    "MLDebug154": ("no", "Highlighted Counter is correct; the random source on line 7 changes expected frequencies."),
    "MLDebug654": ("no", "Highlighted input guards miss undefined random_seed on line 11."),
}


def main():
    with SOURCE.open(newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        rows = list(reader)
    blank = {row["case_id"] for row in rows if not row["relevant_yes_no"]}
    if len(rows) != 50 or blank != set(REVIEW):
        raise ValueError("Review map no longer matches the 39 unjudged fixed-sample cases")
    for row in rows:
        if row["case_id"] in REVIEW:
            row["relevant_yes_no"], row["reviewer_notes"] = REVIEW[row["case_id"]]
        if row["relevant_yes_no"] == "yes" and not json.loads(row["evidence"]):
            raise ValueError(f"Absent evidence marked relevant: {row['case_id']}")
    with DEST.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {DEST}: {sum(row['relevant_yes_no'] == 'yes' for row in rows)}/50 relevant")


if __name__ == "__main__":
    main()
