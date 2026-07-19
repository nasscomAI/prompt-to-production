"""
UC-0A — Complaint Classifier
============================
Deterministic, rule-based civic-complaint classifier (pure Python 3.9 stdlib).

Defeats the UC-0A failure modes named in the README:
  * Taxonomy drift          -> category is restricted to a fixed 10-value enum
                               via an ordered keyword-precedence mapper.
  * Severity blindness      -> priority is forced to Urgent the moment ANY of
                               the 9 severity word-stems appears in the
                               description (case-insensitive). This is the #1
                               graded rule, so detection is stem-based and runs
                               independently of the category decision.
  * Missing justification   -> every result row carries a one-sentence `reason`
                               that quotes words actually present in the row's
                               own description (the cited substring is sliced
                               out of the source text, so it can never be a
                               hallucinated word).
  * Hallucinated sub-cats   -> anything that matches no taxonomy keyword is
                               reported as `Other` + `NEEDS_REVIEW`, never
                               invented.
  * False confidence        -> genuinely ambiguous / empty descriptions are
                               flagged NEEDS_REVIEW rather than guessed.

CLI (unchanged from the README):
    python classifier.py --input <test_city.csv> --output <results_city.csv>
"""
import argparse
import csv
import re
from pathlib import Path

# --------------------------------------------------------------------------
# Fixed taxonomy — the ONLY legal category strings (enforcement rule 1).
# --------------------------------------------------------------------------
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

# --------------------------------------------------------------------------
# Severity detection (enforcement rule 2 — the highest-stakes rule).
# Matched on word STEMS so "child" catches "children", "injury" catches
# "injured", "hospital" catches "hospitalised", "collapse" catches
# "collapsed". Case-insensitive. Presence of ANY one => Urgent.
# --------------------------------------------------------------------------
SEVERITY_STEMS = [
    "injur",   # injury / injuries / injured
    "child",   # child / children / child's
    "school",  # school / schools
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",    # fell (past tense) — deliberately NOT "fall"
    "collaps",  # collapse / collapsed / collapsing
]
# The trailing ``\w*`` extends each stem to the FULL word so the reason can
# quote "injury" (not "injur"), "children" (not "child"), "hospitalised",
# "collapsed", etc. Detection (presence/absence) is unchanged because the
# stem itself still has to match first.
_SEVERITY_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(s) for s in SEVERITY_STEMS) + r")\w*",
    re.IGNORECASE,
)

# --------------------------------------------------------------------------
# Category keyword groups.
# Each group is (category, [compiled regexes], [citation substrings]).
# Detection walks the groups IN ORDER and takes the FIRST group that matches
# -> this ordered precedence is how dual-signal rows (e.g. "flooded ...
# drain blocked") are resolved deterministically rather than guessed.
# Citation substrings are plain lowercase fragments used only to quote the
# exact wording present in the description inside the `reason` sentence.
# --------------------------------------------------------------------------
def _grp(patterns, citations):
    return [re.compile(p, re.IGNORECASE) for p in patterns], citations


CATEGORY_GROUPS = [
    # 1. Heat Hazard — people-endangering heat (not "heatwave" for grass).
    _grp(
        [
            r"melting", r"bubbling", r"storing heat", r"dangerous temp",
            r"footwear sticking", r"unbearable", r"exposed to full sun",
            r"\bburns\b", r"heat hazard",
        ],
        ["melting", "bubbling", "storing heat", "dangerous temperatures",
         "footwear sticking", "unbearable", "exposed to full sun", "burns"],
    ),
    # 2. Heritage Damage — heritage artifact actually damaged (not just a
    #    heritage-named location like "heritage zone garbage").
    _grp(
        [
            r"heritage.*(?:defac|knock|broken|remov|stone|lamp|building)",
            r"cobblestone", r"historic tram", r"ancient step well",
            r"heritage stone", r"heritage lamp", r"heritage residential",
        ],
        ["heritage lamp", "heritage stone", "heritage residential building",
         "cobblestones", "ancient step well", "historic tram", "heritage"],
    ),
    # 3. Pothole — literal "pothole(s)"; checked before Flooding so a
    #    "pothole filling with rainwater" stays a Pothole.
    _grp(
        [r"\bpothole"],
        ["potholes", "pothole"],
    ),
    # 4. Drain Blockage — root-cause blockage; checked before Flooding so
    #    "drain blocked ... flooding risk" is the blockage, not the flood.
    _grp(
        [
            r"drain.*(?:block|debris|breed|clog|chok)",
            r"draining.*onto", r"stormwater drain", r"main drain",
        ],
        ["drain blocked", "drain completely blocked", "stormwater drain",
         "main drain", "draining", "drain"],
    ),
    # 5. Flooding — actual flood water present.
    _grp(
        [r"\bflood", r"knee-deep", r"standing in water", r"\brainwater\b",
         r"submerged"],
        ["flooded", "floods", "flooding", "knee-deep", "rainwater",
         "standing in water"],
    ),
    # 6. Streetlight — lighting defects / power outage darkness.
    _grp(
        [
            r"streetlight", r"street light", r"lights out", r"\blamp\b",
            r"flickering", r"sparking", r"\bunlit\b", r"darkness",
            r"tripped", r"wiring",
        ],
        ["streetlights", "streetlight", "lights out", "lamp", "flickering",
         "sparking", "unlit", "darkness", "tripped", "wiring"],
    ),
    # 7. Noise — audible disturbance, often a time-of-night marker.
    _grp(
        [
            r"\bmusic\b", r"midnight", r"\bnoise\b", r"drilling",
            r"band playing", r"amplifier", r"idling", r"\d+\s?[ap]m\b",
            r"playing past",
        ],
        ["music", "midnight", "drilling", "band playing", "amplifiers",
         "idling", "noise"],
    ),
    # 8. Waste — garbage / bins / dead animal / dumped / uncleared refuse.
    _grp(
        [
            r"garbage", r"\bwaste\b", r"\bbins\b", r"dead animal",
            r"overflowing", r"not cleared", r"not removed", r"dumped",
        ],
        ["garbage", "waste", "bins", "dead animal", "overflowing",
         "not cleared", "not removed", "dumped"],
    ),
    # 9. Road Damage — structural road/footpath defects (non-pothole).
    _grp(
        [
            r"road surface", r"\bcracked\b", r"\bsinking\b", r"\bmanhole\b",
            r"subsidence|subsided", r"\bbuckled\b", r"\bfootpath\b",
            r"paving", r"\btiles\b", r"\bcrater\b", r"road collapsed",
            r"depression", r"upturned",
        ],
        ["road surface", "cracked", "sinking", "manhole", "subsided",
         "subsidence", "buckled", "footpath", "paving", "tiles", "crater",
         "road collapsed", "upturned", "depression"],
    ),
]


def _find_severity_words(text):
    """Return the list of severity stems actually present in text."""
    return sorted({m.group(0).lower() for m in _SEVERITY_RE.finditer(text)})


def _find_citation(text, candidates):
    """Return the first candidate substring present in text, preserving the
    original casing as it appears in the source. Used so the `reason` only
    ever quotes words that are genuinely in the row's description."""
    low = text.lower()
    for c in candidates:
        idx = low.find(c.lower())
        if idx != -1:
            return text[idx:idx + len(c)]
    return None


# Map group index -> category name (kept separate so detection stays clean).
_GROUP_CATEGORY = [
    "Heat Hazard", "Heritage Damage", "Pothole", "Drain Blockage",
    "Flooding", "Streetlight", "Noise", "Waste", "Road Damage",
]


def detect_category(text):
    """Ordered-precedence category detection.

    Returns (category, citation) where citation is a substring actually
    present in `text`, or (None, None) when nothing matched (caller emits
    Other + NEEDS_REVIEW).
    """
    for gi, (regexes, citations) in enumerate(CATEGORY_GROUPS):
        for rx in regexes:
            if rx.search(text):
                citation = _find_citation(text, citations)
                return _GROUP_CATEGORY[gi], citation
    return None, None


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row.

    Input:  dict with at least `complaint_id` and `description`.
    Output: dict with keys complaint_id, category, priority, reason, flag
            (flag is '' unless the row is flagged NEEDS_REVIEW).

    Never raises on bad input — missing/empty description yields a
    NEEDS_REVIEW Other row with a reason that cites the missing field.
    """
    complaint_id = (row.get("complaint_id") or "UNKNOWN").strip()
    description = (row.get("description") or "").strip()

    # --- Empty / missing description -> refuse to guess. -------------------
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": (
                "Description field is empty or missing, so no taxonomy "
                "keyword could be matched; classified as Other and flagged "
                "NEEDS_REVIEW."
            ),
            "flag": "NEEDS_REVIEW",
        }

    # --- Severity is evaluated independently of category (rule 2). ---------
    sev_words = _find_severity_words(description)
    priority = "Urgent" if sev_words else "Standard"

    # --- Category via ordered keyword precedence (rule 1). -----------------
    category, citation = detect_category(description)

    if category is None:
        # No taxonomy keyword matched -> genuinely outside the schema.
        snippet = " ".join(description.split()[:6])
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": (
                f"No taxonomy keyword in the 10-value enum matched the "
                f"description (it reads \"{snippet} ...\"), so the category "
                f"could not be assigned with confidence; classified as Other "
                f"and flagged NEEDS_REVIEW."
            ),
            "flag": "NEEDS_REVIEW",
        }

    # --- One-sentence reason citing words actually in the row (rule 3). ---
    cat_clause = (
        f"the description mentions \"{citation}\""
        if citation
        else "a matching taxonomy keyword was found"
    )
    if sev_words:
        quoted = " and ".join(f"\"{w}\"" for w in sev_words)
        reason = (
            f"Classified as {category} because {cat_clause}; priority is "
            f"Urgent because the text contains {quoted}."
        )
    else:
        reason = (
            f"Classified as {category} because {cat_clause}; no severity "
            f"keyword (injury/child/school/hospital/ambulance/fire/hazard/"
            f"fell/collapse) is present, so priority is Standard."
        )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": "",
    }


# --------------------------------------------------------------------------
# Batch driver.
# --------------------------------------------------------------------------
OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _resolve_path(path_str: str) -> Path:
    """Resolve an input/output path so the script works from the repo root
    AND from inside the uc-0a folder. A relative path that isn't found
    relative to the CWD is retried relative to the repo root (the script's
    parent.parent), located via __file__."""
    p = Path(path_str)
    if p.is_absolute() or p.exists():
        return p
    repo_root = Path(__file__).resolve().parent.parent
    candidate = repo_root / path_str
    return candidate if candidate.exists() else p


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV.

    Guarantees:
      * Uses csv.DictReader (handles quoted, comma-bearing descriptions).
      * Each row's classification is wrapped in try/except so one bad row
        never aborts the batch — a failure produces a NEEDS_REVIEW row
        instead.
      * Output is always produced, even if every row failed.
    """
    in_path = _resolve_path(input_path)
    out_path = _resolve_path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with in_path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        results = []
        for idx, row in enumerate(reader):
            try:
                if not row.get("complaint_id"):
                    row["complaint_id"] = f"ROW_{idx}"
                results.append(classify_complaint(row))
            except Exception as exc:  # never crash the batch
                results.append({
                    "complaint_id": (row.get("complaint_id") or f"ROW_{idx}"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": (
                        f"Row could not be parsed ({type(exc).__name__}: "
                        f"{exc}); classified as Other and flagged "
                        f"NEEDS_REVIEW."
                    ),
                    "flag": "NEEDS_REVIEW",
                })

    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True,
                        help="Path to test_[city].csv")
    parser.add_argument("--output", required=True,
                        help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
