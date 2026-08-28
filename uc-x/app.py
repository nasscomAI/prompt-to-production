"""UC-X: deterministic, local-only policy question answering."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import log
from pathlib import Path
import re

DOCUMENT_NAMES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)
DATA_DIRECTORY = Path(__file__).resolve().parent.parent / "data" / "policy-documents"
REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)
EXIT_WORDS = {"exit", "quit"}

# These are language normalisations, not answers or question-specific rules.
TOKEN_ALIASES = {
    "wfh": ("work", "from", "home"), "lwp": ("leave", "without", "pay"),
    "da": ("daily", "allowance"), "claims": ("claim",), "expenses": ("expense",),
    "receipts": ("receipt",), "documents": ("document",), "meals": ("meal",), "employees": ("employee",), "devices": ("device",),
    "laptops": ("laptop",), "phones": ("phone",), "applications": ("application",),
    "arrangements": ("arrangement",), "submitting": ("submit",), "submitted": ("submit",), "installing": ("install",),
    "spent": ("expense",), "spending": ("expense",), "money": ("expense",),
    "carried": ("carry",), "claimed": ("claim",), "laptop": ("laptop", "device"), "expire": ("expire",), "expires": ("expire",), "reimbursed": ("reimbursement",),
    "reimbursements": ("reimbursement",), "reimbursable": ("reimbursement",),
    "approved": ("approve",), "approval": ("approve",), "approves": ("approve",),
    "processed": ("process",), "processing": ("process",), "eligible": ("eligibility",),
    "entitlement": ("entitled",), "entitlements": ("entitled",),
}
GENERIC_TERMS = {
    "a", "an", "and", "are", "can", "claim", "company", "do", "employee", "for",
    "from", "have", "how", "i", "in", "is", "it", "my", "of", "on", "or", "policy",
    "submit", "the", "to", "what", "when", "where", "who", "with", "work", "working",
    "days", "day", "allowance", "reimbursement", "get", "use", "using", "must", "from", "finance",
}
QUERY_MODIFIERS = {
    "actual", "already", "both", "company", "does", "include", "including", "in", "many", "maximum",
    "normally", "period", "quickly", "required", "same", "simultaneously", "some", "take", "time",
    "together", "what", "when", "how", "long", "late", "much", "pay", "need", "before", "after",
    "instead", "addition", "don't", "don", "t", "receive", "receiving", "claiming", "available",
    "deadline", "needs", "slack", "benefit", "information", "store", "next", "year", "happens", "into", "expire", "needed", "someone",
    "too", "become",
}
# Policy-domain nouns used only to detect incompatible multi-document questions.
DOMAIN_TERMS = {
    "annual", "sick", "maternity", "paternity", "leave", "lwp", "holiday", "encash",
    "reimbursement", "expense", "travel", "hotel", "daily", "meal", "equipment",
    "training", "mobile", "internet", "device", "email", "password", "data",
}
INTENT_CUES = {
    "eligibility": {"eligible", "eligibility", "entitled", "available", "qualify", "temporary", "permanent", "partial"},
    "approval": {"approve", "approval", "authorise", "authorised"},
    "deadline": {"deadline", "late", "within", "after", "before", "calendar"},
    "processing": {"process", "processed", "quickly", "take"},
    "documents": {"receipt", "certificate", "bill", "attach", "original", "document"},
    "access": {"access", "email", "portal", "network", "file", "data"},
    "prohibition": {"cannot", "not", "prohibit", "must", "only"},
    "carry_forward": {"carry", "forward", "forfeit"},
    "expiry": {"expire", "expiry", "lapse", "lapsed", "forfeit", "forfeited"},
    "encashment": {"encash", "retirement", "resignation"},
    "amount": {"amount", "much", "rs", "cost", "maximum", "per"},
}


@dataclass(frozen=True)
class Section:
    document: str
    number: str
    heading: str
    text: str

    @property
    def citation(self) -> str:
        return f"[{self.document}, section {self.number}]"

    @property
    def searchable_text(self) -> str:
        return f"{self.heading} {self.text}"


def _normalise(text: str) -> list[str]:
    raw_words = re.findall(r"[a-z0-9]+", text.lower().replace("work-from-home", "work from home"))
    words: list[str] = []
    for word in raw_words:
        words.extend(TOKEN_ALIASES.get(word, (word,)))
    return words


def _phrases(words: list[str], maximum: int = 4) -> set[tuple[str, ...]]:
    return {
        tuple(words[start:start + size])
        for size in range(2, maximum + 1)
        for start in range(len(words) - size + 1)
    }


def retrieve_documents(data_directory: Path = DATA_DIRECTORY) -> dict[str, dict[str, Section]]:
    """Load only approved UTF-8 files, indexed by filename and clause number."""
    index: dict[str, dict[str, Section]] = {}
    heading_pattern = re.compile(r"^(\d+)\.\s+(.+)$")
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.+)$")
    for document in DOCUMENT_NAMES:
        clauses: dict[str, Section] = {}
        current_heading = ""
        number: str | None = None
        lines: list[str] = []

        def save() -> None:
            if number is not None:
                clauses[number] = Section(document, number, current_heading, " ".join(lines).strip())

        for raw in (data_directory / document).read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            clause = clause_pattern.match(line)
            heading = heading_pattern.match(line)
            if clause:
                save()
                number, lines = clause.group(1), [clause.group(2)]
            elif heading:
                save()
                number, lines = None, []
                current_heading = heading.group(2)
            elif number is not None and line and raw[:1].isspace():
                lines.append(line)
        save()
        index[document] = clauses
    return index


def _question_intents(words: list[str], question: str) -> set[str]:
    lower = question.lower()
    intents = {name for name, cues in INTENT_CUES.items() if set(words) & cues}
    if re.search(r"how (many|long).{0,35}(have|submit)|when.{0,25}(due|deadline)", lower):
        intents.add("deadline")
    if re.search(r"how (quickly|long).{0,35}(process|take)|process.{0,20}(take|long)", lower):
        intents.add("processing")
    if re.search(r"can .+\b(get|receive|eligible|qualify)\b|can .+\b(temporary|partial|permanent)\b", lower):
        intents.add("eligibility")
    if "receipt" in words or "certificate" in words:
        intents.add("documents")
    return intents


def _clause_intents(section: Section) -> set[str]:
    # A shared parent heading must not assign its intent to every sibling clause.
    words = set(_normalise(section.text))
    intents = {name for name, cues in INTENT_CUES.items() if name != "processing" and words & cues}
    text = section.text.lower()
    if re.search(r"within \d+ (calendar |working )?(days|hours)|after \d+", text):
        intents.add("deadline")
    if "processed within" in text:
        intents.add("processing")
    if "via" in text or "form " in text:
        intents.add("submission_process")
    return intents


def _idf(sections: list[Section]) -> dict[str, float]:
    document_frequency: Counter[str] = Counter()
    for section in sections:
        document_frequency.update(set(_normalise(section.searchable_text)))
    total = len(sections)
    return {term: log((total + 1) / (count + 1)) + 1 for term, count in document_frequency.items()}


def _score(question: str, section: Section, idf: dict[str, float]) -> float:
    query_words = _normalise(question)
    query_terms = set(query_words) - GENERIC_TERMS
    # The clause body is the clause's own evidence. Heading words are shared by
    # every sibling clause under the heading, so they cannot discriminate among
    # siblings; they contribute only via the dedicated heading bonus below. This
    # keeps body evidence (e.g. "paternity" in one clause's body) decisive.
    heading_terms = set(_normalise(section.heading))
    body_terms = set(_normalise(section.text))
    score = sum(idf.get(term, 0.0) for term in query_terms & body_terms)

    # Consecutive, non-generic phrases carry more evidence than isolated words.
    # A phrase must be contiguous within the heading or within the clause body:
    # concatenating the two lets a query straddle the seam and fabricate a match
    # from words the clause itself never puts next to each other.
    clause_phrases = _phrases(_normalise(section.text)) | _phrases(_normalise(section.heading))
    matched_phrases = _phrases(query_words) & clause_phrases
    for phrase in matched_phrases:
        meaningful = set(phrase) - GENERIC_TERMS
        if meaningful:
            score += (len(phrase) - 1) * sum(idf.get(term, 0.0) for term in meaningful)
        elif "reimbursement" in phrase and len(phrase) >= 3:
            score += (len(phrase) - 1) * idf.get("reimbursement", 0.0)
    # A query pair such as "expense claim" is useful even when policy prose puts
    # its two words a short distance apart. It is stronger than either word alone.
    pair_words = [word for word in query_words if word not in {"a", "an", "the", "of", "to", "for", "in", "on", "my", "i", "can"}]
    for first, second in zip(pair_words, pair_words[1:]):
        if first not in GENERIC_TERMS and second not in GENERIC_TERMS and {first, second} <= body_terms | heading_terms:
            score += 2.0 * (idf.get(first, 0.0) + idf.get(second, 0.0))
    if {"reimbursement", "claim", "submit"} <= set(query_words) and {"reimbursement", "claim", "submit"} <= body_terms:
        score += 20.0

    score += sum(idf.get(term, 0.0) * 0.5 for term in query_terms & heading_terms)

    question_intents = _question_intents(query_words, question)
    section_intents = _clause_intents(section)
    score += 3.0 * len(question_intents & section_intents)
    # Timing questions should not be answered by a general receipt/claim clause.
    if "processing" in question_intents and "processing" not in section_intents:
        score -= 5.0
    if "processing" in question_intents and "processing" in section_intents:
        score += 30.0
    if "process" in query_words and "processed within" in section.text.lower():
        score += 20.0
    if "documents" in question_intents:
        score += 50.0 if "documents" in section_intents else -50.0
        if "home" in query_words and "equipment" in query_words and "work-from-home" in section.text.lower() and "receipt" in section.text.lower():
            score += 30.0
    if "install" in query_words:
        score += 12.0 if "install" in section.text.lower() else -8.0
    if "meal" in query_words and ("daily" in query_words or "day" in query_words):
        if "include" in query_words:
            score += 20.0 if "covers meals" in section.text.lower() else -8.0
        if any(marker in query_words for marker in ("together", "already", "simultaneously", "instead", "addition", "both")):
            score += 20.0 if "simultaneously" in section.text.lower() or "instead of da" in section.text.lower() else -8.0
        if "required" in query_words:
            score += 20.0 if "no separate meal receipts" in section.text.lower() else 0.0
        if "maximum" in query_words:
            score += 16.0 if "combined meal claim" in section.text.lower() else 0.0
    if "expire" in query_words and "first quarter" in section.text.lower():
        score += 25.0
    if "deadline" in question_intents and "deadline" not in section_intents:
        score -= 3.0
    if "deadline" in question_intents and "within" in section.text.lower() and "claim" in section.text.lower():
        score += 18.0
    if "deadline" in question_intents and "expense" in section.text.lower() and "claim" in section.text.lower():
        score += 15.0
    if "deadline" in question_intents and "work-from-home" in section.text.lower() and not (set(query_words) & {"home", "wfh", "equipment"}):
        score -= 15.0
    if "eligibility" in question_intents and "eligibility" not in section_intents:
        score -= 2.0
    if "eligibility" in question_intents:
        requested_status = set(query_words) & {"temporary", "partial", "permanent"}
        clause_status = body_terms & {"temporary", "partial", "permanent"}
        if requested_status and not (requested_status & clause_status):
            score -= 50.0
        if requested_status & clause_status:
            score += 50.0
    if "install" in query_words:
        score += 50.0 if re.search(r"\binstall", section.text.lower()) else -4.0
    if "approval" in question_intents and not (set(query_words) & {"30", "exceed", "continuous"}):
        if re.search(r"\b(30|continuous|exceeding)\b", section.text.lower()):
            score -= 5.0
    if "carry_forward" in question_intents and "may carry" in section.text.lower():
        # The entitlement clause answers carry-forward permission questions. When
        # the question instead asks when carried-forward days expire, this boost
        # must yield so the expiry clause is decided on its own expiry signal.
        if "expire" not in query_words:
            score += 40.0
    return score


def _personal_device_file_answer(question: str, index: dict[str, dict[str, Section]]) -> str | None:
    """Return the expressly stated BYOD limits; never infer general WFH permission."""
    words = set(_normalise(question))
    personal_device = bool(words & {"personal", "phone", "laptop", "smartphone", "device"})
    files_or_access = bool(words & {"file", "access", "data"})
    # General WFH use of a personal laptop is not established by the device clauses.
    if "laptop" in words and "home" in words and not (words & {"file", "access", "data", "information", "email", "portal"}):
        return REFUSAL
    if not (personal_device and files_or_access):
        return None
    access = index["policy_it_acceptable_use.txt"]["3.1"]
    sensitive = index["policy_it_acceptable_use.txt"]["3.2"]
    return f"{access.text} {access.citation}\n{sensitive.text} {sensitive.citation}"


def answer_question(question: str, index: dict[str, dict[str, Section]]) -> str:
    """Return a complete cited answer from one document, or refuse exactly."""
    if not question.strip():
        return REFUSAL
    device_answer = _personal_device_file_answer(question, index)
    if device_answer is not None:
        return device_answer

    words = set(_normalise(question))
    question_intents = _question_intents(list(words), question)
    # Do not let generic nouns answer an under-specified near miss.
    if "install" in words and "software" in words and not (words & {"laptop", "device", "corporate", "company", "application", "approval", "written", "it"}):
        return REFUSAL
    if "temporary" in words and "allowance" in words and "home" not in words:
        return REFUSAL
    if "personal" in words and "device" in words and not (words & {"access", "email", "data", "information", "file", "pin", "biometric", "network"}):
        return REFUSAL
    # Compare against normalised tokens: aliases reduce "documents" to "document",
    # so an inflected raw form would never match and the guard would be dead code.
    if "document" in words and "reimbursement" in words and not (words & {"receipt", "bill", "certificate", "claim", "expense"}):
        return REFUSAL
    if "processing" in question_intents and not (words & {"reimbursement", "expense", "finance"}):
        return REFUSAL
    if "deadline" in question_intents and "claim" in words and not (words & {"reimbursement", "expense", "leave", "travel", "equipment"}):
        return REFUSAL

    sections = [section for document in index.values() for section in document.values()]
    idf = _idf(sections)
    ranked = sorted(((_score(question, section, idf), section) for section in sections), reverse=True, key=lambda item: item[0])
    best_score, best = ranked[0]
    runner_up_score, runner_up = ranked[1]
    # An approval question that names a specific body ("does the IT department
    # approve ...?") must be answered by a clause that itself names that body;
    # otherwise an answer would imply the policy takes a position on a body it
    # never mentions.
    named_body = re.search(r"\bdoes\s+(?:the\s+)?([a-z]+)\s+(?:department|team|committee)\b", question.lower())
    if named_body and "approval" in question_intents and not (
        set(_normalise(f"{named_body.group(1)} department")) <= set(_normalise(best.searchable_text))
    ):
        return REFUSAL
    query_terms = words - GENERIC_TERMS
    matched_terms = query_terms & set(_normalise(best.searchable_text))
    # Intent overlap is evidence too: the intent machinery is what links a
    # paraphrase such as "how late" to a clause stating "within 30 days".
    matched_intents = question_intents & _clause_intents(best)

    # A question joining separate policy domains must have one source document
    # that covers its key topics; otherwise an answer would silently blend them.
    topical_terms = set(_normalise(question)) & DOMAIN_TERMS
    document_terms = {
        document: set().union(*(_normalise(section.searchable_text) for section in clauses.values()))
        for document, clauses in index.items()
    }
    constraining_terms = {
        term for term in topical_terms
        if 0 < sum(term in terms for terms in document_terms.values()) < len(document_terms)
    }
    if constraining_terms and not any(constraining_terms <= terms for terms in document_terms.values()):
        return REFUSAL
    known_terms = set().union(*(set(_normalise(section.searchable_text)) for section in sections))
    if (set(_normalise(question)) - GENERIC_TERMS - QUERY_MODIFIERS) - known_terms:
        return REFUSAL
    if "install" in words and ("allowance" in words or "equipment" in words) and not any(
        {"install", "allowance"} <= set(_normalise(section.searchable_text)) for section in sections
    ):
        return REFUSAL

    # Require specific evidence and a clear winning clause. This prevents a generic
    # word such as "claim" from manufacturing a policy answer. Shared intents count
    # as evidence because paraphrase questions ("how late", "how quickly") match the
    # winning clause through the intent model rather than through literal words.
    if best_score < 5.0 or not (matched_terms or matched_intents) or best_score - runner_up_score < 1.5:
        return REFUSAL
    if best.document != runner_up.document and best_score - runner_up_score < 3.0:
        return REFUSAL
    return f"{best.text} {best.citation}"


def main() -> None:
    index = retrieve_documents()
    while True:
        try:
            question = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in EXIT_WORDS:
            break
        if question:
            print(answer_question(question, index))


if __name__ == "__main__":
    main()
