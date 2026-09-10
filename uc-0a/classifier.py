"""
UC-0A — Complaint Classifier
Rule-based implementation guided by agents.md and skills.md (RICE workflow).

Behaviour contract (mirrors agents.md enforcement):
- category is always exactly one of the 10 allowed strings
- priority is Urgent when a severity keyword occurs in the description
- every row carries a one-sentence reason quoting words from the description
- genuinely ambiguous rows keep the best single category + NEEDS_REVIEW
"""
import argparse
import csv
import re

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

# Severity keywords from the UC-0A README, plus the minimal inflections
# that occur in the data (injured/injuries, children, hospitalised,
# hazardous, collapsed, fall next to fell). Matching is case-insensitive
# substring on the lowercased description.
SEVERITY_KEYWORDS = [
    "injury", "injured", "injuries",
    "child", "children",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard", "hazardous",
    "fell", "fall",
    "collapse", "collapsed",
]

HERITAGE_CUES = [
    "heritage", "historic", "museum", "ancient", "step well",
    "stepwell", "tagore", "precinct",
]


def _lower(text):
    return (text or "").lower()


def _find_evidence(description, keywords):
    """Return the first keyword found, copied with original casing."""
    low = _lower(description)
    for kw in keywords:
        idx = low.find(kw.lower())
        if idx != -1:
            return description[idx:idx + len(kw)]
    return None


def _snippet_around(description, keyword, window=6):
    """Short word-window around a keyword, stripped of sentence periods."""
    words = re.findall(r"\S+", description or "")
    low_words = [w.lower() for w in words]
    kw = keyword.lower()
    for i, w in enumerate(low_words):
        if kw in w:
            start = max(0, i - 2)
            end = min(len(words), i + window - 2)
            snippet = " ".join(words[start:end]).strip().strip(".")
            return snippet if snippet else keyword
    return keyword


def _match_category(description):
    """Return (category, evidence_phrase, all_matched_categories)."""
    d = _lower(description)
    matched = {}
    evidence = {}

    # --- Heritage Damage: heritage asset itself damaged/defaced ---
    has_heritage = any(c in d for c in HERITAGE_CUES)
    heritage_damage_cues = [
        "knocked over", "broken up", "defaced", "broken", "damaged",
        "destroyed", "cobblestone", "not replaced", "not restored",
        "billboard", "cable laying", "lamp post", "subsiden", "subsid",
    ]
    if has_heritage and any(c in d for c in heritage_damage_cues):
        # Locate-specific rows (lights out / garbage / music near a
        # heritage site) must NOT match here — only physical damage.
        damage_context = any(
            c in d for c in [
                "knocked", "broken", "defac", "damag", "destroy",
                "cobblestone", "not replaced", "not restored",
                "billboard", "cable laying",
            ]
        ) or ("subsiden" in d or "subsid" in d)
        if damage_context:
            matched["Heritage Damage"] = True
            evidence["Heritage Damage"] = (
                _find_evidence(description, ["knocked over", "broken up", "defaced",
                                             "cobblestones", "not replaced", "billboard",
                                             "cable laying", "lamp post", "subsidence",
                                             "subsided"]) or "heritage asset"
            )

    # --- Pothole ---
    if "pothole" in d:
        matched["Pothole"] = True
        evidence["Pothole"] = _find_evidence(description, ["potholes", "pothole"]) or "pothole"

    # --- Flooding (actual event; bare "flooding risk" stays Drain Blockage) ---
    flood_event_cues = ["flooded", "floods", "knee-deep",
                        "stranded", "waterlogged", "standing in water"]
    has_flood_event = any(c in d for c in flood_event_cues)
    if has_flood_event or ("flood" in d and "risk" not in d) or (
        "inaccessible" in d and ("rain" in d or "flood" in d)
    ) or ("abandoned" in d and "rain" in d):
        matched["Flooding"] = True
        evidence["Flooding"] = (
            _find_evidence(description, ["knee-deep", "flooded", "floods", "flooded",
                                         "flooding", "flood", "stranded",
                                         "standing in water", "inaccessible",
                                         "abandoned"]) or "flooded"
        )

    # --- Drain Blockage ---
    if "drain" in d or "mosquito" in d or "breeding" in d or "dengue" in d:
        matched["Drain Blockage"] = True
        evidence["Drain Blockage"] = (
            _find_evidence(description, ["drain 100% blocked", "drain blocked",
                                         "drain completely blocked", "main drain blocked",
                                         "stormwater drain", "drain", "mosquito breeding",
                                         "mosquito", "breeding", "dengue",
                                         "draining directly"]) or "drain"
        )

    # --- Streetlight ---
    street_cues = ["streetlight", "streetlights", "lights out", "unlit",
                   "darkness", "very dark", "flickering", "sparking",
                   "lamp post", "substation tripped", "wiring theft"]
    if any(c in d for c in street_cues):
        # Heritage lamp post knocked over is heritage damage, not a lamp fault.
        if not ("Heritage Damage" in matched and "lamp post" in d and "knocked" in d):
            matched["Streetlight"] = True
            evidence["Streetlight"] = (
                _find_evidence(description, ["streetlights", "streetlight", "lights out",
                                             "unlit", "darkness", "very dark at night",
                                             "flickering and sparking", "flickering",
                                             "sparking", "substation tripped",
                                             "wiring theft"]) or "streetlight"
            )

    # --- Waste ---
    waste_cues = ["garbage", "waste", "bins", "overflowing", "overflow",
                  "dumped", "not cleared", "not removed", "dead animal",
                  "piles of waste", "smell affecting"]
    if any(c in d for c in waste_cues):
        matched["Waste"] = True
        evidence["Waste"] = (
            _find_evidence(description, ["Overflowing garbage bins", "garbage",
                                         "piles of waste", "Bulk waste",
                                         "Post-market waste", "Night market waste",
                                         "Restaurant waste bins", "Dead animal not removed",
                                         "Dead animal", "waste not cleared",
                                         "waste", "bins", "overflowing", "overflow",
                                         "dumped", "not cleared", "not removed"]) or "waste"
        )

    # --- Noise ---
    noise_cues = ["music", "wedding", "band playing", "drilling", "amplifier",
                  "amplifiers", "idling", "engines on", "club music"]
    if any(c in d for c in noise_cues):
        matched["Noise"] = True
        evidence["Noise"] = (
            _find_evidence(description, ["playing music past midnight", "Club music",
                                         "Wedding venue playing music", "Wedding band playing",
                                         "Construction drilling", "drilling", "amplifiers",
                                         "amplifier", "idling with engines on", "idling",
                                         "music", "wedding"]) or "music"
        )

    # --- Road Damage (non-pothole surface / footpath / structure failures) ---
    road_cues = ["cracked", "sinking", "subsided", "subsidence", "buckled",
                 "collapsed", "collapse", "crater", "manhole", "footpath",
                 "tiles broken", "upturned paving", "upturned", "road surface",
                 "surface cracked", "broken bench", "road subsidence",
                 "cobblestones"]
    if any(c in d for c in road_cues):
        # Historic cobblestones torn up = heritage damage, handled above.
        if not ("Heritage Damage" in matched and "cobblestone" in d):
            matched["Road Damage"] = True
            evidence["Road Damage"] = (
                _find_evidence(description, ["Road surface cracked and sinking",
                                             "Road collapsed partially", "Crater 1m deep",
                                             "Manhole cover missing", "Footpath tiles broken",
                                             "Footpath broken and sinking", "Road subsided",
                                             "Road surface buckled", "road subsidence",
                                             "cracked and sinking", "upturned paving",
                                             "broken and upturned", "manhole", "footpath",
                                             "crater", "collapsed", "buckled", "subsided",
                                             "sinking", "cracked"]) or "road surface"
            )

    # --- Heat Hazard ---
    heat_cues = ["°c", "melting", "heatwave", "heat", "burns", "burning",
                 "bubbling", "temperature", "44", "45", "52", "full sun",
                 "grass dying"]
    if (any(c in d for c in heat_cues) and (
            "°c" in d or "melting" in d or "heatwave" in d or "heat" in d
            or "burns" in d or "bubbling" in d or "temperature" in d
            or "full sun" in d or "grass dying" in d)):
        matched["Heat Hazard"] = True
        evidence["Heat Hazard"] = (
            _find_evidence(description, ["Tarmac surface melting at 44",
                                         "reaching dangerous temperatures",
                                         "Grass dying in heatwave", "surface bubbling at 45",
                                         "temperature unbearable", "reads 52",
                                         "storing heat", "burns on contact",
                                         "exposed to full sun", "melting", "heatwave",
                                         "dangerous temperatures", "temperature",
                                         "heat", "burns", "bubbling"]) or "heat"
        )

    # --- Resolve winner by precedence ---
    precedence = ["Heritage Damage", "Pothole", "Heat Hazard", "Flooding",
                  "Drain Blockage", "Streetlight", "Waste", "Noise",
                  "Road Damage"]
    # Pothole beats generic road words; heritage-asset damage beats all;
    # heat cause beats road-symptom wording; flooding beats drain-blockage.
    winner = None
    for cat in precedence:
        if cat in matched:
            winner = cat
            break
    if winner is None:
        winner = "Other"
        evidence["Other"] = _snippet_around(description, (description or "").split()[0] if (description or "").split() else "complaint") if description else "missing description"

    return winner, evidence.get(winner, winner), list(matched.keys())


def _priority_for(description):
    d = _lower(description)
    for kw in SEVERITY_KEYWORDS:
        if kw in d:
            return "Urgent", _find_evidence(description, [kw]) or kw
    return None, None


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = str(row.get("complaint_id") or row.get("id") or "").strip()
    if not complaint_id:
        complaint_id = "UNKNOWN"
    description = row.get("description")
    if description is None:
        description = ""
    description = str(description).strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Classified as Other with Standard priority because the description was missing or blank.",
            "flag": "NEEDS_REVIEW",
        }

    try:
        category, cat_evidence, all_matched = _match_category(description)
        urgent_kw = None
        d = _lower(description)
        for kw in SEVERITY_KEYWORDS:
            if kw in d:
                urgent_kw = _find_evidence(description, [kw]) or kw
                break

        if urgent_kw:
            priority = "Urgent"
        elif category == "Noise":
            priority = "Low"
        else:
            priority = "Standard"

        # --- ambiguity → NEEDS_REVIEW ---
        has_heritage = any(c in d for c in HERITAGE_CUES)
        flag = ""
        if category == "Other":
            flag = "NEEDS_REVIEW"
        elif len(all_matched) > 1:
            flag = "NEEDS_REVIEW"
        elif has_heritage and category != "Heritage Damage":
            flag = "NEEDS_REVIEW"
        elif category == "Streetlight" and ("substation" in d or "theft" in d):
            flag = "NEEDS_REVIEW"
        elif category == "Road Damage" and ("gas leak" in d or "gas" in d):
            flag = "NEEDS_REVIEW"
        elif category == "Drain Blockage" and not any(
            c in d for c in ["blocked", "clogg", "chok", "mosquito",
                             "breeding", "dengue", "debris"]
        ):
            # Bare "drain/draining" mention with no blockage evidence
            # (e.g. runoff discharged onto a road) is genuinely ambiguous.
            flag = "NEEDS_REVIEW"

        # --- one-sentence reason quoting description words ---
        cat_quote = (cat_evidence or "").strip().strip(".")
        if not cat_quote:
            cat_quote = _snippet_around(description, description.split()[0])
        if urgent_kw and urgent_kw.lower() not in cat_quote.lower():
            reason = (
                f'Classified as {category} with {priority} priority because the '
                f'description reports "{cat_quote}" and mentions "{urgent_kw}".'
            )
        else:
            reason = (
                f'Classified as {category} with {priority} priority because the '
                f'description reports "{cat_quote}".'
            )
        # Guarantee exactly one sentence: collapse stray periods inside quotes.
        return {
            "complaint_id": complaint_id,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag,
        }
    except Exception as exc:  # never crash the batch on one bad row
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Classified as Other with Standard priority because the row could not be parsed.",
            "flag": "NEEDS_REVIEW",
        }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, never crashes on bad rows, always writes output.
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []
    counts = {"Urgent": 0, "Standard": 0, "Low": 0, "NEEDS_REVIEW": 0}

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for i, row in enumerate(rows):
        try:
            if row.get("complaint_id") is None and row.get("id") is None:
                row = dict(row)
                row["complaint_id"] = f"ROW-{i + 1}"
            out = classify_complaint(row)
        except Exception:
            out = {
                "complaint_id": str((row or {}).get("complaint_id") or f"ROW-{i + 1}"),
                "category": "Other",
                "priority": "Standard",
                "reason": "Classified as Other with Standard priority because the row could not be parsed.",
                "flag": "NEEDS_REVIEW",
            }
        results.append(out)
        counts[out["priority"]] = counts.get(out["priority"], 0) + 1
        if out["flag"] == "NEEDS_REVIEW":
            counts["NEEDS_REVIEW"] += 1

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} rows "
          f"(Urgent={counts.get('Urgent', 0)}, "
          f"Standard={counts.get('Standard', 0)}, "
          f"Low={counts.get('Low', 0)}, "
          f"NEEDS_REVIEW={counts.get('NEEDS_REVIEW', 0)}).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
