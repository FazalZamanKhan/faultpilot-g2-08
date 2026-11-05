"""Trainable diagnosis and switchable retrieval over development cases."""

import re
from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier

from .benchmark import BenchmarkCase
from .core import diagnose as phase1_diagnose
from .data import CATEGORIES

PHASE1_CATEGORY_MAP = {
    "shape_mismatch": "Type Mismatch",
    "device_mismatch": "Data Transfer Issues",
    "missing_dependency": "Import Errors",
}


def phase1_labels(case: BenchmarkCase) -> tuple[str, ...]:
    result = phase1_diagnose({"case_id": case.case_id, "traceback": case.runtime_feedback})
    mapped = PHASE1_CATEGORY_MAP.get(result["category"])
    return (mapped,) if mapped else ()


def case_text(case: BenchmarkCase) -> str:
    return case.runtime_feedback[:3500] + "\n" + case.bug_code[:7000]


def local_evidence(case: BenchmarkCase, limit: int = 3) -> list[dict]:
    """Choose code lines sharing nontrivial words with runtime feedback."""
    feedback_words = set(re.findall(r"[A-Za-z_][A-Za-z_0-9]{3,}", case.runtime_feedback.lower()))
    ignored = {"test", "case", "line", "file", "traceback", "most", "recent", "call", "last", "error", "assertion"}
    feedback_words -= ignored
    scored = []
    for number, line in enumerate(case.bug_code.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        words = set(re.findall(r"[A-Za-z_][A-Za-z_0-9]{3,}", line.lower()))
        scored.append((len(words & feedback_words), number, line.strip()[:220]))
    scored.sort(key=lambda row: (-row[0], row[1]))
    return [{"line": number, "text": text, "overlap": score}
            for score, number, text in scored[:limit] if score > 0]


@dataclass(frozen=True)
class Diagnosis:
    labels: tuple[str, ...]
    confidence: float
    probabilities: dict[str, float]
    evidence: list[dict]
    retrieved: list[dict]


class DiagnosticModel:
    def __init__(self, training_cases: list[BenchmarkCase]):
        if not training_cases:
            raise ValueError("No training cases")
        self.cases = training_cases
        self.vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(3, 5), min_df=2, max_features=40000)
        self.matrix = self.vectorizer.fit_transform(case_text(case) for case in training_cases)
        labels = np.array([[int(category in case.labels) for category in CATEGORIES]
                           for case in training_cases])
        self.classifier = OneVsRestClassifier(LogisticRegression(
            class_weight="balanced", max_iter=500, random_state=17))
        self.classifier.fit(self.matrix, labels)

    def diagnose(self, case: BenchmarkCase, *, retrieval: bool, alpha: float = 0.25,
                 threshold: float = 0.35, neighbors: int = 3) -> Diagnosis:
        vector = self.vectorizer.transform([case_text(case)])
        base = self.classifier.predict_proba(vector)[0]
        retrieved = []
        if retrieval:
            similarities = (self.matrix @ vector.T).toarray().ravel()
            eligible = [index for index, prior in enumerate(self.cases)
                        if prior.task_id != case.task_id]
            top = sorted(eligible, key=lambda index: (-similarities[index], self.cases[index].case_id))[:neighbors]
            if top:
                weights = np.array([max(similarities[index], 0.0) for index in top])
                if weights.sum() > 0:
                    neighbor_scores = np.zeros(len(CATEGORIES))
                    for weight, index in zip(weights / weights.sum(), top):
                        for label in self.cases[index].labels:
                            neighbor_scores[CATEGORIES.index(label)] += weight
                    base = (1.0 - alpha) * base + alpha * neighbor_scores
                retrieved = [{"case_id": self.cases[index].case_id,
                              "task_id": self.cases[index].task_id,
                              "similarity": round(float(similarities[index]), 4),
                              "labels": self.cases[index].labels}
                             for index in top]
        selected = tuple(CATEGORIES[index] for index, score in enumerate(base) if score >= threshold)
        if not selected:
            selected = (CATEGORIES[int(np.argmax(base))],)
        return Diagnosis(
            labels=selected,
            confidence=round(float(max(base)), 4),
            probabilities={label: round(float(score), 4) for label, score in zip(CATEGORIES, base)},
            evidence=local_evidence(case),
            retrieved=retrieved,
        )
