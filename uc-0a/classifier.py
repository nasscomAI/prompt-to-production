#!/usr/bin/env python3
"""UC-0A Complaint Classifier

Deterministic rule-based classifier. Usage:
  python uc-0a/classifier.py --input ../data/city-test-files/test_pune.csv --output uc-0a/results_pune.csv
Or run internal tests:
  python uc-0a/classifier.py --test
"""
from __future__ import annotations
import argparse
import csv
import os
import re
import sys
from typing import Dict, List, Tuple


ALLOWED_CATEGORIES = [
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

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS = [
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

# Conservative category keyword patterns (lowercase). Use word boundaries where sensible.
CATEGORY_PATTERNS = {
    "Pothole": [r"\bpothole\b", r"\btyre\b", r"\btire\b", r"\bhole\b"],
    "Flooding": [r"\bflood\b", r"flooded", r"knee-deep", r"inaccessible", r"waterlogged"],
    "Streetlight": [r"streetlight", r"lights out", r"flicker", r"sparking", r"street light"],
    "Waste": [r"garbage", r"bin", r"dumped", r"rubbish", r"dead animal", r"overflowing"],
    "Noise": [r"music", r"noise", r"loud", r"loud music"],
    "Road Damage": [r"crack", r"cracked", r"sinking", r"footpath", r"tiles broken", r"manhole cover missing", r"manhole"],
    "Heritage Damage": [r"heritage"],
    "Heat Hazard": [r"heatwave", r"heat hazard", r"extreme heat", r"hot weather"],
    "Drain Blockage": [r"drain", r"drain blocked", r"blocked drain", r"drainage blocked", r"clogged drain"],
}

# Precompile regexes
COMPILED_CATEGORY_REGEX: Dict[str, List[re.Pattern]] = {
    cat: [re.compile(p, re.IGNORECASE) for p in pats]
    for cat, pats in CATEGORY_PATTERNS.items()
}

COMPILED_SEVERITY_REGEX = [re.compile(r"\b" + re.escape(k) + r"\b", re.IGNORECASE) for k in SEVERITY_KEYWORDS]


def normalize(s: str) -> str:
    return (s or "").strip()


def find_category_matches(description: str) -> List[str]:
    desc = description or ""
    matches = []
    for cat, patterns in COMPILED_CATEGORY_REGEX.items():
        for p in patterns:
            if p.search(desc):
                matches.append(cat)
                break
    return matches


def find_severity_matches(description: str) -> List[str]:
    desc = description or ""
    found = []
    for i, r in enumerate(COMPILED_SEVERITY_REGEX):
        if r.search(desc):
            found.append(SEVERITY_KEYWORDS[i])
    return found


def build_reason(description: str, matched_tokens: List[str], category: str, priority: str, flag: str) -> str:
    # Reason must be exactly one sentence ending with a period and cite words from description.
    if description is None:
        description = ""
    # Use up to three matched tokens from the description; preserve their original casing by searching the description.
    tokens = []
    for t in matched_tokens:
        m = re.search(re.escape(t), description, re.IGNORECASE)
        if m:
            token = m.group(0)
            if token not in tokens:
                tokens.append(token)
        if len(tokens) >= 3:
            break

    if tokens:
        evidence = ", ".join([f"'{t}'" for t in tokens])
    else:
        # fallback: short excerpt
        words = description.split()
        excerpt = " ".join(words[:8]) if words else ""
        evidence = f"'{excerpt}'" if excerpt else "'description missing'"

    if flag == "NEEDS_REVIEW":
        reason = f"Contains {evidence}; matches multiple categories, requires review."
    elif category == "Other":
        reason = f"Contains {evidence}; no category-specific keyword matched, classified as Other."
    else:
        reason = f"Contains {evidence}; classified as {category} with {priority} priority."

    # Ensure single sentence ending with period.
    reason = reason.strip()
    if not reason.endswith("."):
        reason += "."
    return reason


def classify_row(row: Dict[str, str]) -> Dict[str, str]:
    desc = normalize(row.get("description", ""))

    severity = find_severity_matches(desc)
    cat_matches = find_category_matches(desc)

    if len(cat_matches) == 1:
        category = cat_matches[0]
        flag = ""
    elif len(cat_matches) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = ""

    # Priority rules
    if severity:
        priority = "Urgent"
    elif category == "Noise":
        priority = "Low"
    else:
        priority = "Standard"

    # Build reason using matched tokens (severity + category keywords found in text)
    matched_tokens: List[str] = []
    # include severity tokens first
    for s in severity:
        if s not in matched_tokens:
            matched_tokens.append(s)
    # then include any literal matched category keywords by scanning patterns
    for cat in cat_matches:
        for p in CATEGORY_PATTERNS.get(cat, []):
            m = re.search(p, desc, re.IGNORECASE)
            if m:
                token = m.group(0)
                if token not in matched_tokens:
                    matched_tokens.append(token)
                break

    reason = build_reason(description=desc, matched_tokens=matched_tokens, category=category, priority=priority, flag=flag)

    # Compose output row preserving original fields
    out = dict(row)
    out["category"] = category
    out["priority"] = priority
    out["reason"] = reason
    out["flag"] = flag

    # Validation
    if out["category"] not in ALLOWED_CATEGORIES:
        raise ValueError(f"Invalid category: {out['category']}")
    if out["priority"] not in ALLOWED_PRIORITIES:
        raise ValueError(f"Invalid priority: {out['priority']}")
    if out["flag"] not in {"", "NEEDS_REVIEW"}:
        raise ValueError(f"Invalid flag: {out['flag']}")
    # Reason must be one sentence
    if not out["reason"] or not out["reason"].endswith('.'):
        raise ValueError("Reason must be a non-empty single sentence ending with a period")

    return out


def read_csv(path: str) -> Tuple[List[Dict[str, str]], List[str]]:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    return rows, fieldnames


def write_csv(path: str, fieldnames: List[str], rows: List[Dict[str, str]]):
    # ensure output dir exists
    outdir = os.path.dirname(os.path.abspath(path))
    if outdir and not os.path.isdir(outdir):
        os.makedirs(outdir, exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def batch_classify(input_path: str, output_path: str) -> int:
    rows, fieldnames = read_csv(input_path)
    results = []
    for r in rows:
        res = classify_row(r)
        results.append(res)

    # preserve original columns and append required columns
    out_fields = list(fieldnames)
    for col in ["category", "priority", "reason", "flag"]:
        if col not in out_fields:
            out_fields.append(col)

    if len(results) != len(rows):
        raise RuntimeError("Row count mismatch after classification")

    write_csv(output_path, out_fields, results)
    return len(results)


def run_internal_tests():
    # 1
    r = {"complaint_id": "T1", "description": "A child fell near the school entrance."}
    out = classify_row(r)
    assert out["priority"] == "Urgent"

    # 2
    r = {"complaint_id": "T2", "description": "There is a pothole near the blocked drain."}
    out = classify_row(r)
    assert out["category"] == "Other" and out["flag"] == "NEEDS_REVIEW"

    # 3
    r = {"complaint_id": "T3", "description": "The streetlight is flickering every night."}
    out = classify_row(r)
    assert out["category"] == "Streetlight"

    # 4
    r = {"complaint_id": "T4", "description": "Loud music is causing noise pollution."}
    out = classify_row(r)
    assert out["category"] == "Noise" and out["priority"] == "Low"

    # 5
    r = {"complaint_id": "T5", "description": "There is some civic issue."}
    out = classify_row(r)
    assert out["category"] == "Other" and out["flag"] == ""

    print("UC-0A internal tests passed")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=False)
    p.add_argument("--output", required=False)
    p.add_argument("--test", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()
    if args.test:
        run_internal_tests()
        return
    if not args.input or not args.output:
        print("ERROR: --input and --output are required for batch mode", file=sys.stderr)
        sys.exit(2)
    count = batch_classify(args.input, args.output)
    print(f"Processed {count} rows. Output: {args.output}")


if __name__ == '__main__':
    main()
