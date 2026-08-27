"""Proper crash detection — separates 'handled' from 'swallowed'."""
import os
import sys
import subprocess
import tempfile
import traceback

sys.path.insert(0, os.path.dirname(__file__))
from app import retrieve_policy, summarize_policy

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
WARN = "\033[93mWARN\033[0m"
RESULTS = []


def check(name, expected_graceful, actual_fn):
    """Test if code crashes or handles gracefully."""
    print(f"TEST: {name}")
    try:
        actual_fn()
        if expected_graceful:
            print(f"  {PASS}: No crash\n")
            RESULTS.append((name, True, "clean"))
        else:
            print(f"  {WARN}: Expected crash but none occurred\n")
            RESULTS.append((name, True, "unexpected_clean"))
    except FileNotFoundError as e:
        print(f"  {PASS}: FileNotFoundError — {e}\n")
        RESULTS.append((name, True, "graceful"))
    except PermissionError as e:
        print(f"  {PASS}: PermissionError — {e}\n")
        RESULTS.append((name, True, "graceful"))
    except TypeError as e:
        print(f"  {FAIL}: TypeError CRASH — {e}")
        print(f"  Fix: Add type check in summarize_policy()\n")
        RESULTS.append((name, False, "crash"))
    except KeyError as e:
        print(f"  {FAIL}: KeyError CRASH — {e}")
        print(f"  Fix: Add .get() or key validation in summarize_policy()\n")
        RESULTS.append((name, False, "crash"))
    except Exception as e:
        print(f"  {FAIL}: {type(e).__name__} CRASH — {e}\n")
        RESULTS.append((name, False, "crash"))


if __name__ == "__main__":
    print("=" * 60)
    print("UC-0B CRASH DETECTION (no silent catches)")
    print("=" * 60 + "\n")

    # --- retrieve_policy tests ---
    real_input = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents", "policy_hr_leave.txt")

    check("retrieve: nonexistent file", True,
          lambda: retrieve_policy("ghost.txt"))

    check("retrieve: directory not file", True,
          lambda: retrieve_policy(os.path.dirname(__file__)))

    tmp_bin = tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="wb")
    tmp_bin.write(b"\x00\x01\x02")
    tmp_bin.close()
    check("retrieve: binary file (UnicodeDecodeError expected)", True,
          lambda: retrieve_policy(tmp_bin.name))
    os.unlink(tmp_bin.name)

    tmp_ok = tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8")
    tmp_ok.write("1. SEC\n1.1 Clause.\n")
    tmp_ok.close()
    check("retrieve: valid small file", True,
          lambda: retrieve_policy(tmp_ok.name))
    os.unlink(tmp_ok.name)

    # --- summarize_policy type safety ---
    check("summarize: None input", True,
          lambda: summarize_policy(None))

    check("summarize: dict instead of list", False,
          lambda: summarize_policy({"section_number": "1"}))

    check("summarize: list of dicts missing 'section_number'", False,
          lambda: summarize_policy([{"bad": "data"}]))

    check("summarize: sections with clauses missing 'clause_id'", False,
          lambda: summarize_policy([{"section_number": "1", "section_title": "X", "clauses": [{"bad": 1}]}]))

    check("summarize: valid input", True,
          lambda: summarize_policy([{"section_number": "1", "section_title": "X", "clauses": [{"clause_id": "1.1", "clause_text": "Text."}]}]))

    # --- main() subprocess tests ---
    def run_main(*args):
        result = subprocess.run(
            [sys.executable, "app.py"] + list(args),
            capture_output=True, text=True, cwd=os.path.dirname(__file__) or "."
        )
        return result

    print("TEST: main() with no args")
    r = run_main()
    if r.returncode != 0 and "error" in r.stderr.lower():
        print(f"  {PASS}: argparse error shown\n")
        RESULTS.append(("main: no args", True, "graceful"))
    else:
        print(f"  {FAIL}: No error shown\n")
        RESULTS.append(("main: no args", False, "crash"))

    print("TEST: main() with nonexistent input file")
    r = run_main("--input", "ghost.txt", "--output", "out.txt")
    if r.returncode != 0:
        print(f"  {PASS}: Error exit code {r.returncode}\n")
        RESULTS.append(("main: ghost input", True, "graceful"))
    else:
        print(f"  {FAIL}: Exited with code 0 on bad input\n")
        RESULTS.append(("main: ghost input", False, "crash"))

    print("TEST: main() shows friendly or raw error on bad input")
    r = run_main("--input", "ghost.txt", "--output", "out.txt")
    has_traceback = "Traceback" in r.stderr
    if has_traceback:
        print(f"  {WARN}: Raw Python traceback shown (not user-friendly)\n")
        RESULTS.append(("main: error style", True, "raw_traceback"))
    else:
        print(f"  {PASS}: No raw traceback\n")
        RESULTS.append(("main: error style", True, "clean"))

    # --- Summary ---
    print("=" * 60)
    crashes = [(n, t) for n, p, t in RESULTS if not p]
    graceful = [(n, t) for n, p, t in RESULTS if p]
    raw_tb = [(n, t) for n, p, t in RESULTS if t == "raw_traceback"]

    print(f"  Total tests:     {len(RESULTS)}")
    print(f"  Handled gracefully: {len(graceful)}")
    print(f"  CRASHES:           {len(crashes)}")
    print()

    if crashes:
        print("CRASHES TO FIX:")
        for n, t in crashes:
            print(f"  {FAIL} {n}")
        print()

    if raw_tb:
        print("WARNINGS (raw traceback not user-friendly):")
        for n, t in raw_tb:
            print(f"  {WARN} {n}")
        print()

    if not crashes and not raw_tb:
        print(f"  {PASS} ALL CLEAN — no crashes, no raw tracebacks")
    print("=" * 60)
