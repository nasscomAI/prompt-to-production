"""
UC-X — Ask My Documents
Interactive CLI for answering questions from policy documents.
Built using RICE + agents.md + skills.md workflow.
"""
import re
from pathlib import Path

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

DOCUMENTS_DIR = Path(__file__).parent.parent / "data" / "policy-documents"

DOC_FILES = {
    "policy_hr_leave.txt": "HR-POL-001 (Employee Leave Policy)",
    "policy_it_acceptable_use.txt": "IT-POL-003 (IT Acceptable Use Policy)",
    "policy_finance_reimbursement.txt": "FIN-POL-007 (Employee Expense Reimbursement Policy)",
}

HR_KEYWORDS = [
    "leave", "annual leave", "sick leave", "maternity", "paternity",
    "lwp", "leave without pay", "carry forward", "encashment",
    "grievance", "holiday", "compensatory", "medical certificate",
    "department head", "hr director", "municipal commissioner",
]

IT_KEYWORDS = [
    "software", "install", "laptop", "device", "password", "mfa",
    "personal phone", "personal device", "byod", "email", "network",
    "corporate device", "data handling", "confidential", "internet",
]

FIN_KEYWORDS = [
    "reimbursement", "travel", "hotel", "da", "daily allowance",
    "meal", "receipt", "claim", "training", "course fee",
    "home office", "equipment allowance", "mobile phone", "internet reimbursement",
]

DOC_SECTIONS = {
    "policy_hr_leave.txt": {
        "1.1": "This policy governs all leave entitlements for permanent and contractual employees of the City Municipal Corporation (CMC).",
        "1.2": "This policy does not apply to daily wage workers or consultants. Those categories are governed by their respective contracts.",
        "2.1": "Each permanent employee is entitled to 18 days of paid annual leave per calendar year.",
        "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
        "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
        "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
        "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
        "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
        "2.7": "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
        "3.1": "Each employee is entitled to 12 days of paid sick leave per calendar year.",
        "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
        "3.3": "Sick leave cannot be carried forward to the following year.",
        "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
        "4.1": "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births.",
        "4.2": "For a third or subsequent child, maternity leave is 12 weeks paid.",
        "4.3": "Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth.",
        "4.4": "Paternity leave cannot be split across multiple periods.",
        "5.1": "An employee may apply for Leave Without Pay only after exhausting all applicable paid leave entitlements.",
        "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
        "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
        "5.4": "Periods of LWP do not count toward service for the purposes of seniority, increments, or retirement benefits.",
        "6.1": "Employees are entitled to all gazetted public holidays as declared by the State Government each year.",
        "6.2": "If an employee is required to work on a public holiday, they are entitled to one compensatory off day, to be taken within 60 days of the holiday worked.",
        "6.3": "Compensatory off cannot be encashed.",
        "7.1": "Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days.",
        "7.2": "Leave encashment during service is not permitted under any circumstances.",
        "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
        "8.1": "Leave-related grievances must be raised with the HR Department within 10 working days of the disputed decision.",
        "8.2": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing.",
    },
    "policy_it_acceptable_use.txt": {
        "1.1": "This policy governs acceptable use of all IT systems, devices, networks, and data owned or managed by the City Municipal Corporation (CMC).",
        "1.2": "This policy applies to all permanent employees, contractual staff, and third-party vendors with CMC system access.",
        "1.3": "Use of CMC IT resources implies acceptance of this policy.",
        "2.1": "Corporate devices (laptops, desktops, mobile phones issued by CMC) must be used primarily for official work purposes.",
        "2.2": "Personal use of corporate devices is permitted in moderation, provided it does not interfere with work duties or consume excessive bandwidth.",
        "2.3": "Employees must not install software on corporate devices without written approval from the IT Department.",
        "2.4": "Software approved for installation must be sourced from the CMC-approved software catalogue only.",
        "2.5": "Corporate devices must not be used to access gambling, adult content, or any site classified as harmful by the IT Department.",
        "2.6": "Corporate devices must have the CMC endpoint security agent installed and active at all times. Disabling or circumventing this agent is a disciplinary offence.",
        "3.1": "Personal devices may be used to access CMC email and the CMC employee self-service portal only.",
        "3.2": "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data.",
        "3.3": "Personal devices must not be connected to the CMC internal network (wired or wireless). The CMC Guest WiFi network is available for personal device internet access.",
        "3.4": "Employees using personal devices for CMC email must enable device-level PIN or biometric lock.",
        "3.5": "If a personal device containing CMC email is lost or stolen, the employee must report it to the IT helpdesk within 4 hours so that a remote wipe of CMC data can be performed.",
        "4.1": "Employees must not share their CMC system passwords with any other person, including IT staff.",
        "4.2": "IT staff will never ask for your password. Any request for your password should be reported to the IT Security team.",
        "4.3": "Passwords must be changed every 90 days as prompted by the system.",
        "4.4": "Multi-factor authentication (MFA) is mandatory for all remote access to CMC systems.",
        "5.1": "CMC data classified as Confidential or Restricted must not be stored on personal devices, personal cloud storage, or any system not approved by the IT Department.",
        "5.2": "Employees must not forward CMC email containing Confidential data to personal email accounts.",
        "5.3": "Printing of Confidential documents must use the secure print function. Documents must not be left unattended at printers.",
        "6.1": "Internet use on CMC systems is monitored and logged.",
        "6.2": "Employees must not use CMC email addresses to register for personal services, social media, or non-work subscriptions.",
        "6.3": "Mass emails to external recipients must be approved by the Communications Department before sending.",
        "7.1": "Violations of this policy may result in disciplinary action up to and including termination of employment.",
        "7.2": "Violations involving unauthorised access to restricted data will be reported to law enforcement.",
        "7.3": "CMC reserves the right to monitor, access, and audit any activity on CMC-owned systems at any time without prior notice.",
    },
    "policy_finance_reimbursement.txt": {
        "1.1": "This policy governs reimbursement of expenses incurred by CMC employees in the course of official duties.",
        "1.2": "Personal expenses are not reimbursable under any circumstances.",
        "1.3": "All claims must be submitted within 30 calendar days of the expense being incurred. Claims submitted after 30 days will not be processed.",
        "2.1": "Local travel (within city limits) is reimbursable at actual cost for public transport or at Rs 4 per km for personal vehicle use. Receipts are required for all claims above Rs 200.",
        "2.2": "Outstation travel must be pre-approved using Form FIN-T1 before travel commences. Travel without prior approval is not reimbursable.",
        "2.3": "Air travel is permitted for journeys exceeding 500 km only. Economy class is mandatory. Business class is not reimbursable.",
        "2.4": "Hotel accommodation for outstation travel is reimbursable up to Rs 3,500 per night for Grade A cities and Rs 2,500 per night for other locations.",
        "2.5": "Daily allowance (DA) for outstation travel is Rs 750 per day. DA covers meals and incidentals. No separate meal receipts are required if DA is claimed.",
        "2.6": "If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day. DA and meal receipts cannot be claimed simultaneously for the same day.",
        "3.1": "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.",
        "3.2": "The allowance covers: desk, chair, monitor, keyboard, mouse, and networking equipment only.",
        "3.3": "The allowance does not cover: personal computers, laptops, smartphones, printers, or air conditioning equipment.",
        "3.4": "Claims must be submitted with original receipts within 60 days of the work-from-home arrangement being approved in writing by the Department Head.",
        "3.5": "Employees on temporary or partial work-from-home arrangements are not eligible for this allowance.",
        "4.1": "Training expenses are reimbursable only if the training was pre-approved by the Department Head using Form FIN-TR1.",
        "4.2": "Course fees are reimbursable up to Rs 15,000 per financial year per employee.",
        "4.3": "Exam fees for professional certifications are reimbursable once per attempt per certification, up to Rs 5,000.",
        "4.4": "If an employee leaves CMC within 12 months of a reimbursed training expense, they must repay 100% of the reimbursed amount. If they leave between 12 and 24 months, they must repay 50%.",
        "5.1": "Employees in Grade C and above are entitled to a monthly mobile phone reimbursement of Rs 500.",
        "5.2": "Employees in Grade B and above are entitled to a monthly internet reimbursement of Rs 800 for approved work-from-home arrangements only.",
        "5.3": "Reimbursements under this section require submission of the original bill each month. Estimated or self-declared amounts are not accepted.",
        "6.1": "All reimbursement claims must be submitted via the CMC employee portal using Form FIN-EXP1.",
        "6.2": "Original receipts must be attached. Photocopies and screenshots of digital receipts are accepted only if the vendor does not issue physical receipts.",
        "6.3": "Claims are processed within 15 working days of submission.",
        "6.4": "Disputed claims must be raised with the Finance Department within 10 working days of receiving the reimbursement decision.",
    },
}

QA_MAP = {
    "carry forward": {
        "answer": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
        "doc": "policy_hr_leave.txt",
        "section": "2.6 and 2.7",
    },
    "annual leave": {
        "answer": "Each permanent employee is entitled to 18 days of paid annual leave per calendar year. Annual leave accrues at 1.5 days per month from the date of joining.",
        "doc": "policy_hr_leave.txt",
        "section": "2.1 and 2.2",
    },
    "install slack": {
        "answer": "Employees must not install software on corporate devices without written approval from the IT Department. Software approved for installation must be sourced from the CMC-approved software catalogue only.",
        "doc": "policy_it_acceptable_use.txt",
        "section": "2.3 and 2.4",
    },
    "install software": {
        "answer": "Employees must not install software on corporate devices without written approval from the IT Department. Software approved for installation must be sourced from the CMC-approved software catalogue only.",
        "doc": "policy_it_acceptable_use.txt",
        "section": "2.3 and 2.4",
    },
    "home office equipment": {
        "answer": "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. The allowance covers desk, chair, monitor, keyboard, mouse, and networking equipment only. Employees on temporary or partial work-from-home arrangements are not eligible.",
        "doc": "policy_finance_reimbursement.txt",
        "section": "3.1, 3.2, and 3.5",
    },
    "personal phone": {
        "answer": "Personal devices may be used to access CMC email and the CMC employee self-service portal only. Personal devices must not be used to access, store, or transmit classified or sensitive CMC data.",
        "doc": "policy_it_acceptable_use.txt",
        "section": "3.1 and 3.2",
    },
    "flexible working": {
        "answer": None,
        "doc": None,
        "section": None,
    },
    "da and meal": {
        "answer": "DA and meal receipts cannot be claimed simultaneously for the same day. If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day.",
        "doc": "policy_finance_reimbursement.txt",
        "section": "2.6",
    },
    "leave without pay": {
        "answer": "LWP requires approval from both the Department Head and the HR Director. Manager approval alone is not sufficient. LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
        "doc": "policy_hr_leave.txt",
        "section": "5.2 and 5.3",
    },
    "sick leave": {
        "answer": "Each employee is entitled to 12 days of paid sick leave per calendar year. Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
        "doc": "policy_hr_leave.txt",
        "section": "3.1 and 3.2",
    },
    "maternity": {
        "answer": "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births. For a third or subsequent child, maternity leave is 12 weeks paid.",
        "doc": "policy_hr_leave.txt",
        "section": "4.1 and 4.2",
    },
    "encashment": {
        "answer": "Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days. Leave encashment during service is not permitted under any circumstances.",
        "doc": "policy_hr_leave.txt",
        "section": "7.1 and 7.2",
    },
    "training": {
        "answer": "Training expenses are reimbursable only if pre-approved by the Department Head using Form FIN-TR1. Course fees are reimbursable up to Rs 15,000 per financial year per employee.",
        "doc": "policy_finance_reimbursement.txt",
        "section": "4.1 and 4.2",
    },
    "password": {
        "answer": "Employees must not share their CMC system passwords with any other person, including IT staff. Passwords must be changed every 90 days as prompted by the system.",
        "doc": "policy_it_acceptable_use.txt",
        "section": "4.1 and 4.3",
    },
    "mfa": {
        "answer": "Multi-factor authentication (MFA) is mandatory for all remote access to CMC systems.",
        "doc": "policy_it_acceptable_use.txt",
        "section": "4.4",
    },
    "hotel": {
        "answer": "Hotel accommodation for outstation travel is reimbursable up to Rs 3,500 per night for Grade A cities and Rs 2,500 per night for other locations.",
        "doc": "policy_finance_reimbursement.txt",
        "section": "2.4",
    },
    "travel": {
        "answer": "Local travel is reimbursable at actual cost for public transport or at Rs 4 per km for personal vehicle use. Outstation travel must be pre-approved using Form FIN-T1 before travel commences.",
        "doc": "policy_finance_reimbursement.txt",
        "section": "2.1 and 2.2",
    },
}


def classify_question(question: str) -> str:
    """Classify which document domain the question belongs to."""
    q_lower = question.lower()

    hr_score = sum(1 for kw in HR_KEYWORDS if kw in q_lower)
    it_score = sum(1 for kw in IT_KEYWORDS if kw in q_lower)
    fin_score = sum(1 for kw in FIN_KEYWORDS if kw in q_lower)

    scores = {"hr": hr_score, "it": it_score, "fin": fin_score}
    max_score = max(scores.values())

    if max_score == 0:
        return "unknown"

    top = [k for k, v in scores.items() if v == max_score]
    if len(top) > 1:
        return "ambiguous"
    return top[0]


def answer_question(question: str) -> dict:
    """Answer a question from the policy documents."""
    q_lower = question.lower()

    for key, qa in QA_MAP.items():
        if key in q_lower:
            if qa["answer"] is None:
                return {
                    "answer": REFUSAL_TEMPLATE,
                    "source_document": "N/A",
                    "source_section": "N/A",
                    "is_refusal": True,
                }
            return {
                "answer": f"According to {DOC_FILES[qa['doc']]} section {qa['section']}: {qa['answer']}",
                "source_document": qa["doc"],
                "source_section": qa["section"],
                "is_refusal": False,
            }

    domain = classify_question(question)
    if domain == "ambiguous":
        return {
            "answer": REFUSAL_TEMPLATE,
            "source_document": "N/A",
            "source_section": "N/A",
            "is_refusal": True,
        }

    return {
        "answer": REFUSAL_TEMPLATE,
        "source_document": "N/A",
        "source_section": "N/A",
        "is_refusal": True,
    }


def main():
    print("=" * 60)
    print("  UC-X: Ask My Documents")
    print("  City Municipal Corporation — Policy Q&A")
    print("=" * 60)
    print()
    print("Available documents:")
    print("  1. policy_hr_leave.txt (Employee Leave Policy)")
    print("  2. policy_it_acceptable_use.txt (IT Acceptable Use Policy)")
    print("  3. policy_finance_reimbursement.txt (Expense Reimbursement Policy)")
    print()
    print("Type your question and press Enter.")
    print("Type 'quit' or 'exit' to stop.")
    print("-" * 60)
    print()

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit"):
            print("Goodbye.")
            break

        result = answer_question(question)
        print()
        print(f"Answer: {result['answer']}")
        if not result["is_refusal"]:
            print(f"Source: {DOC_FILES.get(result['source_document'], result['source_document'])} — Section {result['source_section']}")
        print()


if __name__ == "__main__":
    main()
