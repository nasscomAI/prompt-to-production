"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """ 
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Implements UC-0A closed taxonomy and severity keyword enforcement.
    """

    category_taxonomy = {
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
    }

    urgent_keywords = [
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

    # Try best-effort retrieval of a complaint identifier.
    complaint_id = None
    for key in ("complaint_id", "id", "complaintId"):
        if key in row and row.get(key) not in (None, ""):
            complaint_id = row.get(key)
            break

    # Build a description string from all text-like fields.
    # (We intentionally don't assume a specific column name.)
    parts = []
    for k, v in row.items():
        if v is None:
            continue
        s = str(v).strip()
        if not s:
            continue
        kl = str(k).lower()
        # Prefer likely description columns, but fall back to any non-id text.
        if any(token in kl for token in ["description", "complaint", "details", "issue", "problem", "comment", "message"]):
            parts.append(s)
        elif kl in ("complaint_id", "id", "complaintid"):
            continue
        else:
            parts.append(s)

    description = " ".join(parts).strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "The complaint description is missing or empty, so there is no clear evidence to map it to the allowed taxonomy.",
            "flag": "NEEDS_REVIEW",
        }

    d_lower = description.lower()

    # Priority enforcement
    priority = "Urgent" if any(kw in d_lower for kw in urgent_keywords) else "Standard"

    # Category keyword mapping (conservative; ambiguous cases go to Other + NEEDS_REVIEW)
    candidate_categories = []

    def has_any(keywords):
        return any(kw in d_lower for kw in keywords)

    pothole_kw = ["pothole", "potholes", "pitted road", "broken road", "potholes on road"]
    road_damage_kw = ["road damaged", "crack", "cracks", "cracked", "asphalt", "damaged road", "rough road", "uneven road", "broken patch"]
    flooding_kw = ["flood", "flooding", "waterlogging", "water logged", "stagnant water"]
    streetlight_kw = ["streetlight", "street light", "lamp", "lights out", "led not working", "pole light", "bollard"]
    waste_kw = ["garbage", "waste", "dump", "dumping", "garbage dump", "litter", "trash", "overflowing dustbin"]
    noise_kw = ["noise", "loud", "horn", "banging", "party", "disturb", "firecracker", "music too loud"]
    heritage_damage_kw = ["heritage", "monument", "temple", "mosque", "church", "historic", "memorial", "sculpture damaged"]
    heat_hazard_kw = ["heat", "hot", "overheated", "sunstroke", "heatwave", "unsafe temperature", "temperature"]
    drain_blockage_kw = ["drain", "sewer", "manhole", "choke", "blocked drain", "clogged", "overflow", "sump"]

    if has_any(pothole_kw):
        candidate_categories.append("Pothole")
    if has_any(flooding_kw):
        candidate_categories.append("Flooding")
    if has_any(streetlight_kw):
        candidate_categories.append("Streetlight")
    if has_any(waste_kw):
        candidate_categories.append("Waste")
    if has_any(noise_kw):
        candidate_categories.append("Noise")
    if has_any(road_damage_kw):
        candidate_categories.append("Road Damage")
    if has_any(heritage_damage_kw):
        candidate_categories.append("Heritage Damage")
    if has_any(heat_hazard_kw):
        candidate_categories.append("Heat Hazard")
    if has_any(drain_blockage_kw):
        candidate_categories.append("Drain Blockage")

    # If we matched multiple categories, treat as ambiguous.
    if len(set(candidate_categories)) == 1:
        category = list(set(candidate_categories))[0]
        flag = ""
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # If still Other, attempt a looser single match using substrings but keep ambiguity conservative.
    if category == "Other" and not candidate_categories:
        # try generic hints; only map if exactly one clear hint exists
        generic_map = {
            "Drain Blockage": ["blocked", "clogged"],
            "Flooding": ["water"],
            "Waste": ["trash", "garbage"],
            "Noise": ["horn", "noise", "loud"],
            "Streetlight": ["lamp", "street light"],
            "Road Damage": ["crack", "damaged", "broken"],
            "Pothole": ["pothole"],
        }
        generic_candidates = []
        for cat, kws in generic_map.items():
            if has_any(kws):
                generic_candidates.append(cat)
        if len(set(generic_candidates)) == 1:
            category = list(set(generic_candidates))[0]
            flag = ""
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"

    # Reason: exactly one sentence; cite specific words from description.
    # We cite up to two distinctive substrings we used for classification.
    if category != "Other":
        # choose an evidence snippet from keywords present
        evidence = None
        evidence_lit = None
        for kw in sorted(urgent_keywords + pothole_kw + road_damage_kw + flooding_kw + streetlight_kw + waste_kw + noise_kw + heritage_damage_kw + heat_hazard_kw + drain_blockage_kw, key=len, reverse=True):
            if kw in d_lower:
                evidence_lit = kw
                break
        if evidence_lit:
            evidence = evidence_lit
        else:
            evidence = description[:80].strip().rstrip('.')

        if priority == "Urgent":
            # cite also an urgent keyword
            urgent_hit = next((kw for kw in urgent_keywords if kw in d_lower), None)
            if urgent_hit:
                reason = f"The description contains '{evidence}' and the severity keyword '{urgent_hit}', indicating an urgent {category.lower()} issue."
            else:
                reason = f"The description contains '{evidence}', which supports category '{category}' and requires attention due to urgent severity context."
        else:
            reason = f"The description contains '{evidence}', which supports category '{category}'."
    else:
        # refusal condition, but still grounded in available text.
        reason = "The complaint details do not provide clear discriminating keywords for a single allowed category, so the classification is flagged for review."

    # Final sanity guardrail against taxonomy drift.
    if category not in category_taxonomy:
        category = "Other"
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }



def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV."""

    results_fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    def safe_read_rows():
        with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield row

    with open(output_path, "w", encoding="utf-8", newline="") as out_f:
        writer = csv.DictWriter(out_f, fieldnames=results_fieldnames)
        writer.writeheader()

        try:
            for row in safe_read_rows():
                try:
                    res = classify_complaint(row)
                except Exception:
                    # Refusal-condition defaults for per-row failures.
                    res = {
                        "complaint_id": row.get("complaint_id") or row.get("id") if isinstance(row, dict) else None,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "The complaint could not be classified due to missing or unclear evidence in the available fields, so it is flagged for review.",
                        "flag": "NEEDS_REVIEW",
                    }

                # Ensure output schema and no nulls that violate expectations.
                if res.get("flag") is None:
                    res["flag"] = ""
                for k in results_fieldnames:
                    if k not in res or res[k] is None:
                        res[k] = "" if k == "flag" else ("Other" if k == "category" else "Standard" if k == "priority" else "")

                writer.writerow({k: res[k] for k in results_fieldnames})
        except FileNotFoundError:
            raise



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
