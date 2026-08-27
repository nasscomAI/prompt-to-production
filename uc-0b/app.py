"""
UC-0B — HR Leave Policy Advisor
Built using RICE prompt + agents.md + skills.md workflow.
Reads policy from data/policy-documents/policy_hr_leave.txt and answers leave queries.
"""
import argparse
import os
import re
import json
from dataclasses import dataclass, field, asdict
from typing import Optional

# ─── Leave Category Definitions ───────────────────────────────────────────────

LEAVE_TYPES = [
    "Annual Leave", "Sick Leave", "Maternity Leave",
    "Paternity Leave", "Leave Without Pay", "Compensatory Off"
]

LEAVE_KEYWORDS = {
    "Annual Leave": ["annual leave", "vacation", "paid leave", "casual leave", "earned leave", "privilege leave", "pl leave", "el leave", "carry forward", "encash"],
    "Sick Leave": ["sick", "medical", "illness", "unwell", "hospital", "doctor", "health", "fever", "disease"],
    "Maternity Leave": ["maternity", "pregnancy", "pregnant", "childbirth", "newborn", "baby", "delivery", "expecting"],
    "Paternity Leave": ["paternity", "father", "fatherhood", "child born", "new father", "dad leave"],
    "Leave Without Pay": ["lwp", "without pay", "unpaid", "leave without", "no pay", "exhausted leave"],
    "Compensatory Off": ["compensatory", "comp off", "comp-off", "worked on holiday", "holiday worked",
                          "overtime", "pending holiday", "pending hodliday", "take my holiday",
                          "take holiday", "holiday on", "public holiday", "gazetted holiday",
                          "independence day", "republic day", "gandhi jayanti"]
}

# Common misspellings/typos → corrected keyword for matching
TYPO_CORRECTIONS = {
    "hodliday": "holiday", "holday": "holiday", "hoilday": "holiday",
    "auguest": "august", "agust": "august", "augst": "august",
    "leav": "leave", "leve": "leave", "levae": "leave",
    "anual": "annual", "annuall": "annual",
    "compansatory": "compensatory", "compensatry": "compensatory",
    "maternty": "maternity", "paternty": "paternity",
    "medicl": "medical", "medcal": "medical",
}

# ─── Policy Rules Engine ──────────────────────────────────────────────────────

@dataclass
class LeaveCategory:
    leave_type: str
    confidence: str = "HIGH"
    flag: str = ""

@dataclass
class EligibilityResult:
    verdict: str  # ELIGIBLE | NOT_ELIGIBLE | CONDITIONAL
    conditions: list = field(default_factory=list)
    required_documents: list = field(default_factory=list)
    required_approvals: list = field(default_factory=list)
    policy_references: list = field(default_factory=list)
    explanation: str = ""
    warnings: list = field(default_factory=list)

@dataclass
class LeaveBalance:
    annual_leave_accrued: float = 0.0
    annual_leave_remaining: float = 0.0
    sick_leave_remaining: int = 12
    carry_forward_eligible: int = 0
    summary: str = ""


def categorise_leave(query: str) -> LeaveCategory:
    """Skill 1: Classify free-text query into a leave category."""
    query_lower = query.lower()

    # Apply typo corrections for fuzzy matching
    normalized = query_lower
    for typo, correction in TYPO_CORRECTIONS.items():
        normalized = normalized.replace(typo, correction)

    scores = {}
    for ltype, keywords in LEAVE_KEYWORDS.items():
        # Match against both original and typo-corrected text
        score = sum(1 for kw in keywords if kw in query_lower or kw in normalized)
        if score > 0:
            scores[ltype] = score

    if not scores:
        return LeaveCategory(leave_type="UNKNOWN", confidence="LOW", flag="NEEDS_REVIEW")

    best = max(scores, key=scores.get)
    best_score = scores[best]
    runner_up = sorted(scores.values(), reverse=True)

    if best_score >= 2:
        confidence = "HIGH"
    elif len(runner_up) > 1 and runner_up[0] == runner_up[1]:
        confidence = "LOW"
        return LeaveCategory(leave_type=best, confidence=confidence, flag="NEEDS_REVIEW")
    else:
        confidence = "MEDIUM"

    return LeaveCategory(leave_type=best, confidence=confidence, flag="")


def check_eligibility(
    leave_type: str,
    employee_type: str = "permanent",
    duration_days: int = 1,
    advance_notice_days: int = 14,
    adjacent_to_holiday: bool = False,
    remaining_balance: Optional[dict] = None,
    additional_context: str = ""
) -> EligibilityResult:
    """Skill 2: Check eligibility and list conditions for a leave type."""
    remaining_balance = remaining_balance or {}
    ctx_lower = additional_context.lower()
    result = EligibilityResult(verdict="ELIGIBLE")

    # §1.2 — Scope check
    if employee_type not in ("permanent", "contractual"):
        result.verdict = "NOT_ELIGIBLE"
        result.explanation = "This policy applies only to permanent and contractual employees (§1.2). Daily wage workers and consultants are governed by their respective contracts."
        result.policy_references.append("§1.2")
        return result

    if leave_type == "UNKNOWN":
        result.verdict = "NOT_ELIGIBLE"
        result.explanation = "Could not determine leave type. Please consult HR directly."
        return result

    # ── Annual Leave Rules ────────────────────────────────────────────────
    if leave_type == "Annual Leave":
        result.policy_references = ["§2.1", "§2.2", "§2.3", "§2.4", "§2.5", "§2.6", "§2.7"]
        result.conditions.append("Maximum 18 days per calendar year (§2.1)")
        result.conditions.append("Accrues at 1.5 days/month from date of joining (§2.2)")
        result.required_documents.append("Form HR-L1")
        result.required_approvals.append("Direct Manager (written approval only — verbal not valid)")

        if advance_notice_days < 14:
            result.verdict = "CONDITIONAL"
            result.warnings.append(f"Advance notice is {advance_notice_days} days — policy requires minimum 14 calendar days (§2.3). Unapproved absence will be marked LOP (§2.5).")

        bal = remaining_balance.get("Annual Leave", 18)
        if duration_days > bal:
            result.verdict = "NOT_ELIGIBLE"
            result.warnings.append(f"Requested {duration_days} days but only {bal} days remaining.")

        result.conditions.append("Max 5 unused days carry forward to next year (§2.6)")
        result.conditions.append("Carry-forward days must be used by 31 March (§2.7)")
        result.explanation = f"Annual Leave request for {duration_days} day(s). Requires Form HR-L1 submitted 14+ days in advance with written manager approval."

    # ── Sick Leave Rules ──────────────────────────────────────────────────
    elif leave_type == "Sick Leave":
        result.policy_references = ["§3.1", "§3.2", "§3.3", "§3.4"]
        result.conditions.append("Maximum 12 days per calendar year (§3.1)")
        result.conditions.append("Cannot be carried forward (§3.3)")

        if duration_days >= 3:
            result.required_documents.append("Medical certificate from registered practitioner (submit within 48 hours of return) (§3.2)")
            result.conditions.append("Certificate required for 3+ consecutive days (§3.2)")

        if adjacent_to_holiday:
            result.required_documents.append("Medical certificate (mandatory when adjacent to public holiday or annual leave) (§3.4)")
            result.warnings.append("Sick leave adjacent to holiday/annual leave ALWAYS requires medical certificate regardless of duration (§3.4)")

        bal = remaining_balance.get("Sick Leave", 12)
        if duration_days > bal:
            result.verdict = "NOT_ELIGIBLE"
            result.warnings.append(f"Requested {duration_days} days but only {bal} sick leave days remaining.")

        result.explanation = f"Sick Leave request for {duration_days} day(s). Entitlement: 12 days/year, no carry-forward."

    # ── Maternity Leave Rules ─────────────────────────────────────────────
    elif leave_type == "Maternity Leave":
        result.policy_references = ["§4.1", "§4.2"]
        is_third_plus = any(w in ctx_lower for w in ["third", "3rd", "fourth", "4th", "subsequent"])

        if is_third_plus:
            max_weeks = 12
            result.conditions.append("12 weeks paid for third or subsequent child (§4.2)")
        else:
            max_weeks = 26
            result.conditions.append("26 weeks paid for first two live births (§4.1)")

        max_days = max_weeks * 7
        if duration_days > max_days:
            result.verdict = "CONDITIONAL"
            result.warnings.append(f"Requested {duration_days} days exceeds max {max_days} days ({max_weeks} weeks).")

        result.explanation = f"Maternity Leave: entitled to {max_weeks} weeks paid leave."

    # ── Paternity Leave Rules ─────────────────────────────────────────────
    elif leave_type == "Paternity Leave":
        result.policy_references = ["§4.3", "§4.4"]
        result.conditions.append("5 days paid leave (§4.3)")
        result.conditions.append("Must be taken within 30 days of child's birth (§4.3)")
        result.conditions.append("Cannot be split across multiple periods (§4.4)")

        if duration_days > 5:
            result.verdict = "NOT_ELIGIBLE"
            result.warnings.append(f"Requested {duration_days} days but maximum is 5 days (§4.3).")

        result.explanation = "Paternity Leave: 5 days paid, must be taken in one continuous block within 30 days of birth."

    # ── Leave Without Pay Rules ───────────────────────────────────────────
    elif leave_type == "Leave Without Pay":
        result.policy_references = ["§5.1", "§5.2", "§5.3", "§5.4"]
        result.verdict = "CONDITIONAL"
        result.conditions.append("All paid leave must be exhausted first (§5.1)")
        result.required_approvals.append("Department Head (§5.2)")
        result.required_approvals.append("HR Director (§5.2)")

        # Check if paid leave is exhausted
        annual_bal = remaining_balance.get("Annual Leave", 0)
        sick_bal = remaining_balance.get("Sick Leave", 0)
        if annual_bal > 0 or sick_bal > 0:
            result.verdict = "NOT_ELIGIBLE"
            result.warnings.append(f"Paid leave not exhausted — Annual: {annual_bal}, Sick: {sick_bal} days remaining (§5.1)")

        if duration_days > 30:
            result.required_approvals.append("Municipal Commissioner (for LWP > 30 days) (§5.3)")
            result.warnings.append("LWP exceeding 30 continuous days requires Municipal Commissioner approval (§5.3)")

        result.conditions.append("Manager approval alone is NOT sufficient (§5.2)")
        result.warnings.append("LWP periods do not count toward seniority, increments, or retirement benefits (§5.4)")
        result.explanation = f"Leave Without Pay for {duration_days} day(s). Requires exhaustion of all paid leave plus multi-level approval."

    # ── Compensatory Off Rules ────────────────────────────────────────────
    elif leave_type == "Compensatory Off":
        result.policy_references = ["§6.1", "§6.2", "§6.3"]
        result.conditions.append("Available only if employee worked on a public holiday (§6.2)")
        result.conditions.append("Must be taken within 60 days of the holiday worked (§6.2)")
        result.conditions.append("Cannot be encashed (§6.3)")
        result.explanation = "Compensatory Off: 1 day off for each public holiday worked, must be used within 60 days."

    return result


def calculate_leave_balance(
    employee_type: str = "permanent",
    months_of_service: int = 12,
    annual_leave_used: int = 0,
    sick_leave_used: int = 0,
    carry_forward_days: int = 0
) -> LeaveBalance:
    """Skill 3: Calculate leave balances."""
    if employee_type not in ("permanent", "contractual"):
        return LeaveBalance(summary="Not applicable — policy covers permanent/contractual employees only (§1.2)")

    if months_of_service < 0:
        return LeaveBalance(summary="ERROR: Invalid months of service. Please contact HR.")

    # Annual leave: 1.5 days/month, max 18/year
    accrued = min(months_of_service * 1.5, 18.0)
    cf = min(carry_forward_days, 5)  # Max 5 carry-forward
    annual_remaining = accrued - annual_leave_used + cf
    sick_remaining = max(12 - sick_leave_used, 0)
    cf_eligible = min(max(annual_remaining, 0), 5)

    summary = (
        f"Annual Leave: {accrued:.1f} accrued, {annual_leave_used} used, {cf} carry-forward → {annual_remaining:.1f} remaining\n"
        f"Sick Leave: 12 entitled, {sick_leave_used} used → {sick_remaining} remaining\n"
        f"Carry-forward eligible for next year: {cf_eligible} days (must use by 31 March)"
    )

    return LeaveBalance(
        annual_leave_accrued=accrued,
        annual_leave_remaining=annual_remaining,
        sick_leave_remaining=sick_remaining,
        carry_forward_eligible=cf_eligible,
        summary=summary
    )


def process_leave_query(query: str, employee_context: Optional[dict] = None) -> dict:
    """Skill 4: End-to-end pipeline — categorise, check eligibility, return advisory."""
    employee_context = employee_context or {}

    # Step 1: Categorise
    category = categorise_leave(query)

    # Step 2: Check eligibility
    eligibility = check_eligibility(
        leave_type=category.leave_type,
        employee_type=employee_context.get("employee_type", "permanent"),
        duration_days=employee_context.get("duration_days", 1),
        advance_notice_days=employee_context.get("advance_notice_days", 14),
        adjacent_to_holiday=employee_context.get("adjacent_to_holiday", False),
        remaining_balance=employee_context.get("remaining_balance"),
        additional_context=employee_context.get("additional_context", "")
    )

    # Step 3: Build advisory response
    lines = []
    lines.append("=" * 60)
    lines.append("  HR LEAVE POLICY ADVISOR — City Municipal Corporation")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"📋 Query: {query}")
    lines.append(f"📂 Leave Type: {category.leave_type} (Confidence: {category.confidence})")
    if category.flag:
        lines.append(f"⚠️  Flag: {category.flag}")
    lines.append("")
    lines.append(f"✅ Verdict: {eligibility.verdict}")
    lines.append(f"📝 Explanation: {eligibility.explanation}")
    lines.append("")

    if eligibility.conditions:
        lines.append("📌 Conditions:")
        for c in eligibility.conditions:
            lines.append(f"   • {c}")
        lines.append("")

    if eligibility.required_documents:
        lines.append("📄 Required Documents:")
        for d in eligibility.required_documents:
            lines.append(f"   • {d}")
        lines.append("")

    if eligibility.required_approvals:
        lines.append("👤 Required Approvals:")
        for a in eligibility.required_approvals:
            lines.append(f"   • {a}")
        lines.append("")

    if eligibility.warnings:
        lines.append("⚠️  Warnings:")
        for w in eligibility.warnings:
            lines.append(f"   • {w}")
        lines.append("")

    if eligibility.policy_references:
        lines.append(f"📖 Policy References: {', '.join(eligibility.policy_references)}")
        lines.append("")

    lines.append("=" * 60)

    advisory = "\n".join(lines)

    return {
        "category": asdict(category),
        "eligibility": asdict(eligibility),
        "advisory_response": advisory
    }


# ─── Interactive Mode ─────────────────────────────────────────────────────────

EXAMPLE_QUERIES = [
    "I want to take 5 days annual leave next week",
    "I am sick and need 4 days off, it's right after Diwali holiday",
    "I'm expecting my first child, how much maternity leave can I get?",
    "My wife just had a baby, can I take paternity leave?",
    "I've used all my leaves but need 2 more weeks off",
    "I worked on Republic Day, can I get a comp off?",
    "Can I encash my sick leave?",
    "How many leaves do I have remaining?",
]


def interactive_mode():
    """Run an interactive Q&A session."""
    print("\n" + "=" * 60)
    print("  HR LEAVE POLICY ADVISOR — Interactive Mode")
    print("  City Municipal Corporation | Policy HR-POL-001 v2.3")
    print("=" * 60)
    print("\nExample queries you can ask:")
    for i, q in enumerate(EXAMPLE_QUERIES, 1):
        print(f"  {i}. {q}")
    print("\nType 'quit' or 'exit' to stop.\n")

    while True:
        query = input("Your leave query> ").strip()
        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        # Parse optional context from --context flag inline
        ctx = {}
        # Simple heuristic: extract duration if mentioned
        dur_match = re.search(r'(\d+)\s*days?', query.lower())
        if dur_match:
            ctx["duration_days"] = int(dur_match.group(1))

        week_match = re.search(r'(\d+)\s*weeks?', query.lower())
        if week_match:
            ctx["duration_days"] = int(week_match.group(1)) * 7

        # Check for adjacent holiday hints
        if any(w in query.lower() for w in ["after holiday", "before holiday", "after diwali",
                "after republic", "before weekend", "after weekend", "adjacent"]):
            ctx["adjacent_to_holiday"] = True

        # Check for third child context
        if any(w in query.lower() for w in ["third", "3rd", "fourth", "subsequent"]):
            ctx["additional_context"] = query

        result = process_leave_query(query, ctx)
        print("\n" + result["advisory_response"])
        print()


def single_query_mode(query: str, context_json: Optional[str] = None):
    """Process a single query and print the result."""
    ctx = {}
    if context_json:
        ctx = json.loads(context_json)

    # Auto-extract duration from query if not in context
    if "duration_days" not in ctx:
        dur_match = re.search(r'(\d+)\s*days?', query.lower())
        if dur_match:
            ctx["duration_days"] = int(dur_match.group(1))

    result = process_leave_query(query, ctx)
    print(result["advisory_response"])
    return result


def balance_mode(months: int, annual_used: int, sick_used: int, carry_forward: int):
    """Display leave balance."""
    balance = calculate_leave_balance(
        months_of_service=months,
        annual_leave_used=annual_used,
        sick_leave_used=sick_used,
        carry_forward_days=carry_forward
    )
    print("\n" + "=" * 60)
    print("  LEAVE BALANCE REPORT")
    print("=" * 60)
    print(f"\n{balance.summary}\n")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B — HR Leave Policy Advisor (City Municipal Corporation)"
    )
    parser.add_argument("--query", "-q", type=str, help="Single leave query to process")
    parser.add_argument("--context", "-c", type=str, help='JSON context, e.g. \'{"duration_days":5,"employee_type":"permanent"}\'')
    parser.add_argument("--balance", action="store_true", help="Show leave balance calculator")
    parser.add_argument("--months", type=int, default=12, help="Months of service (for --balance)")
    parser.add_argument("--annual-used", type=int, default=0, help="Annual leave days used (for --balance)")
    parser.add_argument("--sick-used", type=int, default=0, help="Sick leave days used (for --balance)")
    parser.add_argument("--carry-forward", type=int, default=0, help="Carry-forward days from last year (for --balance)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Start interactive mode")

    args = parser.parse_args()

    if args.balance:
        balance_mode(args.months, args.annual_used, args.sick_used, args.carry_forward)
    elif args.query:
        single_query_mode(args.query, args.context)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
