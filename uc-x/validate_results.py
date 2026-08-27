"""
validate_results.py — UC-X Ask My Documents

Validates app.py against every agents.md enforcement rule by running the
7 canonical test questions from the README and checking each answer.

Usage:
    python validate_results.py

Exit code 0 = all checks passed. Exit code 1 = one or more failures.
"""

import os
import sys

# Allow importing app.py from the same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import (
    retrieve_documents,
    answer_question,
    AUTHORISED_FILES,
    BANNED_PHRASES,
    REFUSAL_TEMPLATE,
    POLICY_DIR,
    ConfigError,
    LoadError,
    ParseError,
    DependencyError,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

errors: list[str] = []
passes: list[str] = []


def fail(label: str, reason: str) -> None:
    errors.append(f"FAIL [{label}]: {reason}")


def ok(label: str) -> None:
    passes.append(f"PASS [{label}]")


def check(label: str, condition: bool, reason: str) -> None:
    if condition:
        ok(label)
    else:
        fail(label, reason)


# ---------------------------------------------------------------------------
# Load documents once
# ---------------------------------------------------------------------------

file_paths = [str(POLICY_DIR / f) for f in AUTHORISED_FILES]

try:
    index = retrieve_documents(file_paths)
    ok("retrieve_documents: loaded 3 authorised files")
except (ConfigError, LoadError, ParseError) as exc:
    fail("retrieve_documents: startup", str(exc))
    print("FATAL: cannot load documents — aborting validation.")
    sys.exit(1)

check(
    "retrieve_documents: exactly 3 docs indexed",
    len(index) == 3,
    f"Expected 3 documents in index, got {len(index)}",
)

for fname in AUTHORISED_FILES:
    check(
        f"retrieve_documents: '{fname}' present",
        fname in index,
        f"'{fname}' missing from index",
    )
    if fname in index:
        section_count = len(index[fname]["sections"])
        check(
            f"retrieve_documents: '{fname}' has sections",
            section_count > 0,
            f"'{fname}' parsed 0 sections",
        )

# ---------------------------------------------------------------------------
# Helper: run a question and apply all structural enforcement checks
# ---------------------------------------------------------------------------

def ask(question: str) -> str:
    return answer_question(question, index)


def assert_has_citation(label: str, answer: str) -> None:
    """Enforcement rule 4 — every factual answer must cite Source + Section."""
    if answer.strip().startswith(REFUSAL_TEMPLATE.strip()[:40]):
        ok(f"{label}: refusal (no citation needed)")
        return
    check(
        f"{label}: citation present",
        "Source:" in answer,
        f"No 'Source:' citation in answer.\nAnswer was:\n{answer}",
    )
    check(
        f"{label}: section number in citation",
        "Section" in answer,
        f"'Section' missing from citation.\nAnswer was:\n{answer}",
    )


def assert_no_hedging(label: str, answer: str) -> None:
    """Enforcement rule 2 — no banned hedging phrases."""
    for phrase in BANNED_PHRASES:
        check(
            f"{label}: no hedging '{phrase}'",
            phrase not in answer.lower(),
            f"Banned phrase '{phrase}' found in answer:\n{answer}",
        )


def assert_single_source(label: str, answer: str) -> None:
    """Enforcement rule 1 — answer must not cite more than one filename."""
    cited = [f for f in AUTHORISED_FILES if f in answer]
    check(
        f"{label}: single source (≤1 filename cited)",
        len(cited) <= 1,
        f"Multiple files cited in one answer: {cited}\nAnswer:\n{answer}",
    )


def assert_is_refusal(label: str, answer: str) -> None:
    """Enforcement rule 3 — refusal must match the exact template."""
    expected_start = "This question is not covered in the available policy documents"
    check(
        f"{label}: uses refusal template",
        answer.strip().startswith(expected_start),
        f"Expected refusal template, got:\n{answer}",
    )
    # Must not add extra explanation after the template
    template_lines = set(REFUSAL_TEMPLATE.strip().splitlines())
    extra_lines = [
        ln for ln in answer.strip().splitlines()
        if ln.strip() and ln.strip() not in template_lines
    ]
    check(
        f"{label}: no extra text after refusal",
        len(extra_lines) == 0,
        f"Unexpected extra lines appended to refusal: {extra_lines}",
    )


def assert_not_refusal(label: str, answer: str) -> None:
    """The answer should be factual, not a refusal."""
    check(
        f"{label}: factual answer (not a refusal)",
        "not covered in the available policy documents" not in answer,
        f"Got refusal when a factual answer was expected:\n{answer}",
    )


# ---------------------------------------------------------------------------
# Q1 — Annual leave carry-forward (HR policy 2.6)
# ---------------------------------------------------------------------------

Q1 = "Can I carry forward unused annual leave?"
a1 = ask(Q1)
assert_not_refusal("Q1-carry-forward", a1)
assert_has_citation("Q1-carry-forward", a1)
assert_no_hedging("Q1-carry-forward", a1)
assert_single_source("Q1-carry-forward", a1)
check(
    "Q1-carry-forward: cites HR policy",
    "policy_hr_leave.txt" in a1,
    f"Expected HR policy citation, got:\n{a1}",
)
# The answer must mention a numeric limit (5 days) and a forfeiture condition
check(
    "Q1-carry-forward: mentions carry-forward limit",
    any(term in a1.lower() for term in ["5 ", "five", "carry forward", "carryforward"]),
    f"No carry-forward limit found in answer:\n{a1}",
)

# ---------------------------------------------------------------------------
# Q2 — Install Slack (IT policy 2.3)
# ---------------------------------------------------------------------------

Q2 = "Can I install Slack on my work laptop?"
a2 = ask(Q2)
assert_not_refusal("Q2-install-slack", a2)
assert_has_citation("Q2-install-slack", a2)
assert_no_hedging("Q2-install-slack", a2)
assert_single_source("Q2-install-slack", a2)
check(
    "Q2-install-slack: cites IT policy",
    "policy_it_acceptable_use.txt" in a2,
    f"Expected IT policy citation, got:\n{a2}",
)
check(
    "Q2-install-slack: mentions approval requirement",
    any(term in a2.lower() for term in ["approval", "approve", "written"]),
    f"Approval condition missing from answer:\n{a2}",
)

# ---------------------------------------------------------------------------
# Q3 — Home office equipment allowance (Finance 3.1)
# ---------------------------------------------------------------------------

Q3 = "What is the home office equipment allowance?"
a3 = ask(Q3)
assert_not_refusal("Q3-home-equipment", a3)
assert_has_citation("Q3-home-equipment", a3)
assert_no_hedging("Q3-home-equipment", a3)
assert_single_source("Q3-home-equipment", a3)
check(
    "Q3-home-equipment: cites Finance policy",
    "policy_finance_reimbursement.txt" in a3,
    f"Expected Finance policy citation, got:\n{a3}",
)
check(
    "Q3-home-equipment: mentions amount or condition",
    any(term in a3.lower() for term in ["8,000", "8000", "one-time", "permanent"]),
    f"Amount or condition missing from answer:\n{a3}",
)

# ---------------------------------------------------------------------------
# Q4 — Cross-document trap: personal phone for work files (must NOT blend)
# ---------------------------------------------------------------------------

Q4 = "Can I use my personal phone to access work files when working from home?"
a4 = ask(Q4)
assert_no_hedging("Q4-personal-phone", a4)
assert_single_source("Q4-personal-phone", a4)  # must NOT cite both IT + HR
# Answer is acceptable as either single-source IT OR clean refusal
is_refusal = "not covered in the available policy documents" in a4
is_single_source_it = "policy_it_acceptable_use.txt" in a4 and "policy_hr_leave.txt" not in a4
check(
    "Q4-personal-phone: single-source IT answer OR clean refusal (no blend)",
    is_refusal or is_single_source_it,
    f"Answer blends HR + IT or is otherwise invalid:\n{a4}",
)
if not is_refusal:
    assert_has_citation("Q4-personal-phone", a4)

# ---------------------------------------------------------------------------
# Q5 — Flexible working culture (not in any document → refusal)
# ---------------------------------------------------------------------------

Q5 = "What is the company view on flexible working culture?"
a5 = ask(Q5)
assert_is_refusal("Q5-flexible-culture", a5)
assert_no_hedging("Q5-flexible-culture", a5)

# ---------------------------------------------------------------------------
# Q6 — DA and meal receipts same day (Finance 2.6 — explicitly prohibited)
# ---------------------------------------------------------------------------

Q6 = "Can I claim DA and meal receipts on the same day?"
a6 = ask(Q6)
assert_not_refusal("Q6-da-and-meals", a6)
assert_has_citation("Q6-da-and-meals", a6)
assert_no_hedging("Q6-da-and-meals", a6)
assert_single_source("Q6-da-and-meals", a6)
check(
    "Q6-da-and-meals: cites Finance policy",
    "policy_finance_reimbursement.txt" in a6,
    f"Expected Finance policy citation, got:\n{a6}",
)
check(
    "Q6-da-and-meals: communicates prohibition",
    any(term in a6.lower() for term in ["not", "prohibited", "cannot", "may not", "no "]),
    f"Prohibition not communicated in answer:\n{a6}",
)

# ---------------------------------------------------------------------------
# Q7 — Who approves leave without pay? (HR 5.2 — both approvers required)
# ---------------------------------------------------------------------------

Q7 = "Who approves leave without pay?"
a7 = ask(Q7)
assert_not_refusal("Q7-lwp-approvers", a7)
assert_has_citation("Q7-lwp-approvers", a7)
assert_no_hedging("Q7-lwp-approvers", a7)
assert_single_source("Q7-lwp-approvers", a7)
check(
    "Q7-lwp-approvers: cites HR policy",
    "policy_hr_leave.txt" in a7,
    f"Expected HR policy citation, got:\n{a7}",
)
check(
    "Q7-lwp-approvers: names Department Head",
    "department head" in a7.lower(),
    f"'Department Head' missing from answer (condition omission):\n{a7}",
)
check(
    "Q7-lwp-approvers: names HR Director",
    "hr director" in a7.lower(),
    f"'HR Director' missing from answer (condition omission):\n{a7}",
)

# ---------------------------------------------------------------------------
# Enforcement rule 1: ConfigError on wrong file list
# ---------------------------------------------------------------------------

try:
    retrieve_documents(["bad_file.txt"])
    fail("enforcement-config-error", "Should have raised ConfigError with wrong file list")
except ConfigError:
    ok("enforcement-config-error: rejects wrong file list")
except Exception as exc:
    fail("enforcement-config-error", f"Unexpected exception type: {type(exc).__name__}: {exc}")

# ---------------------------------------------------------------------------
# Enforcement rule 4: DependencyError when index is empty
# ---------------------------------------------------------------------------

try:
    answer_question("Any question", {})
    fail("enforcement-dependency-error", "Should have raised DependencyError with empty index")
except DependencyError:
    ok("enforcement-dependency-error: rejects empty index")
except Exception as exc:
    fail("enforcement-dependency-error", f"Unexpected exception type: {type(exc).__name__}: {exc}")

# ---------------------------------------------------------------------------
# Enforcement rule 4: ValueError on empty question
# ---------------------------------------------------------------------------

try:
    answer_question("", index)
    fail("enforcement-empty-question", "Should have raised ValueError for empty question")
except ValueError:
    ok("enforcement-empty-question: rejects empty string")
except Exception as exc:
    fail("enforcement-empty-question", f"Unexpected exception type: {type(exc).__name__}: {exc}")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

total = len(passes) + len(errors)
print(f"\n{'='*60}")
print(f"UC-X validate_results  —  {total} checks")
print(f"{'='*60}")
for p in passes:
    print(f"  {p}")
if errors:
    print()
    for e in errors:
        print(f"  {e}")
    print(f"\n{'='*60}")
    print(f"RESULT: {len(errors)} FAILURE(S) / {len(passes)} passed")
    sys.exit(1)
else:
    print(f"\nRESULT: ALL {len(passes)} CHECKS PASSED")
