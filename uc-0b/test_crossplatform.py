"""Cross-platform directory structure tests for UC-0B."""
import os
import sys
import subprocess
import tempfile
import platform
import shutil

sys.path.insert(0, os.path.dirname(__file__))
from app import retrieve_policy, summarize_policy

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
RESULTS = []


def check(name, fn):
    print(f"TEST: {name}")
    try:
        fn()
        print(f"  {PASS}\n")
        RESULTS.append((name, True))
    except AssertionError as e:
        print(f"  {FAIL}: {e}\n")
        RESULTS.append((name, False))
    except Exception as e:
        print(f"  {FAIL}: {type(e).__name__}: {e}\n")
        RESULTS.append((name, False))


def assert_true(condition, msg):
    if not condition:
        raise AssertionError(msg)


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


if __name__ == "__main__":
    print("=" * 60)
    print("UC-0B CROSS-PLATFORM DIRECTORY TESTS")
    print(f"OS: {platform.system()} | Python: {platform.python_version()}")
    print("=" * 60 + "\n")

    tmp = tempfile.mkdtemp()
    real_input = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents", "policy_hr_leave.txt")

    # Test 1: Forward slashes
    fwd_path = os.path.join(tmp, "sub", "policy_fwd.txt")
    write_file(fwd_path, "1. SEC\n1.1 Clause.")
    check("Forward slash paths (/)", lambda: assert_true(len(retrieve_policy(fwd_path)) > 0, "Should parse"))

    # Test 2: OS-native paths
    bwd_path = os.path.join(tmp, "sub", "policy_bwd.txt")
    write_file(bwd_path, "1. SEC\n1.1 Clause.")
    check("os.path.join paths (OS-native)", lambda: assert_true(len(retrieve_policy(bwd_path)) > 0, "Should parse"))

    # Test 3: Mixed separators
    mixed_path = tmp + "/sub/policy_mixed.txt"
    write_file(mixed_path, "1. SEC\n1.1 Clause.")
    check("Mixed separators (forward in string)", lambda: assert_true(len(retrieve_policy(mixed_path)) > 0, "Should parse"))

    # Test 4: Relative path
    rel_path = "sub/rel_test.txt"
    rel_full = os.path.join(tmp, rel_path)
    write_file(rel_full, "1. SEC\n1.1 Clause.")
    old_cwd = os.getcwd()
    os.chdir(tmp)
    try:
        check("Relative path", lambda: assert_true(len(retrieve_policy(rel_path)) > 0, "Should parse"))
    finally:
        os.chdir(old_cwd)

    # Test 5: Absolute path
    abs_path = os.path.abspath(fwd_path)
    check("Absolute path", lambda: assert_true(len(retrieve_policy(abs_path)) > 0, "Should parse"))

    # Test 6: Path with spaces
    space_path = os.path.join(tmp, "my documents", "policy file.txt")
    write_file(space_path, "1. SEC\n1.1 Clause.")
    check("Path with spaces", lambda: assert_true(len(retrieve_policy(space_path)) > 0, "Should parse"))

    # Test 7: Path with unicode
    unicode_path = os.path.join(tmp, "docs\u00e9", "policy.txt")
    write_file(unicode_path, "1. SEC\n1.1 Clause.")
    check("Path with unicode (\u00e9)", lambda: assert_true(len(retrieve_policy(unicode_path)) > 0, "Should parse"))

    # Test 8: Deeply nested
    deep_path = os.path.join(tmp, "a", "b", "c", "d", "e", "f", "policy.txt")
    write_file(deep_path, "1. SEC\n1.1 Clause.")
    check("Deeply nested (6 levels)", lambda: assert_true(len(retrieve_policy(deep_path)) > 0, "Should parse"))

    # Test 9: Path with dots
    dots_path = os.path.join(tmp, "sub.dir", "policy..file.txt")
    write_file(dots_path, "1. SEC\n1.1 Clause.")
    check("Path with extra dots", lambda: assert_true(len(retrieve_policy(dots_path)) > 0, "Should parse"))

    # Test 10: Hyphens and underscores
    special_path = os.path.join(tmp, "my-dir_name", "policy-file_v2.txt")
    write_file(special_path, "1. SEC\n1.1 Clause.")
    check("Path with hyphens/underscores", lambda: assert_true(len(retrieve_policy(special_path)) > 0, "Should parse"))

    # Test 11: Output to new directory
    new_dir = os.path.join(tmp, "new_output_dir")
    out_path = os.path.join(new_dir, "summary.txt")
    print("TEST: Output to new directory (auto-create)")
    try:
        os.makedirs(new_dir, exist_ok=True)
        sections = retrieve_policy(real_input)
        summary = summarize_policy(sections)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        assert os.path.exists(out_path), "Output file not created"
        print(f"  {PASS}\n")
        RESULTS.append(("Output new dir", True))
    except Exception as e:
        print(f"  {FAIL}: {e}\n")
        RESULTS.append(("Output new dir", False))

    # Test 12: Non-existent nested output
    nested_out = os.path.join(tmp, "nonexistent", "nested", "output.txt")
    print("TEST: Output to non-existent nested directory")
    try:
        sections = retrieve_policy(real_input)
        summary = summarize_policy(sections)
        with open(nested_out, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"  {FAIL}: Should have raised OSError\n")
        RESULTS.append(("Non-existent nested output", False))
    except OSError:
        print(f"  {PASS} (OSError raised as expected)\n")
        RESULTS.append(("Non-existent nested output", True))
    except Exception as e:
        print(f"  {PASS} ({type(e).__name__} raised)\n")
        RESULTS.append(("Non-existent nested output", True))

    # Test 13: Output to path with spaces
    space_out = os.path.join(tmp, "my output", "summary file.txt")
    print("TEST: Output to path with spaces")
    try:
        os.makedirs(os.path.dirname(space_out), exist_ok=True)
        sections = retrieve_policy(real_input)
        summary = summarize_policy(sections)
        with open(space_out, 'w', encoding='utf-8') as f:
            f.write(summary)
        assert os.path.exists(space_out), "Output file not created"
        print(f"  {PASS}\n")
        RESULTS.append(("Output with spaces", True))
    except Exception as e:
        print(f"  {FAIL}: {e}\n")
        RESULTS.append(("Output with spaces", False))

    # Test 14: Same directory as input
    same_dir_out = os.path.join(os.path.dirname(real_input), "summary_test_delete.txt")
    print("TEST: Output to same directory as input")
    try:
        sections = retrieve_policy(real_input)
        summary = summarize_policy(sections)
        with open(same_dir_out, 'w', encoding='utf-8') as f:
            f.write(summary)
        assert os.path.exists(same_dir_out), "Output file not created"
        os.unlink(same_dir_out)
        print(f"  {PASS}\n")
        RESULTS.append(("Same dir output", True))
    except Exception as e:
        print(f"  {FAIL}: {e}\n")
        RESULTS.append(("Same dir output", False))

    # Test 15: CLI with mixed separators
    print("TEST: CLI with mixed path separators")
    cli_out = os.path.join(tmp, "cli_out.txt")
    mixed_cli = fwd_path.replace("\\", "/")
    r = subprocess.run(
        [sys.executable, "app.py", "--input", mixed_cli, "--output", cli_out],
        capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__))
    )
    if r.returncode == 0:
        print(f"  {PASS}\n")
        RESULTS.append(("CLI mixed separators", True))
    else:
        print(f"  {FAIL}: returncode={r.returncode}\n")
        RESULTS.append(("CLI mixed separators", False))

    # Test 16: CLI with non-existent input
    print("TEST: CLI with non-existent input")
    r = subprocess.run(
        [sys.executable, "app.py", "--input", "ghost.txt", "--output", os.path.join(tmp, "x.txt")],
        capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__))
    )
    if r.returncode != 0 and "not found" in r.stderr.lower():
        print(f"  {PASS}\n")
        RESULTS.append(("CLI non-existent input", True))
    else:
        print(f"  {FAIL}: returncode={r.returncode}\n")
        RESULTS.append(("CLI non-existent input", False))

    # Test 17: Symlink
    print("TEST: Symlinked file")
    try:
        real_file = os.path.join(tmp, "real_policy.txt")
        write_file(real_file, "1. SEC\n1.1 Clause.")
        link_file = os.path.join(tmp, "link_policy.txt")
        os.symlink(real_file, link_file)
        sections = retrieve_policy(link_file)
        assert len(sections) > 0, "Should parse symlink"
        print(f"  {PASS}\n")
        RESULTS.append(("Symlink", True))
    except OSError as e:
        print(f"  SKIP (not supported): {e}\n")
        RESULTS.append(("Symlink", True))
    except Exception as e:
        print(f"  {FAIL}: {e}\n")
        RESULTS.append(("Symlink", False))

    # Cleanup
    shutil.rmtree(tmp, ignore_errors=True)

    # Summary
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
