import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("uc0c_app", ROOT / "app.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class UC0CAppTests(unittest.TestCase):
    def test_compute_growth_marks_null_rows_and_writes_csv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = ROOT.parent / "data" / "budget" / "ward_budget.csv"
            output_path = Path(temp_dir) / "growth_output.csv"

            result = MODULE.run_pipeline(
                input_path=str(input_path),
                ward="Ward 1 – Kasba",
                category="Roads & Pothole Repair",
                growth_type="MoM",
                output_path=str(output_path),
            )

            self.assertTrue(output_path.exists())
            self.assertEqual(result["ward"], "Ward 1 – Kasba")
            self.assertEqual(result["category"], "Roads & Pothole Repair")
            self.assertEqual(result["growth_type"], "MoM")

            with output_path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

            self.assertGreater(len(rows), 0)
            self.assertIn("formula", rows[0])
            self.assertIn("status", rows[0])
            self.assertIn("notes", rows[0])


if __name__ == "__main__":
    unittest.main()
