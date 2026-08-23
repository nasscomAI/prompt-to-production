import argparse
import re


FLOODING_TERMS = (
    "flood",
    "flooded",
    "flooding",
    "waterlogged",
    "waterlogging",
    "water logged",
    "standing water",
    "water accumulation",
    "submerged",
    "inundated",
)


def _extract_location(text: str) -> str:
    match = re.search(
        r"\b(?:in|near|at|on)\s+([A-Za-z][A-Za-z .'-]*?)"
        r"(?=\s+(?:is|was|has|with|and|but|after|due|causing|because|"
        r"there|the|water|flood|flooded|flooding|waterlogged|standing)\b|[,.!?]|$)",
        text,
        re.IGNORECASE,
    )
    return match.group(1).strip() if match else ""


def _has_flood_evidence(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in FLOODING_TERMS)


def detect_flooding(location: str, description: str, image_evidence: str = "") -> dict[str, str]:
    """Produce a flooding report using only supplied text and image evidence."""
    description = (description or "").strip()
    image_evidence = (image_evidence or "").strip()
    evidence = " ".join(part for part in (description, image_evidence) if part)
    location_value = (location or "").strip() or "Unknown"

    if not _has_flood_evidence(evidence):
        return {"Location": location_value, "Fault": "Unknown", "Situation": "Unknown"}

    fault = "Waterlogging" if "waterlog" in evidence.lower() or "standing water" in evidence.lower() else "Flooding"
    situation = description or image_evidence
    return {"Location": location_value, "Fault": fault, "Situation": situation}


def classify_text(text: str, image_evidence: str = "") -> dict[str, str]:
    """Process a complete natural-language flooding report."""
    report = (text or "").strip()
    location = _extract_location(report)
    return detect_flooding(location, report, image_evidence)


def main():
    parser = argparse.ArgumentParser(description="Detect flooding and waterlogging reports.")
    parser.add_argument("--text", help="Complete natural-language flooding report")
    parser.add_argument("--location", help="Location supplied by the user")
    parser.add_argument("--description", help="Description supplied by the user")
    parser.add_argument("--image-evidence", default="", help="Text describing visible evidence in the uploaded image")
    args = parser.parse_args()

    if args.text:
        result = classify_text(args.text, args.image_evidence)
    elif args.location is not None or args.description is not None or args.image_evidence:
        result = detect_flooding(args.location or "", args.description or "", args.image_evidence)
    else:
        parser.error("provide --text or --location/--description")
    print(result)

if __name__ == "__main__":
    main()
