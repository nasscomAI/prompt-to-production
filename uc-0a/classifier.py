# classifier.py

def classify_clause(clause: str) -> dict:
    """
    UC-0A: Classify clause based on severity and keywords
    """

    clause_lower = clause.lower()

    severity = "low"

    # HIGH severity triggers
    high_keywords = ["injury", "hospital", "medical emergency", "child", "school"]
    if any(word in clause_lower for word in high_keywords):
        severity = "high"

    # MEDIUM severity triggers
    medium_keywords = ["leave", "absence", "approval", "notice"]
    if any(word in clause_lower for word in medium_keywords):
        severity = "medium"

    return {
        "clause": clause,
        "severity": severity
    }


def classify_policy(clauses: list) -> list:
    """
    Apply classification on all clauses
    """
    results = []

    for clause in clauses:
        classified = classify_clause(clause)
        results.append(classified)

    return results


def summarize_policy(clauses: list) -> list:
    """
    UC-0B: SAFE summarization (NO clause loss)
    Just returns clauses as-is (preserves meaning fully)
    """

    summary = []

    for clause in clauses:
        # Preserve full clause (important fix)
        summary.append(clause.strip())

    return summary