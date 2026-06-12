"""
Tests for app.py — UC-0C Municipal Budget Growth Analyst

Covers:
  - load_dataset: happy path, missing file, missing columns, null reporting
  - compute_growth: reference values, null flagging, invalid growth_type,
    invalid ward/category, prior period null, first period (no prior)
  - Enforcement: no aggregation across wards, no guessing growth_type
"""

import csv
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(__file__))
from app import load_dataset, compute_growth, _prior_period

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FIELDNAMES = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def _write_csv(rows, fieldnames=None, suffix=".csv"):
    """Write rows to a temp CSV and return the path."""
    if fieldnames is None:
        fieldnames = FIELDNAMES
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=suffix, delete=False, encoding="utf-8", newline=""
    )
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    f.close()
    return f.name


def _kasba_roads_rows():
    """12 months of Ward 1 – Kasba / Roads & Pothole Repair with 2024-11 Waste Mgmt null included."""
    return [
        {"period": "2024-01", "ward": "Ward 1 – Kasba", "category": "Roads & Pothole Repair", "budgeted_amount": "14.0", "actual_spend": "13.3", "notes": ""},
        {"period": "2024-02", "ward": "Ward 1 – Kasba", "category": "Roads & Pothole Repair", "budgeted_amount": "14.0", "actual_spend": "12.2", "notes": ""},
        {"period": "2024-03", "ward": "Ward 1 – Kasba", "category": "Roads & Pothole Repair", "budgeted_amount": "14.0", "actual_spend": "12.3", "notes": ""},
        {"period": "2024-04", "ward": "Ward 1 – Kasba", "category": "Roads & Pothole Repair", "budgeted_amount": "14.0", "actual_spend": "13.4", "notes": ""},
        {"period": "2024-05", "ward": "Ward 1 – Kasba", "category": "Roads & Pothole Repair", "budgeted_amount": "14.0", "actual_spend": "14.1", "notes": ""},
        {"period": "2024-06", "ward": "Ward 1 – Kasba", "category": "Roads & Pothole Repair", "budgeted_amount": "14.0", "actual_spend": "14.8", "notes": ""},
        {"period": "2024-07", "ward": "Ward 1 – Kasba", "category": "Roads & Pothole Repair", "budgeted_amount": "20.0", "actual_spend": "19.7", "notes": "monsoon spike"},
        {"period": "2024-08", "ward": "Ward 1 – Kasba", "category": "Roads & Pothole Repair", "budgeted_amount": "20.0", "actual_spend": "20.2", "notes": ""},
        {"period": "2024-09", "ward": "Ward 1 – Kasba", "category": "Roads & Pothole Repair", "budgeted_amount": "20.0", "actual_spend": "20.1", "notes": ""},
        {"period": "2024-10", "ward": "Ward 1 – Kasba", "category": "Roads & Pothole Repair", "budgeted_amount": "14.0", "actual_spend": "13.1", "notes": "post-monsoon"},
        {"period": "2024-11", "ward": "Ward 1 – Kasba", "category": "Roads & Pothole Repair", "budgeted_amount": "14.0", "actual_spend": "14.2", "notes": ""},
        {"period": "2024-12", "ward": "Ward 1 – Kasba", "category": "Roads & Pothole Repair", "budgeted_amount": "14.0", "actual_spend": "12.7", "notes": ""},
    ]


def _rows_with_null():
    """Minimal dataset containing one null actual_spend row."""
    return [
        {"period": "2024-01", "ward": "Ward 2 – Shivajinagar", "category": "Drainage & Flooding", "budgeted_amount": "10.0", "actual_spend": "9.5", "notes": ""},
        {"period": "2024-02", "ward": "Ward 2 – Shivajinagar", "category": "Drainage & Flooding", "budgeted_amount": "10.0", "actual_spend": "10.1", "notes": ""},
        {"period": "2024-03", "ward": "Ward 2 – Shivajinagar", "category": "Drainage & Flooding", "budgeted_amount": "10.0", "actual_spend": "",  "notes": "Data not submitted by ward office"},
        {"period": "2024-04", "ward": "Ward 2 – Shivajinagar", "category": "Drainage & Flooding", "budgeted_amount": "10.0", "actual_spend": "10.5", "notes": ""},
    ]


# ---------------------------------------------------------------------------
# load_dataset — happy path
# ---------------------------------------------------------------------------

class TestLoadDatasetHappyPath:
    def test_returns_all_rows(self):
        path = _write_csv(_kasba_roads_rows())
        rows, _ = load_dataset(path)
        os.unlink(path)
        assert len(rows) == 12

    def test_null_report_empty_when_no_nulls(self):
        path = _write_csv(_kasba_roads_rows())
        _, null_report = load_dataset(path)
        os.unlink(path)
        assert null_report == []

    def test_null_report_identifies_null_rows(self):
        path = _write_csv(_rows_with_null())
        _, null_report = load_dataset(path)
        os.unlink(path)
        assert len(null_report) == 1
        entry = null_report[0]
        assert entry["period"] == "2024-03"
        assert entry["ward"] == "Ward 2 – Shivajinagar"
        assert entry["category"] == "Drainage & Flooding"

    def test_null_report_includes_reason_from_notes(self):
        path = _write_csv(_rows_with_null())
        _, null_report = load_dataset(path)
        os.unlink(path)
        assert "Data not submitted by ward office" in null_report[0]["reason"]

    def test_null_reason_unavailable_when_notes_also_empty(self):
        rows = _rows_with_null()
        rows[2]["notes"] = ""  # clear the reason
        path = _write_csv(rows)
        _, null_report = load_dataset(path)
        os.unlink(path)
        assert null_report[0]["reason"] == "null reason unavailable"

    def test_null_rows_not_dropped_from_dataset(self):
        path = _write_csv(_rows_with_null())
        rows, _ = load_dataset(path)
        os.unlink(path)
        # All 4 rows including the null one must be present
        assert len(rows) == 4
        null_rows = [r for r in rows if r["actual_spend"] == ""]
        assert len(null_rows) == 1


# ---------------------------------------------------------------------------
# load_dataset — error conditions
# ---------------------------------------------------------------------------

class TestLoadDatasetErrors:
    def test_missing_file_exits(self):
        with pytest.raises(SystemExit):
            load_dataset("/nonexistent/path/ward_budget.csv")

    def test_missing_column_exits(self):
        # Write CSV without the 'notes' column
        rows = [{"period": "2024-01", "ward": "W1", "category": "C1",
                 "budgeted_amount": "10.0", "actual_spend": "9.0"}]
        fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend"]
        path = _write_csv(rows, fieldnames=fieldnames)
        with pytest.raises(SystemExit):
            load_dataset(path)
        os.unlink(path)

    def test_multiple_missing_columns_reported(self):
        rows = [{"period": "2024-01", "ward": "W1"}]
        path = _write_csv(rows, fieldnames=["period", "ward"])
        with pytest.raises(SystemExit) as exc_info:
            load_dataset(path)
        os.unlink(path)
        assert "missing" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# compute_growth — reference values (enforcement: formula + correct numbers)
# ---------------------------------------------------------------------------

class TestComputeGrowthReferenceValues:
    def setup_method(self):
        self.rows = _kasba_roads_rows()

    def test_2024_07_mom_growth_is_plus_33_1(self):
        result = compute_growth(self.rows, "Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        row = next(r for r in result if r["period"] == "2024-07")
        assert row["growth_pct"] == 33.1

    def test_2024_10_mom_growth_is_minus_34_8(self):
        result = compute_growth(self.rows, "Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        row = next(r for r in result if r["period"] == "2024-10")
        assert row["growth_pct"] == -34.8

    def test_formula_shown_for_every_computed_row(self):
        result = compute_growth(self.rows, "Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        computed = [r for r in result if isinstance(r["growth_pct"], float)]
        for row in computed:
            assert "×" in row["formula"] or "x" in row["formula"].lower(), \
                f"Formula missing for period {row['period']}: {row['formula']}"

    def test_formula_contains_actual_values(self):
        result = compute_growth(self.rows, "Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        row = next(r for r in result if r["period"] == "2024-07")
        assert "19.7" in row["formula"]
        assert "14.8" in row["formula"]

    def test_first_period_has_no_prior_period(self):
        result = compute_growth(self.rows, "Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        row = next(r for r in result if r["period"] == "2024-01")
        assert "NOT COMPUTED" in str(row["growth_pct"])

    def test_output_has_12_rows(self):
        result = compute_growth(self.rows, "Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        assert len(result) == 12

    def test_output_sorted_by_period(self):
        result = compute_growth(self.rows, "Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        periods = [r["period"] for r in result]
        assert periods == sorted(periods)


# ---------------------------------------------------------------------------
# compute_growth — null flagging (enforcement rules 2 & 5)
# ---------------------------------------------------------------------------

class TestComputeGrowthNullFlagging:
    def test_null_row_is_not_skipped(self):
        rows = _rows_with_null()
        result = compute_growth(rows, "Ward 2 – Shivajinagar", "Drainage & Flooding", "MoM")
        periods = [r["period"] for r in result]
        assert "2024-03" in periods

    def test_null_row_growth_pct_is_not_computed(self):
        rows = _rows_with_null()
        result = compute_growth(rows, "Ward 2 – Shivajinagar", "Drainage & Flooding", "MoM")
        row = next(r for r in result if r["period"] == "2024-03")
        assert "NOT COMPUTED" in str(row["growth_pct"])

    def test_null_row_actual_spend_shows_flag_and_reason(self):
        rows = _rows_with_null()
        result = compute_growth(rows, "Ward 2 – Shivajinagar", "Drainage & Flooding", "MoM")
        row = next(r for r in result if r["period"] == "2024-03")
        assert "NULL" in str(row["actual_spend"])
        assert "Data not submitted" in str(row["actual_spend"])

    def test_prior_period_null_flags_downstream_row(self):
        """When prior period is null, the next period's growth must be NOT COMPUTED."""
        rows = _rows_with_null()
        result = compute_growth(rows, "Ward 2 – Shivajinagar", "Drainage & Flooding", "MoM")
        row = next(r for r in result if r["period"] == "2024-04")
        assert "NOT COMPUTED" in str(row["growth_pct"])

    def test_null_rows_not_imputed(self):
        rows = _rows_with_null()
        result = compute_growth(rows, "Ward 2 – Shivajinagar", "Drainage & Flooding", "MoM")
        null_row = next(r for r in result if r["period"] == "2024-03")
        # actual_spend must not be a numeric float
        assert not isinstance(null_row["actual_spend"], float)


# ---------------------------------------------------------------------------
# compute_growth — enforcement: invalid inputs & refusals
# ---------------------------------------------------------------------------

class TestComputeGrowthEnforcement:
    def setup_method(self):
        self.rows = _kasba_roads_rows()

    def test_invalid_growth_type_exits(self):
        with pytest.raises(SystemExit):
            compute_growth(self.rows, "Ward 1 – Kasba", "Roads & Pothole Repair", "QoQ")

    def test_none_growth_type_exits(self):
        with pytest.raises(SystemExit):
            compute_growth(self.rows, "Ward 1 – Kasba", "Roads & Pothole Repair", None)

    def test_empty_growth_type_exits(self):
        with pytest.raises(SystemExit):
            compute_growth(self.rows, "Ward 1 – Kasba", "Roads & Pothole Repair", "")

    def test_unknown_ward_exits(self):
        with pytest.raises(SystemExit):
            compute_growth(self.rows, "Ward 99 – Unknown", "Roads & Pothole Repair", "MoM")

    def test_unknown_ward_error_lists_valid_options(self):
        with pytest.raises(SystemExit) as exc_info:
            compute_growth(self.rows, "Ward 99 – Unknown", "Roads & Pothole Repair", "MoM")
        assert "Ward 1" in str(exc_info.value)

    def test_unknown_category_exits(self):
        with pytest.raises(SystemExit):
            compute_growth(self.rows, "Ward 1 – Kasba", "Nonexistent Category", "MoM")

    def test_unknown_category_error_lists_valid_options(self):
        with pytest.raises(SystemExit) as exc_info:
            compute_growth(self.rows, "Ward 1 – Kasba", "Nonexistent Category", "MoM")
        assert "Roads" in str(exc_info.value)


# ---------------------------------------------------------------------------
# _prior_period — unit tests
# ---------------------------------------------------------------------------

class TestPriorPeriod:
    def test_mom_february(self):
        assert _prior_period("2024-02", "MoM") == "2024-01"

    def test_mom_january_wraps_to_december(self):
        assert _prior_period("2024-01", "MoM") == "2023-12"

    def test_yoy(self):
        assert _prior_period("2024-07", "YoY") == "2023-07"

    def test_mom_december(self):
        assert _prior_period("2024-12", "MoM") == "2024-11"
