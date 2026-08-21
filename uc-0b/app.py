"""Civic infrastructure reporting classifier.

The app determines whether a report is about a streetlight or traffic signal
based on the user-provided location, description, and any image context. It
returns only supported facts in the required fields: Location, Fault, and
Situation.
"""

import argparse
import re
from typing import Dict, Optional


def _normalize(text: Optional[str]) -> str:
    return (text or "").strip()


def _match_any(text: str, phrases: list[str]) -> bool:
    lowered = text.lower()
    for phrase in phrases:
        if phrase.lower() in lowered:
            return True
    return False


def classify_civic_issue(location: str, description: str) -> Dict[str, str]:
    """Classify a civic issue report into Location, Fault, and Situation.

    The fault is only set to Streetlight or Traffic Signal when the description
    or other visible evidence explicitly supports that infrastructure. Otherwise,
    it must be Unknown.
    """
    location_name = _normalize(location)
    description_text = _normalize(description)

    streetlight_patterns = [
        "streetlight",
        "street light",
        "street lamp",
        "lamp post",
        "light is not working",
        "light not working",
        "lamp is broken",
        "streetlight is broken",
        "streetlight out",
        "stopped working",
        "dark at night",
        "no light",
        "flickering streetlight",
        "broken streetlight",
    ]
    traffic_signal_patterns = [
        "traffic signal",
        "traffic light",
        "signal is damaged",
        "signal is malfunctioning",
        "traffic signal is malfunctioning",
        "signal malfunction",
        "damaged signal",
        "broken traffic signal",
        "traffic light is damaged",
        "red light stays on",
        "signal not working",
        "light is malfunctioning",
    ]

    if _match_any(description_text, streetlight_patterns):
        fault = "Streetlight"
        if "light is not working" in description_text.lower() or "not working" in description_text.lower() or "out for" in description_text.lower() or "dark at night" in description_text.lower():
            situation = "light is not working"
        elif "flickering" in description_text.lower() or "sparking" in description_text.lower():
            situation = "light is malfunctioning"
        elif "broken" in description_text.lower() or "damaged" in description_text.lower():
            situation = "light is damaged"
        else:
            situation = "light is not working"
    elif _match_any(description_text, traffic_signal_patterns):
        fault = "Traffic Signal"
        if "malfunctioning" in description_text.lower() or "not working" in description_text.lower() or "stays on" in description_text.lower():
            situation = "signal is malfunctioning"
        elif "damaged" in description_text.lower() or "broken" in description_text.lower():
            situation = "signal is damaged"
        else:
            situation = "signal is malfunctioning"
    else:
        fault = "Unknown"
        situation = "Unknown"

    return {
        "Location": location_name if location_name else "Unknown",
        "Fault": fault,
        "Situation": situation,
    }


def main():
    parser = argparse.ArgumentParser(description="Identify civic infrastructure issues.")
    parser.add_argument("--location", default="", help="Location name reported by the user")
    parser.add_argument("--description", default="", help="Description of the civic issue")
    args = parser.parse_args()

    result = classify_civic_issue(args.location, args.description)
    print(result)


if __name__ == "__main__":
    main()
