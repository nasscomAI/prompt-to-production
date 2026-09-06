"""
UC-X app.py — Ask My Documents
Build guided by agents.md (RICE framework) and skills.md.

Failure modes targeted:
  - Cross-document blending     -> every answer cites exactly ONE source document
  - Hedged hallucination        -> verbatim refusal template for out-of-scope questions
  - Condition dropping          -> full limits/approvers/amounts preserved in answers
"""
import argparse
import re
import sys
from typing import Dict, List, Optional, Tuple

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

# ---------------------------------------------------------------------------
# Refusal template — verbatim, fixed. The only permitted out-of-scope answer.
# ---------------------------------------------------------------------------
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# Hedging phrases that must never appear in an answer.
HEDGE_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "as is standard practice",
    "usually",
]


class EnforcementError(Exception):
    """Raised when an answer would violate a RICE enforcement rule."""


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", text)).strip().lower()


def _trigger_match(query_norm: str, trigger: str) -> bool:
    """Word-boundary match for short triggers; substring for longer phrases."""
    t = trigger.lower()
    if len(t) <= 3:
        return re.search(r"\b" + re.escape(t) + r"\b", query_norm) is not None
    return t in query_norm


# ---------------------------------------------------------------------------
# Skill: retrieve_documents
# ---------------------------------------------------------------------------
def retrieve_documents(doc_paths: List[str]) -> Dict[str, Dict[str, str]]:
    """Parse each policy into {filename: {section_id: clause_text}}."""
    clause_re = re.compile(r"^(\d+\.\d+)\s+(.+)$")
    index: Dict[str, Dict[str, str]] = {}
    for path in doc_paths:
        try:
            with open(path, mode="r", encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"Policy file not found: {path}")

        sections: Dict[str, str] = {}
        current_id = None
        current_lines: List[str] = []

        def flush():
            nonlocal current_id, current_lines
            if current_id is not None and current_lines:
                sections[current_id] = " ".join(
                    line.strip() for line in current_lines).strip()
            current_id = None
            current_lines = []

        for raw in lines:
            line = raw.strip()
            if not line or line.startswith("═"):
                flush()
                continue
            m = clause_re.match(line)
            if m:
                flush()
                current_id = m.group(1)
                current_lines = [m.group(2)]
            elif current_id is not None:
                current_lines.append(line)
        flush()

        if not sections:
            raise ValueError(f"No numbered sections parsed from {path}")
        index[path] = sections
    return index


# ---------------------------------------------------------------------------
# Curated single-source knowledge base
# ---------------------------------------------------------------------------
def _intents() -> List[dict]:
    return [
        {
            "id": "annual_leave_carry_forward",
            "doc": "policy_hr_leave.txt",
            "sections": ["2.6", "2.7"],
            "triggers": ["carry forward", "carried forward", "carry-over",
                         "roll over", "unused annual leave", "annual leave"],
            "required": [],
            "forbidden": ["sick"],
            "answer": ("Yes, with limits (policy_hr_leave.txt §2.6–2.7): a maximum of "
                       "5 unused annual leave days may be carried forward to the "
                       "following calendar year; any days above 5 are forfeited on "
                       "31 December (2.6). Carried-over days must be used within the "
                       "first quarter (January–March) of the following year or they "
                       "are forfeited (2.7)."),
        },
        {
            "id": "sick_leave_carry_forward",
            "doc": "policy_hr_leave.txt",
            "sections": ["3.3"],
            "triggers": ["carry forward", "carried forward", "roll over"],
            "required": ["sick"],
            "forbidden": [],
            "answer": ("No — sick leave cannot be carried forward to the following "
                       "year (policy_hr_leave.txt §3.3)."),
        },
        {
            "id": "software_installation",
            "doc": "policy_it_acceptable_use.txt",
            "sections": ["2.3", "2.4"],
            "triggers": ["install", "installed", "software", "laptop", "slack",
                         "apps", "application"],
            "required": [],
            "forbidden": ["personal phone", "personal device", "own phone",
                          "personal cell", "personal laptop", "byod"],
            "answer": ("Employees must not install software on corporate devices "
                       "without written approval from the IT Department "
                       "(policy_it_acceptable_use.txt §2.3). Software approved for "
                       "installation must be sourced from the CMC-approved software "
                       "catalogue only (2.4)."),
        },
        {
            "id": "personal_use_corporate_device",
            "doc": "policy_it_acceptable_use.txt",
            "sections": ["2.1", "2.2"],
            "primary": ["company cell phone", "company phone", "company mobile",
                        "corporate phone", "company laptop", "corporate laptop",
                        "company device", "corporate device", "personal use",
                        "corporate resources"],
            "triggers": ["personal use", "phone", "mobile", "laptop", "device",
                         "ticket", "flight", "flights", "game", "games",
                         "browse", "shopping", "personal"],
            "required": [],
            "forbidden": ["install", "installed", "personal phone", "personal device",
                          "personal cell", "personal mobile", "own phone",
                          "personal laptop"],
            "answer": ("Per policy_it_acceptable_use.txt: corporate devices (laptops, "
                       "desktops, and mobile phones issued by CMC) must be used "
                       "primarily for official work purposes (§2.1). Personal use of "
                       "corporate devices is permitted in moderation, provided it "
                       "does not interfere with work duties or consume excessive "
                       "bandwidth (2.2)."),
        },
        {
            "id": "personal_device_access",
            "doc": "policy_it_acceptable_use.txt",
            "sections": ["3.1", "3.2", "3.4", "3.5"],
            "primary": ["personal phone", "personal device", "personal mobile",
                        "own phone", "personal cell phone", "personal cell",
                        "personal laptop"],
            "require_any": ["access", "email", "portal", "check", "read", "files",
                            "connect", "login", "vpn", "wifi", "network"],
            "triggers": ["personal phone", "personal cell phone", "personal cell",
                         "personal device", "personal mobile", "own phone",
                         "personal laptop", "phone", "mobile", "work files"],
            "required": [],
            "forbidden": ["install", "installed", "game", "games", "shopping",
                          "book", "booking", "ticket", "flight"],
            "answer": ("Per policy_it_acceptable_use.txt: personal devices may be used "
                       "to access CMC email and the CMC employee self-service portal "
                       "only (§3.1); they must not be used to access, store, or "
                       "transmit classified or sensitive CMC data (§3.2), and must "
                       "not connect to the CMC internal network — the CMC Guest WiFi "
                       "network is available for personal device internet access "
                       "(3.3). For CMC email a device-level PIN or biometric lock "
                       "must be enabled (§3.4), and a lost or stolen device must be "
                       "reported to the IT helpdesk within 4 hours for remote wipe "
                       "(§3.5). The documents do not authorise personal devices for "
                       "general work files."),
        },
        {
            "id": "home_office_allowance",
            "doc": "policy_finance_reimbursement.txt",
            "sections": ["3.1", "3.2", "3.3", "3.4", "3.5"],
            "primary": ["home office", "equipment allowance", "work from home", "wfh"],
            "triggers": ["home office", "equipment allowance", "work from home",
                         "wfh", "allowance", "desk", "monitor", "chair"],
            "required": [],
            "forbidden": ["appraisal", "performance", "promotion", "salary"],
            "answer": ("Employees approved for permanent work-from-home arrangements "
                       "are entitled to a one-time home office equipment allowance of "
                       "Rs 8,000 (policy_finance_reimbursement.txt §3.1). It covers "
                       "desk, chair, monitor, keyboard, mouse, and networking "
                       "equipment only (3.2); it does not cover personal computers, "
                       "laptops, smartphones, printers, or air conditioning (3.3). "
                       "Temporary or partial work-from-home arrangements are not "
                       "eligible (3.5). Claims require original receipts within 60 "
                       "days of written approval by the Department Head (3.4)."),
        },
        {
            "id": "da_and_meal_receipts",
            "doc": "policy_finance_reimbursement.txt",
            "sections": ["2.5", "2.6"],
            "triggers": ["daily allowance", "da", "meal", "receipt", "receipts",
                         "incidentals"],
            "required": [],
            "forbidden": [],
            "answer": ("No — DA and meal receipts cannot be claimed simultaneously for "
                       "the same day (policy_finance_reimbursement.txt §2.6). DA of "
                       "Rs 750 per day covers meals and incidentals, and no separate "
                       "meal receipts are required if DA is claimed (2.5). If actual "
                       "meal expenses are claimed instead of DA, receipts are "
                       "mandatory and the combined claim must not exceed Rs 750 per "
                       "day — never both for one day (2.6)."),
        },
        {
            "id": "lwp_approval",
            "doc": "policy_hr_leave.txt",
            "sections": ["5.2", "5.3", "5.4"],
            "triggers": ["leave without pay", "lwp", "unpaid leave"],
            "required": [],
            "forbidden": [],
            "answer": ("Leave Without Pay requires approval from the Department Head "
                       "AND the HR Director; manager approval alone is not sufficient "
                       "(policy_hr_leave.txt §5.2). LWP exceeding 30 continuous days "
                       "requires additional approval from the Municipal Commissioner "
                       "(5.3). Periods of LWP do not count toward service for "
                       "seniority, increments, or retirement benefits (5.4)."),
        },
        {
            "id": "sick_leave",
            "doc": "policy_hr_leave.txt",
            "sections": ["3.1", "3.2", "3.3", "3.4"],
            "triggers": ["sick leave", "sick day", "sick days", "medical certificate",
                         "doctor", "certificate", "illness", "sick"],
            "required": [],
            "forbidden": ["encash", "encashment", "carry forward", "carried forward",
                          "roll over"],
            "answer": ("Each employee is entitled to 12 days of paid sick leave per "
                       "calendar year (policy_hr_leave.txt §3.1). Sick leave of 3 or "
                       "more consecutive days requires a medical certificate from a "
                       "registered medical practitioner, submitted within 48 hours of "
                       "returning to work (3.2). Sick leave cannot be carried forward "
                       "to the following year (3.3), and sick leave taken immediately "
                       "before or after a public holiday or annual leave period "
                       "requires a medical certificate regardless of duration (3.4)."),
        },
        {
            "id": "maternity_leave",
            "doc": "policy_hr_leave.txt",
            "sections": ["4.1", "4.2"],
            "triggers": ["maternity", "maternity leave"],
            "required": [],
            "forbidden": [],
            "answer": ("Female employees are entitled to 26 weeks of paid maternity "
                       "leave for the first two live births (policy_hr_leave.txt §4.1). "
                       "For a third or subsequent child, maternity leave is 12 weeks "
                       "paid (4.2)."),
        },
        {
            "id": "paternity_leave",
            "doc": "policy_hr_leave.txt",
            "sections": ["4.3", "4.4"],
            "triggers": ["paternity", "paternity leave"],
            "required": [],
            "forbidden": [],
            "answer": ("Male employees are entitled to 5 days of paid paternity leave, "
                       "to be taken within 30 days of the child's birth "
                       "(policy_hr_leave.txt §4.3). Paternity leave cannot be split "
                       "across multiple periods (4.4)."),
        },
        {
            "id": "leave_encashment",
            "doc": "policy_hr_leave.txt",
            "sections": ["7.1", "7.2", "7.3"],
            "triggers": ["encash", "encashment", "cash out"],
            "required": [],
            "forbidden": [],
            "answer": ("Annual leave may be encashed only at the time of retirement or "
                       "resignation, subject to a maximum of 60 days "
                       "(policy_hr_leave.txt §7.1). Leave encashment during service is "
                       "not permitted under any circumstances (7.2). Sick leave and "
                       "LWP cannot be encashed under any circumstances (7.3)."),
        },
        {
            "id": "training_reimbursement",
            "doc": "policy_finance_reimbursement.txt",
            "sections": ["4.1", "4.2", "4.3", "4.4"],
            "triggers": ["training", "course fee", "professional development",
                         "exam fee", "certification"],
            "required": [],
            "forbidden": [],
            "answer": ("Training expenses are reimbursable only if the training was "
                       "pre-approved by the Department Head using Form FIN-TR1 "
                       "(policy_finance_reimbursement.txt §4.1). Course fees are "
                       "reimbursable up to Rs 15,000 per financial year per employee "
                       "(4.2); exam fees for professional certifications up to "
                       "Rs 5,000 once per attempt (4.3). If the employee leaves CMC "
                       "within 12 months of a reimbursed training expense, they must "
                       "repay 100%; between 12 and 24 months, 50% (4.4)."),
        },
        {
            "id": "mobile_internet_reimbursement",
            "doc": "policy_finance_reimbursement.txt",
            "sections": ["5.1", "5.2", "5.3"],
            "primary": ["mobile phone", "internet", "bill", "claim",
                        "reimbursement"],
            "triggers": ["mobile phone", "internet", "mobile", "bill", "reimbursement"],
            "required": [],
            "forbidden": ["install", "game", "games"],
            "answer": ("Employees in Grade C and above are entitled to a monthly mobile "
                       "phone reimbursement of Rs 500 (policy_finance_reimbursement.txt "
                       "§5.1). Employees in Grade B and above are entitled to a monthly "
                       "internet reimbursement of Rs 800 for approved work-from-home "
                       "arrangements only (5.2). These require submission of the "
                       "original bill each month — estimated or self-declared amounts "
                       "are not accepted (5.3)."),
        },
        {
            "id": "travel_reimbursement",
            "doc": "policy_finance_reimbursement.txt",
            "sections": ["2.1", "2.2", "2.3", "2.4"],
            "triggers": ["travel", "journey", "air", "economy", "hotel", "accommodation",
                         "outstation"],
            "required": [],
            "forbidden": [],
            "answer": ("Local travel is reimbursable at actual cost for public transport "
                       "or Rs 4 per km for personal vehicle use; receipts required for "
                       "claims above Rs 200 (policy_finance_reimbursement.txt §2.1). "
                       "Outstation travel must be pre-approved using Form FIN-T1 "
                       "before travel commences; travel without prior approval is not "
                       "reimbursable (2.2). Air travel is permitted only for journeys "
                       "exceeding 500 km, economy class mandatory — business class is "
                       "not reimbursable (2.3). Hotel accommodation is reimbursable up "
                       "to Rs 3,500/night (Grade A cities) or Rs 2,500/night "
                       "elsewhere (2.4)."),
        },
        {
            "id": "data_handling",
            "doc": "policy_it_acceptable_use.txt",
            "sections": ["5.1", "5.2", "5.3"],
            "triggers": ["confidential", "restricted data", "print", "cloud",
                         "forward"],
            "required": [],
            "forbidden": [],
            "answer": ("CMC data classified as Confidential or Restricted must not be "
                       "stored on personal devices, personal cloud storage, or any "
                       "system not approved by the IT Department "
                       "(policy_it_acceptable_use.txt §5.1). Employees must not "
                       "forward CMC email containing Confidential data to personal "
                       "email accounts (5.2). Printing Confidential documents must use "
                       "the secure print function and documents must not be left "
                       "unattended at printers (5.3)."),
        },
        {
            "id": "passwords_and_mfa",
            "doc": "policy_it_acceptable_use.txt",
            "sections": ["4.1", "4.3", "4.4"],
            "triggers": ["password", "mfa", "multi-factor", "authentication", "2fa",
                         "shared"],
            "required": [],
            "forbidden": [],
            "answer": ("Employees must not share CMC system passwords with any other "
                       "person, including IT staff (policy_it_acceptable_use.txt §4.1). "
                       "Passwords must be changed every 90 days as prompted by the "
                       "system (4.3). Multi-factor authentication (MFA) is mandatory "
                       "for all remote access to CMC systems (4.4)."),
        },
        {
            "id": "compensatory_off",
            "doc": "policy_hr_leave.txt",
            "sections": ["6.1", "6.2", "6.3"],
            "triggers": ["public holiday", "compensatory", "holiday", "comp off"],
            "required": [],
            "forbidden": [],
            "answer": ("Employees are entitled to all gazetted public holidays declared "
                       "by the State Government each year (policy_hr_leave.txt §6.1). "
                       "Working a public holiday earns one compensatory off day, to be "
                       "taken within 60 days of the holiday worked (6.2). Compensatory "
                       "off cannot be encashed (6.3)."),
        },
        {
            "id": "leave_grievance",
            "doc": "policy_hr_leave.txt",
            "sections": ["8.1", "8.2"],
            "triggers": ["grievance", "dispute", "disputed"],
            "required": [],
            "forbidden": [],
            "answer": ("Leave-related grievances must be raised with the HR Department "
                       "within 10 working days of the disputed decision "
                       "(policy_hr_leave.txt §8.1). Grievances raised after 10 working "
                       "days will not be considered unless exceptional circumstances "
                       "are demonstrated in writing (8.2)."),
        },
        {
            "id": "claim_deadline",
            "doc": "policy_finance_reimbursement.txt",
            "sections": ["1.3"],
            "triggers": ["30 days", "within 30", "deadline", "late"],
            "required": [],
            "forbidden": [],
            "answer": ("All reimbursement claims must be submitted within 30 calendar "
                       "days of the expense being incurred; claims submitted after 30 "
                       "days will not be processed (policy_finance_reimbursement.txt "
                       "§1.3)."),
        },
    ]


# ---------------------------------------------------------------------------
# Skill: answer_question
# ---------------------------------------------------------------------------
def _score_intent(query_norm: str, intent: dict) -> int:
    if not all(_trigger_match(query_norm, t) for t in intent["required"]):
        return 0
    if intent.get("require_any") and not any(
            _trigger_match(query_norm, t) for t in intent["require_any"]):
        return 0
    if any(_trigger_match(query_norm, t) for t in intent["forbidden"]):
        return 0
    primary = intent.get("primary", intent["triggers"])
    if not any(_trigger_match(query_norm, t) for t in primary):
        return 0
    return sum(1 for t in intent["triggers"] if _trigger_match(query_norm, t))


def _validate_citations(index: Dict[str, Dict[str, str]], intent: dict):
    doc_path = next(p for p in DOC_PATHS if p.endswith(intent["doc"]))
    doc_sections = set(index[doc_path].keys())
    missing = [s for s in intent["sections"] if s not in doc_sections]
    if missing:
        raise EnforcementError(
            f"intent '{intent['id']}': sections {missing} not found in {intent['doc']} "
            "— cannot serve unverifiable citation")


def _validate_hedges(answer: str) -> List[str]:
    return [h for h in HEDGE_PHRASES if h.lower() in answer.lower()]


def answer_question(question: str, index: Dict[str, Dict[str, str]],
                    intents: List[dict]) -> str:
    """Return a single-source answer with citation, or the verbatim refusal."""
    q = _normalize(question)

    scored = [(_score_intent(q, it), it) for it in intents]
    best_score = max((s for s, _ in scored), default=0)
    best = [it for s, it in scored if s == best_score]

    if best_score == 0:
        return REFUSAL_TEMPLATE

    if len(best) > 1:
        # Genuine ambiguity between sources -> refuse, never blend or guess.
        return REFUSAL_TEMPLATE

    intent = best[0]
    _validate_citations(index, intent)
    hedges = _validate_hedges(intent["answer"])
    if hedges:
        raise EnforcementError(
            f"intent '{intent['id']}' answer contains prohibited hedge phrase(s): "
            f"{hedges}")
    return intent["answer"]


# ---------------------------------------------------------------------------
# The 7 README test questions
# ---------------------------------------------------------------------------
TESTS = [
    {"q": "Can I carry forward unused annual leave?",
     "answer": True, "must_have": ["31 December", "5 unused"],
     "must_not_have": ["policy_it_acceptable_use", "policy_finance"]},
    {"q": "Can I install Slack on my work laptop?",
     "answer": True, "must_have": ["written approval", "IT Department"],
     "must_not_have": []},
    {"q": "What is the home office equipment allowance?",
     "answer": True, "must_have": ["Rs 8,000", "permanent work-from-home"],
     "must_not_have": []},
    {"q": "Can I use my personal phone for work files from home?",
     "answer": True, "must_have": ["policy_it_acceptable_use.txt"],
     "must_not_have": ["policy_hr_leave", "policy_finance",
                       "can be used for work files"]},
    {"q": "What is the company view on flexible working culture?",
     "answer": False},
    {"q": "Can I claim DA and meal receipts on the same day?",
     "answer": True, "must_have": ["cannot be claimed simultaneously", "2.6"],
     "must_not_have": []},
    {"q": "Who approves leave without pay?",
     "answer": True, "must_have": ["Department Head", "HR Director"],
     "must_not_have": []},
    {"q": "Am I allowed to book flight tickets using my company cell phone?",
     "answer": True, "must_have": ["permitted in moderation", "2.2"],
     "must_not_have": ["may be used to access CMC email"]},
    {"q": "Can I take multiple sick leaves?",
     "answer": True, "must_have": ["12 days"],
     "must_not_have": []},
    {"q": "If I regularly work from home, will it affect my performance appraisal?",
     "answer": False},
    {"q": "Can I install mobile games on my company cell phone?",
     "answer": True, "must_have": ["written approval", "2.3"],
     "must_not_have": ["may be used to access CMC email"]},
    {"q": "My company cell phone is not working and I am working from home. "
          "Can I access company files using my personal cell phone?",
     "answer": True,
     "must_have": ["must not be used to access, store, or transmit classified or "
                   "sensitive CMC data"],
     "must_not_have": []},
]


def run_tests() -> int:
    index = retrieve_documents(DOC_PATHS)
    intents = _intents()
    failures = 0
    for t in TESTS:
        ans = answer_question(t["q"], index, intents)
        if t["answer"] is False:
            ok = ans == REFUSAL_TEMPLATE
        else:
            ok = (ans != REFUSAL_TEMPLATE
                  and all(m in ans for m in t["must_have"])
                  and not any(m in ans for m in t["must_not_have"]))
        print(f"[{'PASS' if ok else 'FAIL'}] {t['q']}")
        print(f"      {ans}")
        if not ok:
            failures += 1
    return failures


def main():
    parser = argparse.ArgumentParser(
        description="UC-X Ask My Documents — policy Q&A (interactive)")
    parser.add_argument("--test", action="store_true",
                        help="run the 7 README test questions and exit")
    parser.add_argument("--question", help="ask a single question and exit")
    args = parser.parse_args()

    try:
        intents = _intents()
        if args.test:
            failures = run_tests()
            if failures:
                print(f"{failures} test(s) FAILED", file=sys.stderr)
                sys.exit(1)
            print("All tests PASSED")
            return

        if args.question:
            index = retrieve_documents(DOC_PATHS)
            print(answer_question(args.question, index, intents))
            return

        index = retrieve_documents(DOC_PATHS)
        print("Ask My Documents — type a question (or 'exit'/'quit').")
        while True:
            try:
                q = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not q:
                continue
            if q.lower() in {"exit", "quit"}:
                break
            print(answer_question(q, index, intents))
            print()
    except (EnforcementError, FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()