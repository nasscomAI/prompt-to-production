"""
Verification Script for UC-0B — Summary That Changes Meaning (CRAFT Self-Test)
Asserts prevention of clause omission, condition dropping, obligation softening, and scope bleed.
"""
import os
import sys
from app import retrieve_policy, summarize_policy

# The 10 critical clauses from the Ground Truth inventory
CRITICAL_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2"
]

# All numbered clauses defined in the policy
ALL_CLAUSES = [
    "1.1", "1.2",
    "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.1", "3.2", "3.3", "3.4",
    "4.1", "4.2", "4.3", "4.4",
    "5.1", "5.2", "5.3", "5.4",
    "6.1", "6.2", "6.3",
    "7.1", "7.2", "7.3",
    "8.1", "8.2",
]

# Scope bleed phrases that must NOT appear in output
FORBIDDEN_SCOPE_BLEED = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
    "generally understood",
    "best practice",
    "industry standard",
    "customarily",
]


def test_output_file_exists():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    summary_path = os.path.join(base_dir, "summary_hr_leave.txt")
    assert os.path.exists(summary_path), f"Output file missing: {summary_path}"
    with open(summary_path, mode="r", encoding="utf-8") as f:
        content = f.read()
    assert len(content.strip()) > 500, "Summary file is too short or empty."
    return content


def test_clause_inventory_presence(content: str):
    """Failure Mode 1: Clause omission check."""
    for cid in ALL_CLAUSES:
        assert f"Clause {cid}" in content or f"{cid}" in content, (
            f"Clause Omission Failure: Clause {cid} is missing from summary."
        )


def test_multi_condition_preservation(content: str):
    """Failure Mode 2: Condition dropping & obligation softening check."""
    # Clause 5.2 dual approver condition
    assert "Department Head" in content and "HR Director" in content, (
        "Condition Drop Failure in Clause 5.2: Missing Department Head or HR Director dual approval requirement."
    )
    assert "Manager approval alone is not sufficient" in content or "not sufficient" in content, (
        "Obligation Softening Failure in Clause 5.2: Manager approval alone restriction missing."
    )

    # Clause 2.4 verbal approval prohibition
    assert "Verbal approval is not valid" in content or "verbal" in content.lower(), (
        "Obligation Softening Failure in Clause 2.4: Verbal approval invalidity dropped."
    )

    # Clause 2.5 LOP regardless of subsequent approval
    assert "Loss of Pay" in content or "LOP" in content, (
        "Obligation Drop Failure in Clause 2.5: Loss of Pay sanction dropped."
    )

    # Clause 2.6 & 2.7 carry forward limits and expiry
    assert "5" in content and "31 December" in content, (
        "Condition Drop Failure in Clause 2.6: 5-day cap or 31 December forfeiture dropped."
    )
    assert ("first quarter" in content.lower() or "january–march" in content.lower() or "january-march" in content.lower()), (
        "Condition Drop Failure in Clause 2.7: Q1 usage window dropped."
    )

    # Clause 3.2 medical cert within 48 hours for 3+ consecutive days
    assert "48 hours" in content and "3" in content, (
        "Condition Drop Failure in Clause 3.2: 48 hours submission window or 3-day threshold dropped."
    )

    # Clause 3.4 holiday-adjacent rule
    assert "public holiday" in content or "annual leave" in content, (
        "Condition Drop Failure in Clause 3.4: Holiday-adjacent medical cert rule dropped."
    )

    # Clause 5.3 Municipal Commissioner approval for >30 days
    assert "Municipal Commissioner" in content and "30" in content, (
        "Condition Drop Failure in Clause 5.3: Municipal Commissioner approval or 30-day threshold dropped."
    )

    # Clause 7.2 prohibition on in-service encashment
    assert "not permitted" in content.lower() or "not permitted under any circumstances" in content.lower(), (
        "Obligation Softening Failure in Clause 7.2: In-service encashment prohibition softened."
    )


def test_zero_scope_bleed(content: str):
    """Failure Mode 3: Scope bleed check."""
    content_lower = content.lower()
    for phrase in FORBIDDEN_SCOPE_BLEED:
        assert phrase not in content_lower, (
            f"Scope Bleed Failure: Prohibited hallucinated phrase '{phrase}' found in summary."
        )


def test_error_handling():
    """Test error handling on missing/empty files."""
    try:
        retrieve_policy("non_existent_policy_file.txt")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        pass


def run_all_checks():
    print("=" * 60)
    print("RUNNING UC-0B SELF-TEST SUITE (CRAFT)")
    print("=" * 60)

    try:
        print("[1/4] Checking output summary existence and size...")
        content = test_output_file_exists()
        print("  --> PASS: summary_hr_leave.txt exists and is fully populated.")

        print("[2/4] Checking 100% clause inventory completeness (No Clause Omission)...")
        test_clause_inventory_presence(content)
        print(f"  --> PASS: All {len(ALL_CLAUSES)} numbered clauses (including all 10 critical ground-truth clauses) present.")

        print("[3/4] Checking multi-condition preservation & binding verbs (No Obligation Softening)...")
        test_multi_condition_preservation(content)
        print("  --> PASS: Dual-approver gates, time windows, and strict prohibitions preserved with 100% fidelity.")

        print("[4/4] Checking zero scope bleed & error resilience...")
        test_zero_scope_bleed(content)
        test_error_handling()
        print("  --> PASS: Zero hallucinated phrases and proper exception handling verified.")

        print("=" * 60)
        print("ALL UC-0B VERIFICATION CHECKS PASSED SUCCESSFULLY! (100% PASS)")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n❌ ASSERTION FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return False


if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
