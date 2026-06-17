import sys
import pathlib
import csv


# Ensure the uc-0a directory is importable
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import classifier


def test_classify_missing_description():
    row = {"complaint_id": "T1", "description": ""}
    res = classifier.classify_complaint(row)
    assert res["category"] == "Other"
    assert res["priority"] == "Standard"
    assert res["flag"] == "NEEDS_REVIEW"
    assert "No description" in res["reason"]


def test_severity_triggers_urgent():
    row = {"complaint_id": "T2", "description": "Child injured near school, needs ambulance to hospital"}
    res = classifier.classify_complaint(row)
    assert res["priority"] == "Urgent"
    # reason should cite at least one severity word
    assert any(w in res["reason"] for w in ["'child'", "'hospital'", "'ambulance'", "'school'", "'injury'", "'fell'"])


def test_category_exactness():
    row = {"complaint_id": "T3", "description": "Large pothole on the main road causing tyre punctures."}
    res = classifier.classify_complaint(row)
    assert res["category"] == "Pothole"


def test_ambiguity_flags():
    # mentions both waste and heritage
    row = {"complaint_id": "T4", "description": "Garbage dumped near the heritage monument causing stains"}
    res = classifier.classify_complaint(row)
    assert res["flag"] == "NEEDS_REVIEW"
    # reason should mention at least one of the keywords
    assert "'waste'" in res["reason"] or "'garbage'" in res["reason"] or "'heritage'" in res["reason"]


def test_batch_classify_writes_output(tmp_path):
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"

    rows = [
        {
            "complaint_id": "B1",
            "date_raised": "2024-01-01",
            "city": "TestCity",
            "ward": "Ward 1",
            "location": "Loc A",
            "description": "Large pothole near market",
            "reported_by": "Portal",
            "days_open": "1",
        },
        {
            "complaint_id": "B2",
            "date_raised": "2024-01-02",
            "city": "TestCity",
            "ward": "Ward 2",
            "location": "Loc B",
            "description": "Streetlight out and a child fell",
            "reported_by": "Phone",
            "days_open": "2",
        },
    ]

    with open(input_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    classifier.batch_classify(str(input_file), str(output_file))

    # verify output exists and has two data rows
    with open(output_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        out_rows = list(reader)
    assert len(out_rows) == 2
    # ensure categories are exact strings
    for r in out_rows:
        assert r["category"] in classifier.ALLOWED_CATEGORIES
