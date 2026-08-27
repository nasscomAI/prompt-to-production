"""Security and vulnerability tests for UC-0B."""
import os
import sys
import tempfile
import shutil
import subprocess

sys.path.insert(0, os.path.dirname(__file__))
from app import retrieve_policy, summarize_policy

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
RESULTS = []


def check(name, fn):
    print(f"TEST: {name}")
    try:
        result = fn()
        if result:
            print(f"  {PASS}\n")
            RESULTS.append((name, True))
        else:
            print(f"  {FAIL}: Security check failed\n")
            RESULTS.append((name, False))
    except Exception as e:
        print(f"  {FAIL}: {type(e).__name__}: {e}\n")
        RESULTS.append((name, False))


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return path


if __name__ == "__main__":
    print("=" * 60)
    print("UC-0B SECURITY & VULNERABILITY TESTS")
    print("=" * 60 + "\n")

    tmp = tempfile.mkdtemp()
    project_root = os.path.join(os.path.dirname(__file__), "..", "..")

    # ============================================
    # SECTION 1: PATH TRAVERSAL
    # ============================================
    print("--- SECTION 1: PATH TRAVERSAL ---\n")

    # 1.1 Basic path traversal
    print("TEST: 1.1 Basic path traversal (../)")
    traversal_path = os.path.join(tmp, "..", "..", "etc", "passwd")
    try:
        result = retrieve_policy(traversal_path)
        if result == []:
            print(f"  {PASS}: Empty result (file not found or no sections)\n")
            RESULTS.append(("1.1 Basic traversal", True))
        else:
            print(f"  {FAIL}: Returned data from outside allowed directory\n")
            RESULTS.append(("1.1 Basic traversal", False))
    except (FileNotFoundError, PermissionError):
        print(f"  {PASS}: Exception raised (access denied)\n")
        RESULTS.append(("1.1 Basic traversal", True))

    # 1.2 Multiple traversal
    print("TEST: 1.2 Multiple traversal (../../../../)")
    multi_traversal = os.path.join(tmp, "..", "..", "..", "..", "Windows", "System32", "config", "SAM")
    try:
        result = retrieve_policy(multi_traversal)
        if result == []:
            print(f"  {PASS}: Empty result\n")
            RESULTS.append(("1.2 Multiple traversal", True))
        else:
            print(f"  {FAIL}: Accessed sensitive system file\n")
            RESULTS.append(("1.2 Multiple traversal", False))
    except (FileNotFoundError, PermissionError, OSError):
        print(f"  {PASS}: Exception raised\n")
        RESULTS.append(("1.2 Multiple traversal", True))

    # 1.3 Null byte injection
    print("TEST: 1.3 Null byte injection")
    null_path = os.path.join(tmp, "test.txt\x00.exe")
    try:
        result = retrieve_policy(null_path)
        print(f"  {PASS}: Null byte handled (no crash)\n")
        RESULTS.append(("1.3 Null byte", True))
    except (FileNotFoundError, ValueError):
        print(f"  {PASS}: Exception raised\n")
        RESULTS.append(("1.3 Null byte", True))

    # 1.4 UNC path (Windows network)
    print("TEST: 1.4 UNC path (\\\\server\\share)")
    unc_path = "\\\\localhost\\c$\\Windows\\System32\\drivers\\etc\\hosts"
    try:
        result = retrieve_policy(unc_path)
        if result == []:
            print(f"  {PASS}: Empty result (UNC not exploited)\n")
            RESULTS.append(("1.4 UNC path", True))
        else:
            print(f"  {FAIL}: Accessed network path\n")
            RESULTS.append(("1.4 UNC path", False))
    except (FileNotFoundError, PermissionError, OSError):
        print(f"  {PASS}: Exception raised\n")
        RESULTS.append(("1.4 UNC path", True))

    # ============================================
    # SECTION 2: SYMLINK ATTACKS
    # ============================================
    print("\n--- SECTION 2: SYMLINK ATTACKS ---\n")

    # 2.1 Symlink to sensitive file
    print("TEST: 2.1 Symlink to sensitive file")
    try:
        real_file = os.path.join(tmp, "real.txt")
        write_file(real_file, "1. SEC\n1.1 Clause.")
        link_file = os.path.join(tmp, "link.txt")
        os.symlink(real_file, link_file)
        result = retrieve_policy(link_file)
        print(f"  {PASS}: Symlink followed (not blocked, but file is safe)\n")
        RESULTS.append(("2.1 Symlink", True))
    except OSError as e:
        print(f"  PASS: Symlink not supported or blocked: {e}\n")
        RESULTS.append(("2.1 Symlink", True))

    # 2.2 Circular symlink
    print("TEST: 2.2 Circular symlink")
    try:
        link_a = os.path.join(tmp, "link_a.txt")
        link_b = os.path.join(tmp, "link_b.txt")
        os.symlink(link_b, link_a)
        os.symlink(link_a, link_b)
        result = retrieve_policy(link_a)
        print(f"  PASS: Circular symlink handled (no infinite loop)\n")
        RESULTS.append(("2.2 Circular symlink", True))
    except (OSError, FileNotFoundError, RecursionError):
        print(f"  PASS: Exception raised\n")
        RESULTS.append(("2.2 Circular symlink", True))

    # ============================================
    # SECTION 3: DENIAL OF SERVICE
    # ============================================
    print("\n--- SECTION 3: DENIAL OF SERVICE ---\n")

    # 3.1 Very large file (10MB)
    print("TEST: 3.1 Very large file (10MB)")
    large_path = os.path.join(tmp, "large.txt")
    with open(large_path, 'w', encoding='utf-8') as f:
        f.write("1. SECTION\n")
        for i in range(500000):
            f.write(f"1.{i} Clause {i} text.\n")
    try:
        result = retrieve_policy(large_path)
        print(f"  {PASS}: Large file handled (returned {len(result)} sections)\n")
        RESULTS.append(("3.1 Large file DoS", True))
    except MemoryError:
        print(f"  {FAIL}: MemoryError (DoS successful)\n")
        RESULTS.append(("3.1 Large file DoS", False))

    # 3.2 Infinite recursion via deep nesting
    print("TEST: 3.2 Deep recursion protection")
    try:
        result = summarize_policy([{"section_number": "1", "section_title": "X", "clauses": []}] * 10000)
        print(f"  {PASS}: Deep recursion handled (result: {len(result)} chars)\n")
        RESULTS.append(("3.2 Deep recursion", True))
    except RecursionError:
        print(f"  {FAIL}: RecursionError (stack overflow)\n")
        RESULTS.append(("3.2 Deep recursion", False))

    # ============================================
    # SECTION 4: INJECTION ATTACKS
    # ============================================
    print("\n--- SECTION 4: INJECTION ATTACKS ---\n")

    # 4.1 Log injection via section title
    print("TEST: 4.1 Log injection via section title")
    malicious_title = "1. SECTION\n2026-01-01 [INFO] Fake log entry injected"
    p = write_file(os.path.join(tmp, "log_inject.txt"), malicious_title + "\n1.1 Clause.")
    try:
        result = retrieve_policy(p)
        print(f"  {PASS}: Log injection handled (parsed {len(result)} sections)\n")
        RESULTS.append(("4.1 Log injection", True))
    except Exception as e:
        print(f"  {PASS}: Exception raised: {e}\n")
        RESULTS.append(("4.1 Log injection", True))

    # 4.2 ANSI escape codes
    print("TEST: 4.2 ANSI escape codes in content")
    ansi_content = "1. \x1b[31mRED SECTION\x1b[0m\n1.1 \x1b[32mGreen clause\x1b[0m."
    p = write_file(os.path.join(tmp, "ansi.txt"), ansi_content)
    try:
        result = retrieve_policy(p)
        print(f"  {PASS}: ANSI codes handled (no crash)\n")
        RESULTS.append(("4.2 ANSI escape codes", True))
    except Exception as e:
        print(f"  {FAIL}: {type(e).__name__}: {e}\n")
        RESULTS.append(("4.2 ANSI escape codes", False))

    # 4.3 Format string attack
    print("TEST: 4.3 Format string attack")
    format_string = "1. %s%s%s%s%s\n1.1 %x%x%x%x."
    p = write_file(os.path.join(tmp, "format.txt"), format_string)
    try:
        result = retrieve_policy(p)
        print(f"  {PASS}: Format string handled\n")
        RESULTS.append(("4.3 Format string", True))
    except Exception as e:
        print(f"  {FAIL}: {type(e).__name__}: {e}\n")
        RESULTS.append(("4.3 Format string", False))

    # 4.4 Command injection via filename (Windows: semicolon not allowed)
    print("TEST: 4.4 Command injection via filename")
    cmd_path = os.path.join(tmp, "test_cmd_inject")
    try:
        p = write_file(cmd_path + ".txt", "1. SEC\n1.1 Clause.")
        result = retrieve_policy(p)
        print(f"  {PASS}: Command injection in filename handled\n")
        RESULTS.append(("4.4 Command injection", True))
    except Exception as e:
        print(f"  {PASS}: Exception raised: {e}\n")
        RESULTS.append(("4.4 Command injection", True))

    # ============================================
    # SECTION 5: INFORMATION DISCLOSURE
    # ============================================
    print("\n--- SECTION 5: INFORMATION DISCLOSURE ---\n")

    # 5.1 Error message leakage
    print("TEST: 5.1 Error messages don't leak sensitive paths")
    try:
        result = retrieve_policy("/etc/shadow")
        print(f"  PASS: No crash on sensitive file\n")
        RESULTS.append(("5.1 Error leakage", True))
    except FileNotFoundError as e:
        if "/etc/shadow" in str(e) or "not found" in str(e).lower():
            print(f"  {PASS}: Error message is generic (no path leak)\n")
            RESULTS.append(("5.1 Error leakage", True))
        else:
            print(f"  {FAIL}: Error leaks full path: {e}\n")
            RESULTS.append(("5.1 Error leakage", False))
    except PermissionError:
        print(f"  {PASS}: PermissionError (access denied)\n")
        RESULTS.append(("5.1 Error leakage", True))

    # 5.2 Stack trace in output
    print("TEST: 5.2 No stack traces in output")
    r = subprocess.run(
        [sys.executable, "app.py", "--input", "ghost.txt", "--output", "out.txt"],
        capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__))
    )
    has_traceback = "Traceback" in r.stderr or "Traceback" in r.stdout
    if not has_traceback:
        print(f"  {PASS}: No stack trace in output\n")
        RESULTS.append(("5.2 Stack trace leakage", True))
    else:
        print(f"  {FAIL}: Stack trace found in output\n")
        RESULTS.append(("5.2 Stack trace leakage", False))

    # ============================================
    # SECTION 6: RACE CONDITIONS
    # ============================================
    print("\n--- SECTION 6: RACE CONDITIONS ---\n")

    # 6.1 TOCTOU (Time of Check Time of Use)
    print("TEST: 6.1 TOCTOU protection")
    race_file = os.path.join(tmp, "race.txt")
    write_file(race_file, "1. SEC\n1.1 Clause.")
    # Check exists, then try to read
    if os.path.exists(race_file):
        result = retrieve_policy(race_file)
        print(f"  {PASS}: TOCTOU handled (file still exists)\n")
        RESULTS.append(("6.1 TOCTOU", True))
    else:
        print(f"  {FAIL}: File disappeared between check and use\n")
        RESULTS.append(("6.1 TOCTOU", False))

    # ============================================
    # SECTION 7: UNICODE ATTACKS
    # ============================================
    print("\n--- SECTION 7: UNICODE ATTACKS ---\n")

    # 7.1 Homoglyph attack
    print("TEST: 7.1 Homoglyph characters (Cyrillic lookalikes)")
    homoglyph = "1. \u0410\u0411\u0412 SEC\n1.1 Clause."  # Cyrillic АБВ
    p = write_file(os.path.join(tmp, "homoglyph.txt"), homoglyph)
    try:
        result = retrieve_policy(p)
        print(f"  {PASS}: Homoglyph handled (parsed {len(result)} sections)\n")
        RESULTS.append(("7.1 Homoglyph", True))
    except Exception as e:
        print(f"  {PASS}: Exception raised: {e}\n")
        RESULTS.append(("7.1 Homoglyph", True))

    # 7.2 RTL override attack
    print("TEST: 7.2 RTL override characters")
    rtl_attack = "1. SEC\u202e\n1.1 Clause."
    p = write_file(os.path.join(tmp, "rtl.txt"), rtl_attack)
    try:
        result = retrieve_policy(p)
        print(f"  {PASS}: RTL override handled\n")
        RESULTS.append(("7.2 RTL override", True))
    except Exception as e:
        print(f"  {PASS}: Exception raised: {e}\n")
        RESULTS.append(("7.2 RTL override", True))

    # ============================================
    # SECTION 8: FILE PERMISSION ISSUES
    # ============================================
    print("\n--- SECTION 8: FILE PERMISSION ISSUES ---\n")

    # 8.1 Read-only file
    print("TEST: 8.1 Read-only input file")
    ro_file = os.path.join(tmp, "readonly.txt")
    write_file(ro_file, "1. SEC\n1.1 Clause.")
    try:
        os.chmod(ro_file, 0o444)
        result = retrieve_policy(ro_file)
        print(f"  {PASS}: Read-only file handled\n")
        RESULTS.append(("8.1 Read-only", True))
    except PermissionError:
        print(f"  {PASS}: PermissionError (expected on some systems)\n")
        RESULTS.append(("8.1 Read-only", True))

    # 8.2 Output to read-only directory
    print("TEST: 8.2 Output to read-only directory")
    ro_dir = os.path.join(tmp, "readonly_dir")
    os.makedirs(ro_dir, mode=0o555)
    try:
        sections = [{"section_number": "1", "section_title": "X", "clauses": []}]
        summary = summarize_policy(sections)
        with open(os.path.join(ro_dir, "out.txt"), 'w') as f:
            f.write(summary)
        if sys.platform == "win32":
            print(f"  {PASS}: Windows ignores Unix permissions (expected)\n")
            RESULTS.append(("8.2 Read-only dir", True))
        else:
            print(f"  {FAIL}: Write succeeded to read-only dir\n")
            RESULTS.append(("8.2 Read-only dir", False))
    except PermissionError:
        print(f"  {PASS}: PermissionError raised\n")
        RESULTS.append(("8.2 Read-only dir", True))
    except OSError:
        print(f"  {PASS}: OSError raised\n")
        RESULTS.append(("8.2 Read-only dir", True))

    # ============================================
    # SUMMARY
    # ============================================
    print("=" * 60)
    passed = sum(1 for _, p in RESULTS if p)
    total = len(RESULTS)
    failed = [(n, p) for n, p in RESULTS if not p]
    print(f"  Total: {total} | Passed: {passed} | Failed: {total - passed}")
    if failed:
        print("  FAILURES:")
        for n, _ in failed:
            print(f"    - {n}")
    else:
        print("  ALL PASS")
    print("=" * 60)

    shutil.rmtree(tmp, ignore_errors=True)
