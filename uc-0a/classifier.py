"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import re
from typing import Dict, List, Optional, Tuple


ALLOWED_CATEGORIES: List[str] = [
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other",
]

ALLOWED_PRIORITIES: List[str] = ["Urgent", "Standard", "Low"]
SEVERITY_KEYWORDS: List[str] = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]

OUTPUT_FIELDS: List[str] = ["complaint_id", "category", "priority", "reason", "flag"]


CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flood", "flooded", "waterlogged", "water logging", "inundated"],
    "Streetlight": ["streetlight", "street light", "lights out", "lamp post", "dark at night", "flickering", "sparking"],
    "Waste": ["garbage", "waste", "trash", "rubbish", "dead animal", "overflowing bin", "dumped"],
    "Noise": ["noise", "loud", "music", "midnight", "speaker", "blaring"],
    "Road Damage": ["cracked", "sinking", "damaged road", "broken road", "road surface", "footpath tiles", "upturned"],
    "Heritage Damage": ["heritage", "monument", "historic", "old city"],
    "Heat Hazard": ["heat", "heatwave", "heat wave", "sunstroke", "extreme temperature"],
    "Drain Blockage": ["drain blocked", "blocked drain", "drain choke", "choked drain", "manhole", "sewer blocked"],
}


def _normalize_text(value: Optional[str]) -> str:
    raw = (value or "").strip().lower()
    return re.sub(r"\s+", " ", raw)


def _word_present(text: str, term: str) -> bool:
    return re.search(rf"\b{re.escape(term)}\b", text) is not None


def _severity_hits(text: str) -> List[str]:
    return [kw for kw in SEVERITY_KEYWORDS if _word_present(text, kw)]


def _extract_category_evidence(text: str) -> Dict[str, List[str]]:
    evidence: Dict[str, List[str]] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in text]
        if hits:
            evidence[category] = hits
    return evidence


def _choose_category(text: str, evidence: Dict[str, List[str]]) -> Tuple[str, bool, List[str]]:
    if not evidence:
        return "Other", True, ["insufficient explicit category evidence"]

    # Prefer explicit drain-blockage evidence over generic flooding when both appear.
    if "Drain Blockage" in evidence and "Flooding" in evidence:
        return "Drain Blockage", False, evidence["Drain Blockage"]

    sorted_candidates = sorted(
        ((cat, len(hits)) for cat, hits in evidence.items()),
        key=lambda item: item[1],
        reverse=True,
    )
    top_category, top_score = sorted_candidates[0]
    tied = [cat for cat, score in sorted_candidates if score == top_score]

    if len(tied) > 1:
        return "Other", True, [f"ambiguous between {', '.join(tied)}"]

    return top_category, False, evidence[top_category]


def _choose_priority(text: str) -> Tuple[str, List[str]]:
    hits = _severity_hits(text)
    if hits:
        return "Urgent", hits

    low_cues = ["minor", "occasional", "intermittent", "flickering"]
    if any(cue in text for cue in low_cues):
        return "Low", [cue for cue in low_cues if cue in text]

    return "Standard", []


def _build_reason(
    category: str,
    priority: str,
    category_evidence: List[str],
    priority_evidence: List[str],
) -> str:
    cat_part = (
        f"Category set to {category} based on description terms: {', '.join(category_evidence[:3])}"
        if category_evidence
        else f"Category set to {category} due to insufficient explicit category evidence"
    )

    if priority == "Urgent" and priority_evidence:
        pri_part = f"priority set to Urgent because severity keyword(s) appear: {', '.join(priority_evidence[:3])}"
    elif priority_evidence:
        pri_part = f"priority set to {priority} based on severity cue(s): {', '.join(priority_evidence[:3])}"
    else:
        pri_part = f"priority set to {priority} because no urgency keyword is present"

    # Keep exactly one sentence.
    return f"{cat_part}; {pri_part}."


def _validate_and_repair(result: dict, source_row: dict) -> Tuple[dict, bool]:
    repaired = False
    out = {
        "complaint_id": str(result.get("complaint_id") or source_row.get("complaint_id") or "UNKNOWN"),
        "category": result.get("category", "Other"),
        "priority": result.get("priority", "Standard"),
        "reason": str(result.get("reason") or "").strip(),
        "flag": result.get("flag", ""),
    }

    if out["category"] not in ALLOWED_CATEGORIES:
        out["category"] = "Other"
        out["flag"] = "NEEDS_REVIEW"
        repaired = True

    if out["priority"] not in ALLOWED_PRIORITIES:
        out["priority"] = "Standard"
        repaired = True

    text = _normalize_text(source_row.get("description"))
    if _severity_hits(text) and out["priority"] != "Urgent":
        out["priority"] = "Urgent"
        repaired = True

    if not out["reason"]:
        out["reason"] = "Description did not provide enough structured evidence, so a conservative schema-valid classification was used."
        out["flag"] = "NEEDS_REVIEW"
        repaired = True

    if out["flag"] not in ("", "NEEDS_REVIEW"):
        out["flag"] = "NEEDS_REVIEW"
        repaired = True

    if out["category"] == "Other" and out["flag"] != "NEEDS_REVIEW":
        out["flag"] = "NEEDS_REVIEW"
        repaired = True

    return out, repaired

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id") or "UNKNOWN")
    description = _normalize_text(row.get("description"))

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Description is missing or blank, so category cannot be determined from row text.",
            "flag": "NEEDS_REVIEW",
        }

    category_evidence_map = _extract_category_evidence(description)
    category, ambiguous, category_evidence = _choose_category(description, category_evidence_map)
    priority, priority_evidence = _choose_priority(description)

    reason = _build_reason(category, priority, category_evidence, priority_evidence)
    flag = "NEEDS_REVIEW" if ambiguous else ""

    result = {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }
    repaired, _ = _validate_and_repair(result, row)
    return repaired


def batch_classify_with_quality_gate(
    input_path: str,
    output_path: str,
    review_output_path: Optional[str] = None,
) -> dict:
    """
    Batch classify with a strict quality gate.
    Returns a summary dict with totals and repair/review counts.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    summary = {
        "total_rows": 0,
        "valid_rows": 0,
        "repaired_rows": 0,
        "review_rows": 0,
        "failed_rows": 0,
    }

    review_rows: List[dict] = []

    with open(input_path, "r", encoding="utf-8", newline="") as f_in:
        reader = csv.DictReader(f_in)
        required_cols = {"complaint_id", "description"}
        if not reader.fieldnames or not required_cols.issubset(set(reader.fieldnames)):
            raise ValueError("Input CSV must contain complaint_id and description columns")

        with open(output_path, "w", encoding="utf-8", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()

            for row in reader:
                summary["total_rows"] += 1
                complaint_id = str(row.get("complaint_id") or "UNKNOWN")
                try:
                    raw = classify_complaint(row)
                    repaired, was_repaired = _validate_and_repair(raw, row)

                    if repaired["flag"] == "NEEDS_REVIEW":
                        summary["review_rows"] += 1
                        review_rows.append(
                            {
                                "complaint_id": complaint_id,
                                "review_reason": repaired["reason"],
                            }
                        )

                    if was_repaired:
                        summary["repaired_rows"] += 1
                    else:
                        summary["valid_rows"] += 1

                    writer.writerow(repaired)
                except Exception as exc:
                    summary["failed_rows"] += 1
                    fallback = {
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Row processing failed ({exc.__class__.__name__}); conservative fallback applied.",
                        "flag": "NEEDS_REVIEW",
                    }
                    summary["review_rows"] += 1
                    review_rows.append(
                        {
                            "complaint_id": complaint_id,
                            "review_reason": fallback["reason"],
                        }
                    )
                    writer.writerow(fallback)

    if review_output_path:
        with open(review_output_path, "w", encoding="utf-8", newline="") as f_review:
            review_writer = csv.DictWriter(
                f_review,
                fieldnames=["complaint_id", "review_reason"],
            )
            review_writer.writeheader()
            for rr in review_rows:
                review_writer.writerow(rr)

    reconciled = (
        summary["valid_rows"] + summary["repaired_rows"] + summary["failed_rows"]
        == summary["total_rows"]
    )
    if not reconciled:
        raise RuntimeError("QC summary counts do not reconcile with total rows")

    return summary


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    batch_classify_with_quality_gate(input_path=input_path, output_path=output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    parser.add_argument(
        "--quality-gate",
        action="store_true",
        help="Enable strict quality gate and return QC summary.",
    )
    parser.add_argument(
        "--review-output",
        required=False,
        help="Optional path for writing NEEDS_REVIEW rows when quality gate is enabled.",
    )
    args = parser.parse_args()

    if args.quality_gate:
        summary = batch_classify_with_quality_gate(
            input_path=args.input,
            output_path=args.output,
            review_output_path=args.review_output,
        )
        print(f"QC summary: {summary}")
    else:
        batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")
