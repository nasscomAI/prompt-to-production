import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from classifier import classify_complaint


def test_classify_complaint_detects_streetlight_and_urgent_priority():
    row = {
        "complaint_id": "PM-202411",
        "description": "Streetlight flickering and sparking. Electrical hazard reported.",
    }

    result = classify_complaint(row)

    assert result["complaint_id"] == "PM-202411"
    assert result["category"] == "Streetlight"
    assert result["priority"] == "Urgent"
    assert result["flag"] == ""
    assert "Streetlight" in result["reason"] or "streetlight" in result["reason"]
    assert "hazard" in result["reason"].lower()
