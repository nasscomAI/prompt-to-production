"""Comprehensive failure and edge case tests for UC-0B Policy Summarizer."""
import os
import sys
import tempfile
import shutil

# Import functions from app.py
sys.path.insert(0, os.path.dirname(__file__))
from app import retrieve_policy, summarize_policy

TEST_DIR = tempfile.mkdtemp()

def cleanup():
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

def write_test_file(name, content):
    path = os.path.join(TEST_DIR, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return path

def test_file_not_found():
    """Edge Case 1: File does not exist."""
    print("TEST 1: File not found")
    try:
        retrieve_policy("nonexistent_file.txt")
        print("  FAIL: Should have raised FileNotFoundError")
        return False
    except FileNotFoundError:
        print("  PASS: FileNotFoundError raised correctly")
        return True

def test_empty_file():
    """Edge Case 2: Empty file."""
    print("TEST 2: Empty file")
    path = write_test_file("empty.txt", "")
    result = retrieve_policy(path)
    if result == []:
        print("  PASS: Empty list returned for empty file")
        return True
    else:
        print(f"  FAIL: Expected empty list, got {result}")
        return False

def test_no_numbered_clauses():
    """Edge Case 3: File with no numbered clauses."""
    print("TEST 3: No numbered clauses")
    path = write_test_file("no_clauses.txt", "This is a policy document without any numbered clauses.")
    result = retrieve_policy(path)
    if len(result) == 0:
        print("  PASS: No sections returned for unnumbered content")
        return True
    else:
        print(f"  FAIL: Expected 0 sections, got {len(result)}")
        return False

def test_single_clause():
    """Edge Case 4: Single clause document."""
    print("TEST 4: Single clause")
    path = write_test_file("single.txt", "1. POLICY\n1.1 This is the only clause.")
    result = retrieve_policy(path)
    if len(result) == 1 and len(result[0]["clauses"]) == 1:
        print("  PASS: Single clause parsed correctly")
        return True
    else:
        print(f"  FAIL: Expected 1 section with 1 clause, got {len(result)} sections")
        return False

def test_summary_empty_input():
    """Edge Case 5: summarize_policy with empty input."""
    print("TEST 5: Summarize empty input")
    result = summarize_policy([])
    if result == "No policy content to summarize.":
        print("  PASS: Refusal message returned for empty input")
        return True
    else:
        print(f"  FAIL: Expected refusal message, got '{result}'")
        return False

def test_clause_5_2_trap():
    """Edge Case 6: Clause 5.2 two approvers trap."""
    print("TEST 6: Clause 5.2 trap (two approvers)")
    path = write_test_file("trap.txt", "5. LWP\n5.2 LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.")
    sections = retrieve_policy(path)
    summary = summarize_policy(sections)
    has_dept = "Department Head" in summary
    has_hr = "HR Director" in summary
    has_and = "Department Head and" in summary
    if has_dept and has_hr and has_and:
        print("  PASS: Both approvers preserved with AND condition")
        return True
    else:
        print(f"  FAIL: Dept={has_dept}, HR={has_hr}, AND={has_and}")
        return False

def test_scope_bleed_prevention():
    """Edge Case 7: No scope bleed phrases added."""
    print("TEST 7: Scope bleed prevention")
    path = write_test_file("scope.txt", "1. POLICY\n1.1 Employees must submit forms on time.")
    sections = retrieve_policy(path)
    summary = summarize_policy(sections)
    bleed_phrases = ["as is standard", "generally expected", "typically"]
    found = [p for p in bleed_phrases if p in summary.lower()]
    if not found:
        print("  PASS: No scope bleed phrases found")
        return True
    else:
        print(f"  FAIL: Found scope bleed phrases: {found}")
        return False

def test_clause_numbering_preserved():
    """Edge Case 8: Clause numbering preserved in output."""
    print("TEST 8: Clause numbering preserved")
    path = write_test_file("numbering.txt", "2. LEAVE\n2.1 First clause.\n2.2 Second clause.\n2.3 Third clause.")
    sections = retrieve_policy(path)
    summary = summarize_policy(sections)
    has_21 = "2.1" in summary
    has_22 = "2.2" in summary
    has_23 = "2.3" in summary
    if has_21 and has_22 and has_23:
        print("  PASS: All clause numbers preserved")
        return True
    else:
        print(f"  FAIL: Missing clause numbers: 2.1={has_21}, 2.2={has_22}, 2.3={has_23}")
        return False

def test_real_policy():
    """Edge Case 9: Real policy document (full run)."""
    print("TEST 9: Real policy document")
    real_path = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents", "policy_hr_leave.txt")
    if not os.path.exists(real_path):
        print("  SKIP: Real policy file not found")
        return True
    try:
        sections = retrieve_policy(real_path)
        summary = summarize_policy(sections)
        critical = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
        missing = [c for c in critical if c not in summary]
        if not missing:
            print("  PASS: All 10 critical clauses present")
            return True
        else:
            print(f"  FAIL: Missing clauses: {missing}")
            return False
    except Exception as e:
        print(f"  FAIL: Exception: {e}")
        return False

def test_multi_section_document():
    """Edge Case 10: Multiple sections with multiple clauses."""
    print("TEST 10: Multi-section document")
    content = """1. SECTION ONE
1.1 First clause of section one.
1.2 Second clause of section one.

2. SECTION TWO
2.1 First clause of section two.
2.2 Second clause of section two.
2.3 Third clause of section two.

3. SECTION THREE
3.1 Only clause in section three."""
    path = write_test_file("multi.txt", content)
    sections = retrieve_policy(path)
    if len(sections) == 3:
        clause_counts = [len(s["clauses"]) for s in sections]
        if clause_counts == [2, 3, 1]:
            print("  PASS: Multi-section parsed correctly")
            return True
        else:
            print(f"  FAIL: Clause counts: {clause_counts}")
            return False
    else:
        print(f"  FAIL: Expected 3 sections, got {len(sections)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("UC-0B FAILURE & EDGE CASE TESTS")
    print("=" * 60)
    print()

    results = []
    results.append(test_file_not_found())
    results.append(test_empty_file())
    results.append(test_no_numbered_clauses())
    results.append(test_single_clause())
    results.append(test_summary_empty_input())
    results.append(test_clause_5_2_trap())
    results.append(test_scope_bleed_prevention())
    results.append(test_clause_numbering_preserved())
    results.append(test_real_policy())
    results.append(test_multi_section_document())

    cleanup()

    print()
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    if passed == total:
        print(f"RESULT: ALL {total} TESTS PASSED")
        sys.exit(0)
    else:
        print(f"RESULT: {passed}/{total} tests passed, {total - passed} failed")
        sys.exit(1)
