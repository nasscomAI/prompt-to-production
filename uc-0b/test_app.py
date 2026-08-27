"""Tests for app.py — retrieve_policy and summarize_policy skills."""
import os
import tempfile
import unittest

from app import retrieve_policy, summarize_policy, main


SAMPLE_POLICY = """\
CITY MUNICIPAL CORPORATION
HUMAN RESOURCES DEPARTMENT

═══════════════════════════════════════════════════════════
1. PURPOSE AND SCOPE
═══════════════════════════════════════════════════════════
1.1 This policy governs all leave entitlements for permanent and
    contractual employees of the City Municipal Corporation (CMC).

═══════════════════════════════════════════════════════════
2. ANNUAL LEAVE
═══════════════════════════════════════════════════════════
2.1 Each permanent employee is entitled to 18 days of paid annual
    leave per calendar year.
2.2 Annual leave accrues at 1.5 days per month.
2.3 Employees must submit a leave application at least 14 calendar
    days in advance.
"""


class TestRetrievePolicy(unittest.TestCase):

    def test_retrieves_numbered_clauses(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write(SAMPLE_POLICY)
            fpath = f.name
        try:
            result = retrieve_policy(fpath)
            self.assertEqual(len(result), 4)
            self.assertEqual(result[0]["clause_id"], "1.1")
            self.assertIn("governs all leave entitlements", result[0]["text"])
            self.assertEqual(result[1]["clause_id"], "2.1")
            self.assertIn("18 days", result[1]["text"])
            self.assertEqual(result[2]["clause_id"], "2.2")
            self.assertIn("1.5 days", result[2]["text"])
            self.assertEqual(result[3]["clause_id"], "2.3")
            self.assertIn("14 calendar", result[3]["text"])
        finally:
            os.unlink(fpath)

    def test_empty_file_returns_empty_list(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            fpath = f.name
        try:
            result = retrieve_policy(fpath)
            self.assertEqual(result, [])
        finally:
            os.unlink(fpath)

    def test_file_not_found_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            retrieve_policy("nonexistent_file_xyz.txt")

    def test_no_numbered_clauses_returns_raw(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("Some plain text without any numbered clauses.")
            fpath = f.name
        try:
            result = retrieve_policy(fpath)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["clause_id"], "raw")
        finally:
            os.unlink(fpath)


class TestSummarizePolicy(unittest.TestCase):

    def test_empty_clauses_returns_message(self):
        result = summarize_policy([])
        self.assertIn("no clauses to summarise", result)

    def test_summary_includes_all_clauses(self):
        clauses = [
            {"clause_id": "2.3", "text": "Employees must submit leave 14 days in advance."},
            {"clause_id": "5.2", "text": "LWP requires approval from Department Head and HR Director."},
        ]
        result = summarize_policy(clauses)
        self.assertIn("Clause 2.3", result)
        self.assertIn("14 days in advance", result)
        self.assertIn("Clause 5.2", result)
        self.assertIn("Department Head and HR Director", result)

    def test_raw_clause_is_flagged(self):
        clauses = [{"clause_id": "raw", "text": "Unstructured content."}]
        result = summarize_policy(clauses)
        self.assertIn("FLAGGED", result)
        self.assertIn("Unstructured content.", result)

    def test_no_extraneous_content_added(self):
        clauses = [
            {"clause_id": "2.6", "text": "Max 5 days carry-forward."},
        ]
        result = summarize_policy(clauses)
        self.assertNotIn("standard practice", result.lower())
        self.assertNotIn("typically", result.lower())
        self.assertNotIn("generally", result.lower())


class TestMain(unittest.TestCase):

    def test_main_writes_output_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as inf:
            inf.write(SAMPLE_POLICY)
            inpath = inf.name
        outpath = os.path.join(
            tempfile.gettempdir(), "test_summary_output.txt"
        )
        try:
            import sys
            old_argv = sys.argv
            sys.argv = ["app.py", "--input", inpath, "--output", outpath]
            try:
                main()
                self.assertTrue(os.path.exists(outpath))
                with open(outpath, encoding="utf-8") as f:
                    content = f.read()
                self.assertIn("Clause 1.1", content)
                self.assertIn("Clause 2.1", content)
                self.assertIn("Clause 2.2", content)
                self.assertIn("Clause 2.3", content)
            finally:
                sys.argv = old_argv
        finally:
            os.unlink(inpath)
            if os.path.exists(outpath):
                os.unlink(outpath)


if __name__ == "__main__":
    unittest.main()
