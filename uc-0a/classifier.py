"""
UC-0A — Complaint Classifier
Implements agents.md (RICE) + skills.md (classify_complaint, batch_classify).

Enforcement summary:
  E1 taxonomy closed — category always one of the 10 allowed strings.
  E2 severity — Urgent iff severity keywords (with inflections) present.
  E3 justification — reason always one sentence quoting description words.
  E4 ambiguity — NEEDS_REVIEW on empty / no-signal / tied signals.
  E5 precedence — fixed decision order so same-type complaints stay identical.
"""
import argparse
import csv
import os
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

SEVERITY_RE = re.compile(
    r"\b(injury|injuries|injured|child|children|school|hospital|hospitalised"
    r"|hospitalized|ambulance|fire|hazard|hazardous|fell|fallen|collapse"
    r"|collapsed|collapses|collapsing)\b",
    re.IGNORECASE,
)

# --- signal patterns (all case-insensitive) ---
POTHOLE_RE = re.compile(r"\bpotholes?\b", re.IGNORECASE)
FLOOD_ACTUAL_RE = re.compile(
    r"\bflooded\b|\bfloods\b|\bflooding\b|\bwaterlogged\b|knee[\s-]?deep"
    r"|\bstranded\b|standing in water|inundat",
    re.IGNORECASE,
)
FLOOD_RISK_QUALIFIER_RE = re.compile(
    r"\brisk\b|\blikely\b|\bmay\b|\bpotential\b|\bthreat\b", re.IGNORECASE
)
STREETLIGHT_RE = re.compile(
    r"streetlights?|street lights?|lights? out|unlit|darkness|dark at night"
    r"|flickering|sparking|wiring theft|substation tripped|\blamps?\b|no light",
    re.IGNORECASE,
)
DRAIN_RE = re.compile(r"\bdrains?\b|\bdrainage\b|\bstormwater\b", re.IGNORECASE)
DRAIN_BLOCK_RE = re.compile(
    r"block|chok|clog|debris|mosquito|breeding", re.IGNORECASE
)
WASTE_RE = re.compile(
    r"garbage|waste|bins? overflowing|overflowing|dumped|dumping|not cleared"
    r"|dead animal|smell affecting|piles? of waste|piles\b|market waste|bins\b",
    re.IGNORECASE,
)
NOISE_RE = re.compile(
    r"music|noise|noisy|drilling|amplifiers?|band playing|audible|loud"
    r"|past midnight|idling|engines? on",
    re.IGNORECASE,
)
HEAT_RE = re.compile(
    r"heat|melting|melts?|\bhot\b|temperature|°c|degrees?|heatwave|heat wave"
    r"|sunburn|burns? on contact|burning|storing heat|unbearable|sticking"
    r"|bubbling at \d|reads? \d+\s*°?c|44\s*°?c|45\s*°?c|52\s*°?c"
    r"|dead trees|dying grass|grass dying|full sun",
    re.IGNORECASE,
)
HERITAGE_CTX_RE = re.compile(
    r"heritage|monument|museum|step[\s-]?well|historic|historical|ancient"
    r"|archaeolog|tram road|cobblestones?|precinct|palace|tagore|lamp post"
    r"|heritage zone|heritage area|heritage street|heritage precinct"
    r"|heritage stone|old city",
    re.IGNORECASE,
)
HERITAGE_DMG_RE = re.compile(
    r"knocked over|knocked|broken up|defaced|damaged|destroyed|removed"
    r"|not replaced|not restored|billboard|cable laying|utility work.{0,40}"
    r"heritage|heritage.{0,40}(damag|defac|remov|knock|broken)",
    re.IGNORECASE,
)
ROAD_DMG_RE = re.compile(
    r"cracked|sinking|subsiden|subsided|crater|buckled|footpath|tiles broken"
    r"|upturned|paving|manhole|bench|shelter roof|road surface|tyre blowouts?"
    r"|tire blowouts?|accident risk|depth invisible|gas pipeline|road dividers?"
    r"|cable laying|surface cracked|approach road|bridge approach",
    re.IGNORECASE,
)


def _evidence(text: str, pattern: re.Pattern, limit: int = 3):
    """Return up to `limit` verbatim substrings of text matching pattern."""
    found = []
    for m in pattern.finditer(text):
        s = m.group(0).strip()
        if s and s.lower() not in [f.lower() for f in found]:
            found.append(s)
        if len(found) >= limit:
            break
    return found


def _has_severity(text: str) -> bool:
    return bool(SEVERITY_RE.search(text or ""))


def _heritage_fabric_damaged(text: str) -> bool:
    if not HERITAGE_CTX_RE.search(text):
        return False
    # damage must be present AND tied to the heritage context, not e.g.
    # "heritage street, lights out" (no damage words at all).
    if not HERITAGE_DMG_RE.search(text):
        return False
    # Exclude pure location mentions where the only "damage" word is about
    # unrelated infrastructure (lights/potholes/waste) — those keep their
    # own category per E5. Require a heritage-fabric damage pairing.
    fabric_pair = re.compile(
        r"(lamp post|tram|cobblestone|monument|museum|step[\s-]?well|building"
        r"|palace|paving|stone|precinct|zone|area).{0,60}"
        r"(knock|broken|defac|damag|remov|not restor|not replac|billboard)"
        r"|(knock|broken|defac|damag|remov|not restor|not replac|billboard)"
        r".{0,60}(lamp post|tram|cobblestone|monument|museum|step[\s-]?well"
        r"|building|palace|paving|stone|precinct|zone|area)",
        re.IGNORECASE | re.DOTALL,
    )
    return bool(fabric_pair.search(text))


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    Never raises on bad input — degrades to Other/NEEDS_REVIEW.
    """
    try:
        cid = str(row.get("complaint_id") or "").strip()
        if not cid:
            cid = "ROW-UNKNOWN"
        desc_raw = row.get("description")
        desc = "" if desc_raw is None else str(desc_raw)
        loc_raw = row.get("location") or ""
        loc = str(loc_raw)
        text = desc.strip()

        # E4: null / empty → Other + NEEDS_REVIEW, never crash.
        if not text:
            if loc.strip():
                return {
                    "complaint_id": cid,
                    "category": "Other",
                    "priority": "Low",
                    "reason": f'No usable description, only location "{loc.strip()[:60]}", marked for review.',
                    "flag": "NEEDS_REVIEW",
                }
            return {
                "complaint_id": cid,
                "category": "Other",
                "priority": "Low",
                "reason": "No usable description provided, marked for review.",
                "flag": "NEEDS_REVIEW",
            }

        urgent = _has_severity(text)
        sev_hit = _evidence(text, SEVERITY_RE, 1)
        sev_note = f", noting \"{sev_hit[0]}\"" if sev_hit else ""

        heritage_hit = _heritage_fabric_damaged(text)
        flood_actual = bool(FLOOD_ACTUAL_RE.search(text))
        # "flooding risk this week" without an actual event is a drain issue.
        if flood_actual and FLOOD_RISK_QUALIFIER_RE.search(text) and not re.search(
            r"\bflooded\b|knee[\s-]?deep|\bstranded\b|\bwaterlogged\b|\babandoned\b",
            text,
            re.IGNORECASE,
        ):
            flood_actual = False  # risk language only → not an actual flood
        pothole_hit = bool(POTHOLE_RE.search(text))
        street_hit = bool(STREETLIGHT_RE.search(text))
        drain_hit = bool(DRAIN_RE.search(text) and DRAIN_BLOCK_RE.search(text))
        waste_hit = bool(WASTE_RE.search(text))
        noise_hit = bool(NOISE_RE.search(text))
        heat_hit = bool(HEAT_RE.search(text))
        road_hit = bool(ROAD_DMG_RE.search(text))

        # E5 precedence decision (deterministic, anti-drift).
        category = "Other"
        ev = []
        if heritage_hit:
            category = "Heritage Damage"
            ev = _evidence(text, HERITAGE_CTX_RE, 2) + _evidence(
                text, HERITAGE_DMG_RE, 1
            )
        elif flood_actual:
            category = "Flooding"
            ev = _evidence(text, FLOOD_ACTUAL_RE, 3)
        elif pothole_hit:
            category = "Pothole"
            ev = _evidence(text, POTHOLE_RE, 1) + _evidence(
                text, re.compile(r"tyre damage|blowouts?|wheel|depth invisible",
                                 re.IGNORECASE), 2,
            )
        elif street_hit:
            category = "Streetlight"
            ev = _evidence(text, STREETLIGHT_RE, 3)
        elif drain_hit:
            category = "Drain Blockage"
            ev = _evidence(text, DRAIN_RE, 1) + _evidence(
                text, DRAIN_BLOCK_RE, 2
            )
        elif waste_hit:
            category = "Waste"
            ev = _evidence(text, WASTE_RE, 3)
        elif noise_hit:
            category = "Noise"
            ev = _evidence(text, NOISE_RE, 3)
        elif heat_hit:
            category = "Heat Hazard"
            ev = _evidence(text, HEAT_RE, 3)
        elif road_hit:
            category = "Road Damage"
            ev = _evidence(text, ROAD_DMG_RE, 3)
        else:
            category = "Other"
            # quote the most informative words available for grounding
            words = re.findall(r"[A-Za-z]{4,}", text)[:3]
            ev = words

        # E4 ambiguity flag: empty handled above; here no-signal or true ties.
        # Decisive heritage-fabric wins (e.g. lamp post knocked over, paving
        # stone removed) are NOT ambiguous. But heritage *context* + road
        # structural damage with no decisive pairing (e.g. subsidence near a
        # step well) genuinely is — flag it while keeping best-guess category.
        flag = ""
        heritage_ctx = bool(HERITAGE_CTX_RE.search(text))
        signals = {
            "heritage": heritage_hit,
            "flood": flood_actual,
            "pothole": pothole_hit,
            "street": street_hit,
            "drain": drain_hit,
            "waste": waste_hit,
            "noise": noise_hit,
            "heat": heat_hit,
            "road": road_hit,
        }
        n_signals = sum(1 for v in signals.values() if v)
        # Genuinely ambiguous: heritage context + road damage without a
        # decisive fabric pairing, or nothing matched at all, or a very
        # vague one-liner with 3+ competing signals.
        heritage_road_ambiguous = heritage_ctx and road_hit and not heritage_hit
        if category == "Other":
            flag = "NEEDS_REVIEW"
        elif heritage_road_ambiguous:
            flag = "NEEDS_REVIEW"
        elif n_signals >= 3 and len(text.split()) <= 20:
            flag = "NEEDS_REVIEW"

        # E2 priority.
        if urgent:
            priority = "Urgent"
        elif category == "Other" and flag == "NEEDS_REVIEW":
            priority = "Low"
        else:
            priority = "Standard"

        # E3 grounded one-sentence reason quoting verbatim words.
        ev = [e for e in ev if e and e.lower() in text.lower()][:3]
        if not ev:
            words = re.findall(r"[A-Za-z]{4,}", text)[:2]
            ev = [w for w in words if w.lower() in text.lower()]
        if not ev:
            # Ultra-short/vague input (e.g. "hi"): quote it verbatim so the
            # reason stays grounded even when no keyword matched.
            ev = [text.strip()[:40]]
        quoted = ", ".join(f'"{e}"' for e in ev[:3]) if ev else '"complaint"'
        if flag == "NEEDS_REVIEW" and category != "Other":
            reason = (
                f"Classified as {category} due to {quoted}{sev_note} "
                f"in description, but flagged as ambiguous."
            )
        elif category == "Other":
            reason = (
                f"No clear category from {quoted}{sev_note} in description, "
                f"marked Other for review."
            )
        else:
            reason = (
                f"Classified as {category} due to {quoted}{sev_note} "
                f"in description."
            )
        # Keep it one sentence: collapse extra sentence breaks.
        reason = re.sub(r"\s+", " ", reason).strip()

        assert category in ALLOWED_CATEGORIES  # E1 guard
        return {
            "complaint_id": cid,
            "category": category,
            "priority": priority,
            "reason": reason,
            "flag": flag,
        }
    except Exception as exc:  # batch must never crash on a bad row
        cid = str((row or {}).get("complaint_id") or "ROW-UNKNOWN")
        return {
            "complaint_id": cid,
            "category": "Other",
            "priority": "Low",
            "reason": f"Row failed safe ({type(exc).__name__}), marked for review.",
            "flag": "NEEDS_REVIEW",
        }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls, never crashes on bad rows, always writes output.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(input_path, "r", newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader) if reader.fieldnames else []

    results = []
    for i, row in enumerate(rows, start=2):  # line numbers for synthetic ids
        try:
            if row is None:
                raise ValueError("null row")
            if not row.get("complaint_id"):
                row = dict(row)
                row["complaint_id"] = f"ROW-{i}"
            results.append(classify_complaint(row))
        except Exception as exc:
            results.append(
                {
                    "complaint_id": f"ROW-{i}",
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row failed safe ({type(exc).__name__}), marked for review.",
                    "flag": "NEEDS_REVIEW",
                }
            )

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["complaint_id", "category", "priority", "reason", "flag"]
        )
        writer.writeheader()
        writer.writerows(results)
    return len(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    n = batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output} ({n} rows)")
