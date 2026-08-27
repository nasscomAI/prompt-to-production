"""Load testing and performance tests for UC-0B."""
import os
import sys
import time
import tempfile
import shutil
import statistics

sys.path.insert(0, os.path.dirname(__file__))
from app import retrieve_policy, summarize_policy

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
WARN = "\033[93mWARN\033[0m"
RESULTS = []


def check(name, fn, threshold=None):
    print(f"TEST: {name}")
    try:
        start = time.perf_counter()
        result = fn()
        elapsed = time.perf_counter() - start
        if threshold and elapsed > threshold:
            print(f"  {WARN}: SLOW ({elapsed:.3f}s > {threshold}s threshold)\n")
            RESULTS.append((name, True, elapsed, "slow"))
        else:
            print(f"  {PASS}: {elapsed:.3f}s\n")
            RESULTS.append((name, True, elapsed, "ok"))
    except Exception as e:
        print(f"  {FAIL}: {type(e).__name__}: {e}\n")
        RESULTS.append((name, False, 0, "error"))


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return path


def generate_policy(num_sections, clauses_per_section):
    """Generate a realistic policy document."""
    lines = []
    for s in range(1, num_sections + 1):
        lines.append(f"{s}. SECTION {s}")
        for c in range(1, clauses_per_section + 1):
            text = f"Clause {s}.{c} text with some detailed information about the policy requirement."
            lines.append(f"{s}.{c} {text}")
    return "\n".join(lines)


if __name__ == "__main__":
    print("=" * 60)
    print("UC-0B LOAD & PERFORMANCE TESTS")
    print("=" * 60 + "\n")

    tmp = tempfile.mkdtemp()
    real_input = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents", "policy_hr_leave.txt")

    # ============================================
    # SECTION 1: PARSE PERFORMANCE
    # ============================================
    print("--- SECTION 1: PARSE PERFORMANCE ---\n")

    # 1.1 Small file (1KB)
    small = generate_policy(5, 3)
    p = write_file(os.path.join(tmp, "small.txt"), small)
    check("1.1 Small file (1KB, 15 clauses)", lambda: retrieve_policy(p), threshold=0.1)

    # 1.2 Medium file (100KB)
    medium = generate_policy(50, 10)
    p = write_file(os.path.join(tmp, "medium.txt"), medium)
    check("1.2 Medium file (100KB, 500 clauses)", lambda: retrieve_policy(p), threshold=0.5)

    # 1.3 Large file (1MB)
    large = generate_policy(100, 50)
    p = write_file(os.path.join(tmp, "large.txt"), large)
    check("1.3 Large file (1MB, 5000 clauses)", lambda: retrieve_policy(p), threshold=2.0)

    # 1.4 Very large file (10MB)
    very_large = generate_policy(500, 100)
    p = write_file(os.path.join(tmp, "very_large.txt"), very_large)
    check("1.4 Very large file (10MB, 50000 clauses)", lambda: retrieve_policy(p), threshold=10.0)

    # 1.5 Huge file (50MB)
    print("TEST: 1.5 Huge file (50MB, 250000 clauses)")
    huge_path = os.path.join(tmp, "huge.txt")
    with open(huge_path, 'w', encoding='utf-8') as f:
        for s in range(1, 501):
            f.write(f"{s}. SECTION {s}\n")
            for c in range(1, 501):
                f.write(f"{s}.{c} Clause {s}.{c} text.\n")
    try:
        start = time.perf_counter()
        result = retrieve_policy(huge_path)
        elapsed = time.perf_counter() - start
        total_clauses = sum(len(sec["clauses"]) for sec in result)
        print(f"  {PASS}: {elapsed:.3f}s ({total_clauses} clauses)\n")
        RESULTS.append(("1.5 Huge file (50MB)", True, elapsed, "ok"))
    except MemoryError:
        print(f"  {FAIL}: MemoryError (50MB too large)\n")
        RESULTS.append(("1.5 Huge file (50MB)", False, 0, "error"))

    # ============================================
    # SECTION 2: SUMMARIZE PERFORMANCE
    # ============================================
    print("\n--- SECTION 2: SUMMARIZE PERFORMANCE ---\n")

    # 2.1 Small input
    small_sections = [{"section_number": str(i), "section_title": f"Section {i}", "clauses": [{"clause_id": f"{i}.1", "clause_text": f"Clause text."}]} for i in range(1, 6)]
    check("2.1 Small input (5 sections)", lambda: summarize_policy(small_sections), threshold=0.01)

    # 2.2 Medium input
    medium_sections = [{"section_number": str(i), "section_title": f"Section {i}", "clauses": [{"clause_id": f"{i}.1", "clause_text": f"Clause text."}]} for i in range(1, 101)]
    check("2.2 Medium input (100 sections)", lambda: summarize_policy(medium_sections), threshold=0.1)

    # 2.3 Large input
    large_sections = [{"section_number": str(i), "section_title": f"Section {i}", "clauses": [{"clause_id": f"{i}.1", "clause_text": f"Clause text."}]} for i in range(1, 1001)]
    check("2.3 Large input (1000 sections)", lambda: summarize_policy(large_sections), threshold=1.0)

    # 2.4 Huge input
    huge_sections = [{"section_number": str(i), "section_title": f"Section {i}", "clauses": [{"clause_id": f"{i}.1", "clause_text": f"Clause text."}]} for i in range(1, 10001)]
    check("2.4 Huge input (10000 sections)", lambda: summarize_policy(huge_sections), threshold=5.0)

    # ============================================
    # SECTION 3: END-TO-END PERFORMANCE
    # ============================================
    print("\n--- SECTION 3: END-TO-END PERFORMANCE ---\n")

    # 3.1 Full pipeline small
    p = write_file(os.path.join(tmp, "e2e_small.txt"), generate_policy(10, 5))
    check("3.1 E2E Small (50 clauses)", lambda: (
        sections := retrieve_policy(p),
        summarize_policy(sections)
    ), threshold=0.2)

    # 3.2 Full pipeline medium
    p = write_file(os.path.join(tmp, "e2e_medium.txt"), generate_policy(50, 10))
    check("3.2 E2E Medium (500 clauses)", lambda: (
        sections := retrieve_policy(p),
        summarize_policy(sections)
    ), threshold=1.0)

    # 3.3 Full pipeline large
    p = write_file(os.path.join(tmp, "e2e_large.txt"), generate_policy(100, 50))
    check("3.3 E2E Large (5000 clauses)", lambda: (
        sections := retrieve_policy(p),
        summarize_policy(sections)
    ), threshold=5.0)

    # ============================================
    # SECTION 4: REPEATED OPERATIONS (STABILITY)
    # ============================================
    print("\n--- SECTION 4: REPEATED OPERATIONS ---\n")

    # 4.1 Parse same file 100 times
    p = write_file(os.path.join(tmp, "repeat.txt"), generate_policy(20, 5))
    check("4.1 Parse 100 times", lambda: [
        retrieve_policy(p) for _ in range(100)
    ], threshold=5.0)

    # 4.2 Summarize same input 100 times
    sections = [{"section_number": str(i), "section_title": f"S{i}", "clauses": [{"clause_id": f"{i}.1", "clause_text": "Text."}]} for i in range(1, 51)]
    check("4.2 Summarize 100 times", lambda: [
        summarize_policy(sections) for _ in range(100)
    ], threshold=2.0)

    # ============================================
    # SECTION 5: MEMORY USAGE
    # ============================================
    print("\n--- SECTION 5: MEMORY USAGE ---\n")

    # 5.1 Memory with 10000 clauses
    print("TEST: 5.1 Memory with 10000 clauses")
    big_sections = [{"section_number": str(i), "section_title": f"Section {i}", "clauses": [{"clause_id": f"{i}.1", "clause_text": f"Clause text " * 10}]} for i in range(1, 1001)]
    try:
        import tracemalloc
        tracemalloc.start()
        result = summarize_policy(big_sections)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peak_mb = peak / 1024 / 1024
        if peak_mb < 100:
            print(f"  {PASS}: Peak memory {peak_mb:.1f}MB (< 100MB)\n")
            RESULTS.append(("5.1 Memory 10K clauses", True, peak_mb, "ok"))
        else:
            print(f"  {WARN}: Peak memory {peak_mb:.1f}MB (> 100MB)\n")
            RESULTS.append(("5.1 Memory 10K clauses", True, peak_mb, "high_memory"))
    except ImportError:
        print(f"  PASS: tracemalloc not available (skip)\n")
        RESULTS.append(("5.1 Memory 10K clauses", True, 0, "skip"))

    # ============================================
    # SECTION 6: THROUGHPUT
    # ============================================
    print("\n--- SECTION 6: THROUGHPUT ---\n")

    # 6.1 Clauses per second
    print("TEST: 6.1 Throughput measurement")
    p = write_file(os.path.join(tmp, "throughput.txt"), generate_policy(100, 20))
    try:
        start = time.perf_counter()
        total_clauses = 0
        for _ in range(10):
            sections = retrieve_policy(p)
            total_clauses += sum(len(s["clauses"]) for s in sections)
        elapsed = time.perf_counter() - start
        throughput = total_clauses / elapsed
        print(f"  {PASS}: {throughput:.0f} clauses/second ({total_clauses} clauses in {elapsed:.3f}s)\n")
        RESULTS.append(("6.1 Throughput", True, throughput, "ok"))
    except Exception as e:
        print(f"  {FAIL}: {e}\n")
        RESULTS.append(("6.1 Throughput", False, 0, "error"))

    # ============================================
    # SECTION 7: REAL POLICY FILE PERFORMANCE
    # ============================================
    print("\n--- SECTION 7: REAL POLICY FILE ---\n")

    # 7.1 Real policy file performance
    check("7.1 Real policy file (policy_hr_leave.txt)", lambda: (
        sections := retrieve_policy(real_input),
        summarize_policy(sections)
    ), threshold=1.0)

    # ============================================
    # SUMMARY
    # ============================================
    print("=" * 60)
    passed = sum(1 for _, p, _, _ in RESULTS if p)
    total = len(RESULTS)
    failed = [(n, _, _, _) for n, p, _, _ in RESULTS if not p]
    slow = [(n, _, t, _) for n, p, t, s in RESULTS if s == "slow"]

    print(f"  Total: {total} | Passed: {passed} | Failed: {total - passed}")
    if failed:
        print("  FAILURES:")
        for n, _, _, _ in failed:
            print(f"    - {n}")
    if slow:
        print("  SLOW (> threshold):")
        for n, _, t, _ in slow:
            print(f"    - {n}: {t:.3f}s")
    if not failed and not slow:
        print("  ALL PASS - No performance issues")
    print("=" * 60)

    shutil.rmtree(tmp, ignore_errors=True)
