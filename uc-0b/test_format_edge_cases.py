"""Comprehensive input format edge case tests for UC-0B."""
import os
import sys
import tempfile
import shutil

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
            print(f"  {FAIL}: Test returned False\n")
            RESULTS.append((name, False))
    except Exception as e:
        print(f"  {FAIL}: {type(e).__name__}: {e}\n")
        RESULTS.append((name, False))


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return path


def write_file_bytes(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(content)
    return path


if __name__ == "__main__":
    print("=" * 60)
    print("UC-0B INPUT FORMAT EDGE CASES")
    print("=" * 60 + "\n")

    tmp = tempfile.mkdtemp()

    # ============================================
    # SECTION 1: NO STRUCTURE AT ALL
    # ============================================
    print("--- SECTION 1: NO STRUCTURE ---\n")

    # 1.1 Empty file
    path = write_file(os.path.join(tmp, "empty.txt"), "")
    check("1.1 Empty file (0 bytes)", lambda: (
        retrieve_policy(path) == []
    ))

    # 1.2 Only whitespace
    p = write_file(os.path.join(tmp, "whitespace.txt"), "   \n\n   \t  \n  ")
    check("1.2 Only whitespace", lambda: (
        retrieve_policy(p) == []
    ))

    # 1.3 Only newlines
    p = write_file(os.path.join(tmp, "newlines.txt"), "\n\n\n\n\n")
    check("1.3 Only newlines", lambda: (
        retrieve_policy(p) == []
    ))

    # 1.4 Plain text, no numbers
    p = write_file(os.path.join(tmp, "plain.txt"), "This is a policy document about leave. There are no numbered sections.")
    check("1.4 Plain text, no numbers", lambda: (
        retrieve_policy(p) == []
    ))

    # 1.5 Single word
    p = write_file(os.path.join(tmp, "single_word.txt"), "Policy")
    check("1.5 Single word", lambda: (
        retrieve_policy(p) == []
    ))

    # ============================================
    # SECTION 2: SECTIONS WITHOUT CLAUSES
    # ============================================
    print("\n--- SECTION 2: SECTIONS WITHOUT CLAUSES ---\n")

    # 2.1 One section, no clauses
    p = write_file(os.path.join(tmp, "sec_no_clauses.txt"), "1. ANNUAL LEAVE\n2. SICK LEAVE\n3. HOLIDAYS")
    check("2.1 Sections without clauses", lambda: (
        len(retrieve_policy(p)) == 3
    ))

    # 2.2 Section with empty content
    p = write_file(os.path.join(tmp, "sec_empty.txt"), "1. ANNUAL LEAVE\n\n2. SICK LEAVE")
    check("2.2 Sections with empty lines between", lambda: (
        len(retrieve_policy(p)) == 2
    ))

    # ============================================
    # SECTION 3: CLAUSES WITHOUT SECTIONS
    # ============================================
    print("\n--- SECTION 3: CLAUSES WITHOUT SECTIONS ---\n")

    # 3.1 Clauses with no parent section
    p = write_file(os.path.join(tmp, "orphan_clauses.txt"), "1.1 First clause.\n1.2 Second clause.\n2.1 Another clause.")
    check("3.1 Orphan clauses (no section header)", lambda: (
        retrieve_policy(p) == []
    ))

    # ============================================
    # SECTION 4: MALFORMED NUMBERING
    # ============================================
    print("\n--- SECTION 4: MALFORMED NUMBERING ---\n")

    # 4.1 Section number without space
    p = write_file(os.path.join(tmp, "no_space.txt"), "1.ANNUAL LEAVE\n1.1 Some clause.")
    check("4.1 Section without space after number", lambda: (
        len(retrieve_policy(p)) == 0
    ))

    # 4.2 Double dots in section
    p = write_file(os.path.join(tmp, "double_dot.txt"), "1.. ANNUAL LEAVE\n1.1 Some clause.")
    check("4.2 Double dots in section number", lambda: (
        len(retrieve_policy(p)) == 0
    ))

    # 4.3 Non-numeric section number
    p = write_file(os.path.join(tmp, "alpha_section.txt"), "A. ANNUAL LEAVE\nA.1 Some clause.")
    check("4.3 Non-numeric section (A.)", lambda: (
        retrieve_policy(p) == []
    ))

    # 4.4 Roman numerals
    p = write_file(os.path.join(tmp, "roman.txt"), "I. ANNUAL LEAVE\nI.1 Some clause.")
    check("4.4 Roman numeral section (I.)", lambda: (
        retrieve_policy(p) == []
    ))

    # 4.5 Three-level numbering
    p = write_file(os.path.join(tmp, "three_level.txt"), "1. SECTION\n1.1.1 Deep clause.\n1.1.2 Another deep clause.")
    result = retrieve_policy(p)
    check("4.5 Three-level numbering (1.1.1) - clause rejected, section kept", lambda: (
        len(result) == 1 and len(result[0]["clauses"]) == 0
    ))

    # 4.6 Inconsistent numbering
    p = write_file(os.path.join(tmp, "inconsistent.txt"), "1. FIRST\n1.1 Clause.\n3. THIRD\n2.1 Clause.")
    check("4.6 Inconsistent section numbering", lambda: (
        len(retrieve_policy(p)) == 2
    ))

    # ============================================
    # SECTION 5: LINE ENDING VARIATIONS
    # ============================================
    print("\n--- SECTION 5: LINE ENDING VARIATIONS ---\n")

    # 5.1 Windows line endings (\r\n)
    p = write_file_bytes(os.path.join(tmp, "windows.txt"), b"1. SEC\r\n1.1 Clause.\r\n2. SEC2\r\n2.1 Clause2.\r\n")
    check("5.1 Windows line endings (\\r\\n)", lambda: (
        len(retrieve_policy(p)) == 2
    ))

    # 5.2 Unix line endings (\n)
    p = write_file_bytes(os.path.join(tmp, "unix.txt"), b"1. SEC\n1.1 Clause.\n2. SEC2\n2.1 Clause2.\n")
    check("5.2 Unix line endings (\\n)", lambda: (
        len(retrieve_policy(p)) == 2
    ))

    # 5.3 Old Mac line endings (\r)
    p = write_file_bytes(os.path.join(tmp, "oldmac.txt"), b"1. SEC\r1.1 Clause.\r2. SEC2\r2.1 Clause2.\r")
    check("5.3 Old Mac line endings (\\r)", lambda: (
        len(retrieve_policy(p)) >= 1
    ))

    # 5.4 Mixed line endings
    p = write_file_bytes(os.path.join(tmp, "mixed_endings.txt"), b"1. SEC\n1.1 Clause.\r\n2. SEC2\r2.1 Clause2.\n")
    check("5.4 Mixed line endings", lambda: (
        len(retrieve_policy(p)) >= 1
    ))

    # ============================================
    # SECTION 6: ENCODING ISSUES
    # ============================================
    print("\n--- SECTION 6: ENCODING ISSUES ---\n")

    # 6.1 UTF-8 with BOM
    p = write_file_bytes(os.path.join(tmp, "utf8bom.txt"), b"\xef\xbb\xbf1. SEC\n1.1 Clause.")
    check("6.1 UTF-8 with BOM", lambda: (
        len(retrieve_policy(p)) >= 1
    ))

    # 6.2 Latin-1 encoding
    p = write_file_bytes(os.path.join(tmp, "latin1.txt"), b"1. SEC\n1.1 Clause \xe9 accented.")
    try:
        retrieve_policy(p)
        check("6.2 Latin-1 encoding (may fail)", lambda: True)
    except UnicodeDecodeError:
        check("6.2 Latin-1 encoding (UnicodeDecodeError expected)", lambda: True)

    # 6.3 Binary file
    p = write_file_bytes(os.path.join(tmp, "binary.txt"), b"\x00\x01\x02\x03\xff\xfe")
    try:
        retrieve_policy(p)
        check("6.3 Binary file", lambda: True)
    except UnicodeDecodeError:
        check("6.3 Binary file (UnicodeDecodeError expected)", lambda: True)

    # ============================================
    # SECTION 7: SPECIAL CONTENT
    # ============================================
    print("\n--- SECTION 7: SPECIAL CONTENT ---\n")

    # 7.1 Very long line (10KB)
    long_line = "1. SECTION\n1.1 " + "x" * 10000 + "\n2. SECTION2\n2.1 Short."
    p = write_file(os.path.join(tmp, "long_line.txt"), long_line)
    check("7.1 Very long line (10KB)", lambda: (
        len(retrieve_policy(p)) == 2
    ))

    # 7.2 Unicode in content
    p = write_file(os.path.join(tmp, "unicode_content.txt"), "1. \u00c9TUDE\n1.1 Cl\u00e1use with \u00e9\u00e8\u00ea.")
    check("7.2 Unicode characters in content", lambda: (
        len(retrieve_policy(p)) == 1
    ))

    # 7.3 Special regex characters
    p = write_file(os.path.join(tmp, "regex_chars.txt"), "1. SECTION [test]\n1.1 Clause (with) {braces} + plus * star.")
    check("7.3 Special regex characters in text", lambda: (
        len(retrieve_policy(p)) == 1
    ))

    # 7.4 HTML-like content
    p = write_file(os.path.join(tmp, "html.txt"), "1. <b>SECTION</b>\n1.1 <p>Clause with <a>link</a></p>")
    check("7.4 HTML-like content", lambda: (
        len(retrieve_policy(p)) == 1
    ))

    # 7.5 JSON-like content
    p = write_file(os.path.join(tmp, "json.txt"), '1. {"key": "value"}\n1.1 {"nested": {"data": true}}')
    check("7.5 JSON-like content", lambda: (
        len(retrieve_policy(p)) == 1
    ))

    # 7.6 Markdown-like content
    p = write_file(os.path.join(tmp, "markdown.txt"), "1. # HEADING\n1.1 **Bold** and *italic* text.")
    check("7.6 Markdown-like content", lambda: (
        len(retrieve_policy(p)) == 1
    ))

    # ============================================
    # SECTION 8: PATH EDGE CASES
    # ============================================
    print("\n--- SECTION 8: PATH EDGE CASES ---\n")

    # 8.1 Path with Chinese characters
    p = write_file(os.path.join(tmp, "\u6587\u4ef6\u5939", "policy.txt"), "1. SEC\n1.1 Clause.")
    check("8.1 Path with Chinese characters", lambda: (
        len(retrieve_policy(p)) == 1
    ))

    # 8.2 Path with Arabic characters
    p = write_file(os.path.join(tmp, "\u0645\u062c\u0644\u062f", "policy.txt"), "1. SEC\n1.1 Clause.")
    check("8.2 Path with Arabic characters", lambda: (
        len(retrieve_policy(p)) == 1
    ))

    # 8.3 Path with emoji-like chars
    p = write_file(os.path.join(tmp, "folder_\U0001f600", "policy.txt"), "1. SEC\n1.1 Clause.")
    check("8.3 Path with emoji character", lambda: (
        len(retrieve_policy(p)) == 1
    ))

    # 8.4 Very long filename (200 chars)
    long_name = "a" * 200 + ".txt"
    p = write_file(os.path.join(tmp, long_name), "1. SEC\n1.1 Clause.")
    check("8.4 Very long filename (200 chars)", lambda: (
        len(retrieve_policy(p)) == 1
    ))

    # 8.5 Path with leading/trailing spaces
    p = write_file(os.path.join(tmp, " folder ", " policy.txt "), "1. SEC\n1.1 Clause.")
    check("8.5 Path with leading/trailing spaces", lambda: (
        len(retrieve_policy(p)) == 1
    ))

    # ============================================
    # SECTION 9: SUMMARIZE POLICY EDGE CASES
    # ============================================
    print("\n--- SECTION 9: SUMMARIZE POLICY EDGE CASES ---\n")

    # 9.1 Empty list
    check("9.1 summarize_policy([])", lambda: (
        summarize_policy([]) == "No policy content to summarize."
    ))

    # 9.2 None
    check("9.2 summarize_policy(None)", lambda: (
        "Error" in summarize_policy(None)
    ))

    # 9.3 String instead of list
    check("9.3 summarize_policy('string')", lambda: (
        "Error" in summarize_policy("string")
    ))

    # 9.4 Dict instead of list
    check("9.4 summarize_policy({})", lambda: (
        "Error" in summarize_policy({})
    ))

    # 9.5 List with non-dict items
    check("9.5 summarize_policy([1, 2, 3])", lambda: (
        "WARNING" in summarize_policy([1, 2, 3])
    ))

    # 9.6 Sections with missing keys
    check("9.6 Sections missing 'section_number'", lambda: (
        "WARNING" in summarize_policy([{"bad": "data"}])
    ))

    # 9.7 Clauses with missing keys
    check("9.7 Clauses missing 'clause_id'", lambda: (
        "WARNING" in summarize_policy([{"section_number": "1", "section_title": "X", "clauses": [{"bad": 1}]}])
    ))

    # 9.8 Very large input
    large_sections = [{"section_number": str(i), "section_title": f"Section {i}", "clauses": [{"clause_id": f"{i}.1", "clause_text": f"Clause {i}.1 text."}]} for i in range(1, 101)]
    result = summarize_policy(large_sections)
    check("9.8 Very large input (100 sections)", lambda: (
        len(result) > 1000
    ))

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
