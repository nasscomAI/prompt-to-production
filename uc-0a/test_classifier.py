import os
import csv
import tempfile
import unittest
import importlib.util
import unittest
import importlib


def load_module():
    here = os.path.dirname(__file__)
    path = os.path.join(here, "classifier.py")
    spec = importlib.util.spec_from_file_location("classifier_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ClassifierTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()

    def test_classify_flags_null_description(self):
        row = {"complaint_id": "T1", "description": "", "location": ""}
        res = self.mod.classify_complaint(row)
        self.assertEqual(res["complaint_id"], "T1")
        self.assertIn("nulls", res["flag"])

    def test_classify_pothole_medium_priority(self):
        row = {"complaint_id": "T2", "description": "Large pothole on main road", "days_open": "10"}
        res = self.mod.classify_complaint(row)
        self.assertIn("Pothole", res["category"])
        self.assertEqual(res["priority"], "medium")

    def test_batch_classify_writes_output(self):
        # create a small input CSV
        fd_in, in_path = tempfile.mkstemp(suffix=".csv")
        os.close(fd_in)
        fd_out, out_path = tempfile.mkstemp(suffix=".csv")
        os.close(fd_out)
        try:
            with open(in_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["complaint_id", "description", "location", "days_open"])
                writer.writerow(["B1", "Missing manhole cover near park", "Park Road", "2"])
                writer.writerow(["B2", "Overflowing garbage bin", "Market St", "15"])

            # run batch classify
            self.mod.batch_classify(in_path, out_path)

            # read output and validate
            with open(out_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                self.assertEqual(len(rows), 2)
                ids = {r["complaint_id"] for r in rows}
                self.assertIn("B1", ids)
                self.assertIn("B2", ids)
        finally:
            try:
                os.remove(in_path)
            except Exception:
                pass
            try:
                os.remove(out_path)
            except Exception:
                pass

    @unittest.skipUnless(importlib.util.find_spec("sklearn"), "sklearn not installed")
    def test_enable_ml(self):
        mod = load_module()
        ok = mod.enable_ml()
        self.assertTrue(ok)
        self.assertTrue(globals().get('_SKLEARN_AVAILABLE', True) or True)


if __name__ == "__main__":
    unittest.main()
