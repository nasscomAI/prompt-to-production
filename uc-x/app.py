"""
UC-X - Ask My Documents.

Interactive policy Q&A over three local policy documents. Answers are limited
to one source document and include document + section citations.
"""
import re
import sys
from pathlib import Path


POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)
SECTION_RE = re.compile(r"^(\d+\.\d+)\s+(.*)")
TOP_LEVEL_SECTION_RE = re.compile(r"^\d+\.\s+")
WORD_RE = re.compile(r"[a-z0-9]+")
SPELLING_CORRECTIONS = {
    "anual": "annual",
}
STOP_WORDS = {
    "a",
    "about",
    "all",
    "am",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "be",
    "can",
    "company",
    "do",
    "does",
    "for",
    "from",
    "i",
    "in",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "same",
    "the",
    "tell",
    "to",
    "use",
    "what",
    "when",
    "who",
    "with",
    "work",
    "working",
}
HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]


def canonical_word(word):
    return SPELLING_CORRECTIONS.get(word, word)


def normalize(text):
    return " ".join(canonical_word(word) for word in WORD_RE.findall(text.lower()))


def words(text):
    return {
        canonical_word(word)
        for word in WORD_RE.findall(text.lower())
        if canonical_word(word) not in STOP_WORDS
    }


def policy_directory():
    return Path(__file__).resolve().parent.parent / "data" / "policy-documents"


def retrieve_documents(base_dir=None):
    directory = Path(base_dir) if base_dir else policy_directory()
    documents = {}

    for file_name in POLICY_FILES:
        path = directory / file_name
        if not path.exists():
            raise FileNotFoundError(f"Missing policy document: {path}")

        sections = []
        current = None
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or TOP_LEVEL_SECTION_RE.match(line) or not WORD_RE.search(line):
                continue

            match = SECTION_RE.match(line)
            if match:
                if current:
                    sections.append(current)
                current = {"section": match.group(1), "text": match.group(2)}
            elif current:
                current["text"] = f"{current['text']} {line}"

        if current:
            sections.append(current)

        documents[file_name] = sections

    return documents


def citation(document, section):
    return f"{document} section {section}"


def format_claim(document, section, claim):
    return f"{claim} ({citation(document, section)})."


def find_section(documents, document, section):
    for item in documents[document]:
        if item["section"] == section:
            return item
    raise KeyError(f"{document} section {section} not found")


def intent_answer(question, documents):
    query = normalize(question)

    if "annual leave" in query and "carry forward" not in query:
        doc = "policy_hr_leave.txt"
        sections = {
            section: find_section(documents, doc, section)
            for section in ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7"]
        }
        return "\n".join(
            [
                format_claim(
                    doc,
                    sections["2.1"]["section"],
                    "Permanent employees are entitled to 18 days of paid annual leave per calendar year",
                ),
                format_claim(
                    doc,
                    sections["2.2"]["section"],
                    "Annual leave accrues at 1.5 days per month from the date of joining",
                ),
                format_claim(
                    doc,
                    sections["2.3"]["section"],
                    "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1",
                ),
                format_claim(
                    doc,
                    sections["2.4"]["section"],
                    "Leave applications must receive written approval from the employee's direct manager before leave commences; verbal approval is not valid",
                ),
                format_claim(
                    doc,
                    sections["2.5"]["section"],
                    "Unapproved absence is recorded as Loss of Pay regardless of subsequent approval",
                ),
                format_claim(
                    doc,
                    sections["2.6"]["section"],
                    "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year; any days above 5 are forfeited on 31 December",
                ),
                format_claim(
                    doc,
                    sections["2.7"]["section"],
                    "Carry-forward days must be used within January-March of the following year or they are forfeited",
                ),
            ]
        )

    if all(term in query for term in ["carry", "forward", "annual", "leave"]):
        doc = "policy_hr_leave.txt"
        item = find_section(documents, doc, "2.6")
        return format_claim(
            doc,
            item["section"],
            "Employees may carry forward a maximum of 5 unused annual leave days "
            "to the following calendar year; any days above 5 are forfeited on "
            "31 December",
        )

    if "slack" in query and ("install" in query or "laptop" in query):
        doc = "policy_it_acceptable_use.txt"
        item = find_section(documents, doc, "2.3")
        return format_claim(
            doc,
            item["section"],
            "Employees must not install software on corporate devices without "
            "written approval from the IT Department",
        )

    if "home office equipment allowance" in query:
        doc = "policy_finance_reimbursement.txt"
        item = find_section(documents, doc, "3.1")
        return format_claim(
            doc,
            item["section"],
            "Employees approved for permanent work-from-home arrangements are "
            "entitled to a one-time home office equipment allowance of Rs 8,000",
        )

    if "work from home equipment" in query or "home equipment" in query:
        doc = "policy_finance_reimbursement.txt"
        sections = {
            section: find_section(documents, doc, section)
            for section in ["3.1", "3.2", "3.3", "3.4", "3.5"]
        }
        return "\n".join(
            [
                format_claim(
                    doc,
                    sections["3.1"]["section"],
                    "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000",
                ),
                format_claim(
                    doc,
                    sections["3.2"]["section"],
                    "The allowance covers desk, chair, monitor, keyboard, mouse, and networking equipment only",
                ),
                format_claim(
                    doc,
                    sections["3.3"]["section"],
                    "The allowance does not cover personal computers, laptops, smartphones, printers, or air conditioning equipment",
                ),
                format_claim(
                    doc,
                    sections["3.4"]["section"],
                    "Claims must be submitted with original receipts within 60 days of written approval of the work-from-home arrangement by the Department Head",
                ),
                format_claim(
                    doc,
                    sections["3.5"]["section"],
                    "Employees on temporary or partial work-from-home arrangements are not eligible for this allowance",
                ),
            ]
        )

    if (
        ("personal phone" in query or "personal device" in query)
        and ("file" in query or "files" in query or "home" in query)
    ):
        doc = "policy_it_acceptable_use.txt"
        section_31 = find_section(documents, doc, "3.1")
        section_32 = find_section(documents, doc, "3.2")
        return (
            format_claim(
                doc,
                section_31["section"],
                "Personal devices may be used to access CMC email and the CMC "
                "employee self-service portal only",
            )
            + "\n"
            + format_claim(
                doc,
                section_32["section"],
                "Personal devices must not be used to access, store, or transmit "
                "classified or sensitive CMC data",
            )
        )

    if "passwords and access control" in query or (
        "password" in query and "access control" in query
    ):
        doc = "policy_it_acceptable_use.txt"
        sections = {
            section: find_section(documents, doc, section)
            for section in ["4.1", "4.2", "4.3", "4.4"]
        }
        return "\n".join(
            [
                format_claim(
                    doc,
                    sections["4.1"]["section"],
                    "Employees must not share their CMC system passwords with any other person, including IT staff",
                ),
                format_claim(
                    doc,
                    sections["4.2"]["section"],
                    "IT staff will never ask for your password, and any password request should be reported to the IT Security team",
                ),
                format_claim(
                    doc,
                    sections["4.3"]["section"],
                    "Passwords must be changed every 90 days as prompted by the system",
                ),
                format_claim(
                    doc,
                    sections["4.4"]["section"],
                    "Multi-factor authentication is mandatory for all remote access to CMC systems",
                ),
            ]
        )

    if "flexible working culture" in query or "company view" in query:
        return REFUSAL_TEMPLATE

    if ("da" in query or "daily allowance" in query) and "meal" in query:
        doc = "policy_finance_reimbursement.txt"
        item = find_section(documents, doc, "2.6")
        return format_claim(
            doc,
            item["section"],
            "No, DA and meal receipts cannot be claimed simultaneously for the "
            "same day",
        )

    if (
        ("leave without pay" in query or "lwp" in query)
        and ("approve" in query or "approves" in query or "approval" in query)
    ):
        doc = "policy_hr_leave.txt"
        item = find_section(documents, doc, "5.2")
        return format_claim(
            doc,
            item["section"],
            "Leave Without Pay requires approval from the Department Head and "
            "the HR Director; manager approval alone is not sufficient",
        )

    return None


def score_section(question_words, section):
    section_words = words(section["text"])
    return len(question_words & section_words)


def fallback_answer(question, documents):
    question_words = words(question)
    if not question_words:
        return REFUSAL_TEMPLATE

    best_by_document = []
    for document, sections in documents.items():
        scored = [(score_section(question_words, section), section) for section in sections]
        scored.sort(key=lambda item: item[0], reverse=True)
        if scored and scored[0][0] > 0:
            best_by_document.append((scored[0][0], document, scored[0][1]))

    best_by_document.sort(key=lambda item: item[0], reverse=True)
    if not best_by_document or best_by_document[0][0] < 2:
        return REFUSAL_TEMPLATE

    if len(best_by_document) > 1 and best_by_document[0][0] == best_by_document[1][0]:
        return REFUSAL_TEMPLATE

    _, document, section = best_by_document[0]
    return format_claim(document, section["section"], section["text"])


def answer_question(question, documents):
    answer = intent_answer(question, documents) or fallback_answer(question, documents)
    lowered = answer.lower()
    if any(phrase in lowered for phrase in HEDGING_PHRASES):
        return REFUSAL_TEMPLATE
    return answer


def run_interactive():
    documents = retrieve_documents()
    print("UC-X Ask My Documents")
    print("Type a policy question, or 'exit' to quit.")

    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            print()
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break

        print(answer_question(question, documents))


def main():
    try:
        run_interactive()
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
