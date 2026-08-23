"""Evidence-based smart-city traffic and route recommendation agent."""

import argparse
import json
import re
from typing import Any

CONDITION_TERMS = {
    "traffic jam": "Traffic Jam",
    "jammed": "Traffic Jam",
    "standstill": "Traffic Jam",
    "heavy traffic": "Heavy Traffic",
    "congested": "Heavy Traffic",
    "moderate traffic": "Moderate Traffic",
    "slow traffic": "Moderate Traffic",
}


def _condition(text: str) -> str:
    lowered = text.lower()
    for phrase, condition in CONDITION_TERMS.items():
        if phrase in lowered:
            return condition
    if any(word in lowered for word in ("clear", "normal traffic", "free flowing")):
        return "Normal"
    return "Unknown"


def recommend_route(origin: str, destination: str, routes: list[dict[str, Any]] | None = None, traffic_evidence: str = "", civic_reports: str = "", live_traffic_available: bool = False) -> dict[str, Any]:
    """Recommend the best supplied route without inventing live conditions."""
    origin = origin.strip()
    destination = destination.strip()
    if not origin or not destination:
        return {"Status": "Missing information", "Message": "Please provide both origin and destination."}

    routes = routes or []
    evidence = " ".join(part.strip() for part in (traffic_evidence, civic_reports) if part.strip())
    if not routes:
        return {
            "Origin": origin,
            "Destination": destination,
            "Recommended Route": "Unavailable",
            "Condition": _condition(evidence),
            "Reason": "No verified route options were provided.",
            "Traffic Data": "Live traffic information unavailable" if not live_traffic_available else "Available",
        }

    def route_score(route: dict[str, Any]) -> tuple[int, float]:
        text = json.dumps(route).lower()
        penalty = 100 if any(term in text for term in ("flood", "closed", "blocked", "accident", "traffic jam")) else 0
        if "heavy traffic" in text:
            penalty += 50
        return penalty, float(route.get("duration_minutes", 0) or 0)

    selected = min(routes, key=route_score)
    route_name = str(selected.get("name") or selected.get("route") or "Unnamed route")
    selected_evidence = str(selected.get("evidence") or selected.get("condition") or "")
    return {
        "Origin": origin,
        "Destination": destination,
        "Recommended Route": route_name,
        "Condition": _condition(selected_evidence or evidence),
        "Reason": selected_evidence or "Selected from the supplied route options using the available evidence.",
        "Traffic Data": "Live traffic information unavailable" if not live_traffic_available else "Available",
    }


def _extract_places(text: str) -> tuple[str, str]:
    match = re.search(r"from\s+(.+?)\s+to\s+(.+?)(?:\.|,|$)", text, re.IGNORECASE)
    return (match.group(1).strip(), match.group(2).strip()) if match else ("", "")


def main() -> None:
    parser = argparse.ArgumentParser(description="Recommend routes from verified traffic evidence.")
    parser.add_argument("--origin", help="Starting location")
    parser.add_argument("--destination", help="Travel destination")
    parser.add_argument("--text", help="Natural-language travel request")
    parser.add_argument("--routes-file", help="JSON file containing supplied route candidates")
    parser.add_argument("--traffic", default="", help="Verified traffic evidence")
    parser.add_argument("--civic-reports", default="", help="Verified civic issue reports")
    parser.add_argument("--live-traffic", action="store_true", help="Use only when a trusted live source was obtained")
    args = parser.parse_args()

    origin, destination = args.origin or "", args.destination or ""
    if args.text:
        origin, destination = _extract_places(args.text)
    routes = []
    if args.routes_file:
        with open(args.routes_file, encoding="utf-8") as route_file:
            routes = json.load(route_file)
    print(recommend_route(origin, destination, routes, args.traffic, args.civic_reports, args.live_traffic))


if __name__ == "__main__":
    main()
