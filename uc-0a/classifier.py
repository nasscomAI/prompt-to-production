"""
UC-0A — Complaint Classifier

Deterministic rule-based classifier built from agents.md / skills.md.
Reads one complaint row at a time and outputs category, priority, reason, flag.
"""
import argparse
import csv
import re

CATEGORIES = [
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

SEVERITY_STEMS = [
    "injur", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collaps",
]

LOW_MARKERS = ["cosmetic", "non-urgent", "minor", "superficial"]

CATEGORY_PATTERNS = {
    "Pothole": ["pothole", "crater"],
    "Flooding": ["flood", "water", "waterlog", "submerg", "inundat", "rainwater", "draining", "drainage"],
    "Streetlight": ["streetlight", "street light", "lights out", "lamp", "unlit", "flicker", "spark", "wiring", "substation"],
    "Waste": ["garbage", "waste", "trash", "refuse", "overflow", "bins", "dead animal", "carcass", "dumped", "dumping", "litter", "sewage"],
    "Noise": ["noise", "noisy", "music", "loud", "amplifier", "drilling", "idling", "engines", "band", "honk"],
    "Road Damage": ["road surface", "paving", "pavement", "footpath", "manhole", "asphalt", "tarmac", "cobblestone", "buckled", "subsidence", "subsided", "sinking", "cracked", "collaps", "crater"],
    "Heritage Damage": ["heritage", "historic"],
    "Heat Hazard": ["heat", "heatwave", "temperature", "celsius", "melting", "bubbling", "sun", "°c"],
    "Drain Blockage": [],
    "Other": [],
}

SENTENCE_SPLIT = re.compile(r"[.!?]")

WATER_FAMILY = ("water", "rainwater", "draining", "drainage")
HERITAGE_CONTEXT = [
    "street", "road", "lamp", "lights", "cobblestone", "stone", "building", "paving",
    "monument", "structure", "facade", "wall", "tram", "light", "pavement",
    "gate", "house",
]
HERITAGE_WORDS = ("heritage", "historic")


def _split_sentences(text: str) -> list:
    return [s.strip() for s in SENTENCE_SPLIT.split(text) if s.strip()]


def _heritage_context_near(sent: str) -> bool:
    tokens = re.findall(r"[A-Za-z']+", sent)
    for i, token in enumerate(tokens):
        if token not in HERITAGE_WORDS:
            continue
        window = tokens[max(0, i - 3): i + 4]
        if any(w in HERITAGE_CONTEXT for w in window):
            return True
    return False


def _match_in(cat: str, patterns: list, sentences: list, orig_sentences: list, low: str):
    if cat == "Flooding" and "pothole" in low:
        patterns = [p for p in patterns if p not in WATER_FAMILY]
    score = 0
    first = None
    matched = None
    for i, (sent, orig) in enumerate(zip(sentences, orig_sentences)):
        weight = 2 if i == 0 else 1
        if cat == "Heritage Damage" and not _heritage_context_near(sent):
            continue
        for p in patterns:
            if p in sent:
                score += weight
                if first is None:
                    first = i
                    m = re.search(re.escape(p), orig, re.IGNORECASE)
                    matched = m.group(0) if m else p
    return score, first, matched


def _drain_blockage(sentences: list, orig_sentences: list):
    low = " ".join(sentences)
    if not re.search(r"\bdrain\b", low):
        return 0, None, None
    if not re.search(r"\b(blocked|blockage|clogged|clog)\b", low):
        return 0, None, None
    score = 0
    first = None
    matched = "drain"
    for i, (sent, orig) in enumerate(zip(sentences, orig_sentences)):
        weight = 2 if i == 0 else 1
        for word in ["drain", "blocked", "blockage", "clogged", "clog"]:
            if re.search(r"\b" + word + r"\b", sent):
                score += weight
                if first is None:
                    first = i
                    m = re.search(r"\bdrain\b", orig, re.IGNORECASE)
                    matched = m.group(0) if m else "drain"
    return score, first, matched


def _priority(description: str) -> str:
    low = description.lower()
    if any(stem in low for stem in SEVERITY_STEMS):
        return "Urgent"
    if any(marker in low for marker in LOW_MARKERS):
        return "Low"
    return "Standard"


def _reason(description: str, category: str, flag: str, matched: str, tied=None) -> str:
    if not matched:
        snippet = (description.strip().split(". ")[0][:80] if description.strip() else "no description")
        matched = snippet or "no description"
    if flag == "NEEDS_REVIEW":
        if tied:
            return f'The description says "{matched}" which is ambiguous between {tied[0]} and {tied[1]}, so it needs review.'
        return f'The description says "{matched}" which does not clearly match any category, so it needs review.'
    return f'The description says "{matched}" which indicates {category}.'


def classify_complaint(row: dict) -> dict:
    description = row.get("description") or ""
    complaint_id = row.get("complaint_id", "")
    low_sentences = _split_sentences(description.lower())
    orig_sentences = _split_sentences(description)

    if not low_sentences:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The complaint has no description, so it needs review.",
            "flag": "NEEDS_REVIEW",
        }

    scores = {}
    firsts = {}
    matcheds = {}
    low = description.lower()
    for cat in CATEGORIES:
        patterns = CATEGORY_PATTERNS[cat]
        score, first, matched = _match_in(cat, patterns, low_sentences, orig_sentences, low)
        if cat == "Drain Blockage":
            dscore, dfirst, dmatched = _drain_blockage(low_sentences, orig_sentences)
            if dscore > score:
                score, first, matched = dscore, dfirst, dmatched
        scores[cat] = score
        firsts[cat] = first
        matcheds[cat] = matched

    max_score = max(scores.values())
    flag = ""
    category = None
    tied = None

    if max_score == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        candidates = [cat for cat in CATEGORIES if scores[cat] == max_score]
        if len(candidates) == 1:
            category = candidates[0]
        else:
            earliest = min(firsts[cat] for cat in candidates)
            earliest_cats = [cat for cat in candidates if firsts[cat] == earliest]
            if len(earliest_cats) == 1:
                category = earliest_cats[0]
            else:
                category = "Other"
                flag = "NEEDS_REVIEW"
                tied = [earliest_cats[0], earliest_cats[1]]

    matched = matcheds[category] if category else None
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": _priority(description),
        "reason": _reason(description, category, flag, matched, tied),
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        for row in rows:
            try:
                result = classify_complaint(row)
            except Exception as exc:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification failed: {exc}",
                    "flag": "NEEDS_REVIEW",
                }
            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
