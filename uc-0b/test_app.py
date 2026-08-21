import json

from app import classify_civic_issue


def test_streetlight_report():
    result = classify_civic_issue(
        "Main Road, Ward 2",
        "Streetlight is not working and the road is dark at night.",
    )
    assert result["Location"] == "Main Road, Ward 2"
    assert result["Fault"] == "Streetlight"
    assert result["Situation"] == "light is not working"


def test_traffic_signal_report():
    result = classify_civic_issue(
        "Traffic junction near City Center",
        "Traffic signal is malfunctioning and the red light stays on continuously.",
    )
    assert result["Location"] == "Traffic junction near City Center"
    assert result["Fault"] == "Traffic Signal"
    assert result["Situation"] == "signal is malfunctioning"


def test_unknown_report_when_evidence_missing():
    result = classify_civic_issue("Somewhere", "The area looks unsafe.")
    assert result["Location"] == "Somewhere"
    assert result["Fault"] == "Unknown"
    assert result["Situation"] == "Unknown"
