import argparse
import csv
import re


SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_RULES = [
    ("Pothole", ["pothole"]),
    ("Flooding", ["flood", "waterlog", "rainwater"]),
    ("Streetlight", ["streetlight", "street light", "lamp post"]),
    ("Waste", ["garbage", "waste", "trash", "litter"]),
    ("Noise", ["noise", "drilling", "honking", "loud", "idling"]),
    ("Road Damage", ["road damage", "road collapsed", "crater", "caved in", "road"]),
    ("Heritage Damage", ["heritage"]),
    ("Heat Hazard", ["heat", "heatwave"]),
    ("Drain Blockage", ["drain block", "drain blocked", "drainage", "drain"]),
]


def _normalize(text: str) -> str:
    return text.lower().strip()


def _contains_keyword(text: str, keywords: list[str]) -> bool:
    lowered = _normalize(text)
    for kw in keywords:
        if kw in lowered:
            return True
    return False


def _count_keyword_matches(text: str, keywords: list[str]) -> int:
    lowered = _normalize(text)
    count = 0
    for kw in keywords:
        if kw in lowered:
            count += 1
    return count


def _classify_category(description: str) -> tuple[str, bool]:
    normalized = _normalize(description)
    matches = []
    for cat_name, keywords in CATEGORY_RULES:
        score = _count_keyword_matches(description, keywords)
        if score > 0:
            matches.append((score, cat_name))
    matches.sort(key=lambda x: -x[0])
    if not matches:
        return "Other", False
    top_score = matches[0][0]
    top_candidates = [m[1] for m in matches if m[0] == top_score]
    best = top_candidates[0]
    ambiguous = len(top_candidates) > 1
    ambiguous = ambiguous or len(matches) > 1 and matches[0][0] == matches[1][0]
    return best, ambiguous


def _get_severity_priority(description: str) -> str:
    if _contains_keyword(description, SEVERITY_KEYWORDS):
        return "Urgent"
    return "Standard"


def _build_reason(description: str, category: str, priority: str) -> str:
    normalized = _normalize(description)
    words = re.findall(r"[a-zA-Z]+", normalized)
    severity_hit = None
    for kw in SEVERITY_KEYWORDS:
        if kw in normalized:
            severity_hit = kw
            break
    if priority == "Urgent" and severity_hit:
        return f"Urgent due to mention of '{severity_hit}' in description"
    cat_hits = []
    for cat_name, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in normalized:
                cat_hits.append(kw)
    if cat_hits:
        return f"Classified as {category} based on mention of '{cat_hits[0]}' in description"
    return f"Classified as {category} based on description content"


def classify_complaint(row: dict) -> dict:
    description = (row.get("description") or "").strip()
    complaint_id = row.get("complaint_id", "").strip()
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW",
        }
    category, ambiguous = _classify_category(description)
    priority = _get_severity_priority(description)
    reason = _build_reason(description, category, priority)
    flag = "NEEDS_REVIEW" if ambiguous else ""
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows = []
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            try:
                result = classify_complaint(row)
                rows.append(result)
            except Exception as e:
                print(f"Warning: row {i} skipped ({e})")
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
