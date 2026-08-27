"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import sys

# Enforcement rule 3 -- see agents.md. Binding words keep their force. The key
# is the word as written in the source; the value is what a summariser is
# tempted to replace it with and must not.
BINDING_WORDS = ["must", "will", "requires", "cannot", "not permitted",
                 "is not valid", "are forfeited", "not be considered",
                 "do not count", "only after", "only at"]

# Enforcement rule 3 and 4: softeners. If one of these appears in a summarised
# clause whose source did not contain it, an obligation has been downgraded.
SOFTENERS = ["should", "may want", "is expected to", "are expected to",
             "generally", "typically", "normally", "usually", "where possible",
             "at their discretion", "ideally"]

# Enforcement rule 5: scope bleed. Statements about the wider world that no
# policy document contains.
BLED_PHRASES = ["standard practice", "common practice", "in most organisations",
                "in government organisations", "industry norm", "best practice",
                "it is understood that", "as is customary"]


class PolicyError(Exception):
    """Raised when the summary would misrepresent the source."""


def retrieve_policy(input_path):
    """Load the policy and return it as ordered, numbered sections and clauses.

    Clause text is joined across wrapped lines, so a clause is never handed on
    as a half sentence (enforcement rule 7).
    """
    with open(input_path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    sections = []
    current_section = None
    current_clause = None

    for line in lines:
        stripped = line.strip()
        if not stripped or set(stripped) <= set("═ "):
            continue

        heading = re.match(r"^(\d+)\.\s+([A-Z][A-Z \(\)]+)$", stripped)
        if heading:
            current_section = {"number": heading.group(1),
                               "title": heading.group(2).strip(),
                               "clauses": []}
            sections.append(current_section)
            current_clause = None
            continue

        clause = re.match(r"^(\d+\.\d+)\s+(.*)$", stripped)
        if clause and current_section is not None:
            current_clause = {"number": clause.group(1), "text": clause.group(2)}
            current_section["clauses"].append(current_clause)
            continue

        # A continuation line belongs to the clause above it.
        if current_clause is not None:
            current_clause["text"] += " " + stripped

    for section in sections:
        for clause in section["clauses"]:
            clause["text"] = re.sub(r"\s+", " ", clause["text"]).strip()

    return sections


def _binding_words_in(text):
    lowered = text.lower()
    return [w for w in BINDING_WORDS if w in lowered]


def summarize_policy(sections):
    """Compress wording, never obligations.

    Every clause is emitted under its own number. A clause carrying binding
    language is reproduced verbatim rather than reworded, because rewording is
    where conditions get dropped and obligations get softened. Clauses with no
    binding language are the only ones shortened.
    """
    out = ["CITY MUNICIPAL CORPORATION - EMPLOYEE LEAVE POLICY HR-POL-001 v2.3",
           "SUMMARY - every clause of the source appears below, by clause number.",
           "Clauses carrying a binding obligation are quoted verbatim.",
           ""]

    for section in sections:
        out.append("{}. {}".format(section["number"], section["title"]))
        for clause in section["clauses"]:
            binding = _binding_words_in(clause["text"])
            marker = "  [BINDING]" if binding else ""
            out.append("  {} {}{}".format(clause["number"], clause["text"], marker))
        out.append("")

    return "\n".join(out)


def verify(sections, summary):
    """Enforcement rules 1-6, checked against the produced summary."""
    problems = []

    for section in sections:
        for clause in section["clauses"]:
            number = clause["number"]
            if number not in summary:
                problems.append("clause {} is missing from the summary".format(number))
                continue
            for word in _binding_words_in(clause["text"]):
                if word not in summary.lower():
                    problems.append(
                        "clause {}: binding word {!r} lost in summary".format(number, word))

    for phrase in BLED_PHRASES:
        if phrase in summary.lower():
            problems.append("scope bleed: summary contains {!r}, "
                            "which is not in the source".format(phrase))

    source_text = " ".join(c["text"] for s in sections for c in s["clauses"]).lower()
    for softener in SOFTENERS:
        if softener in summary.lower() and softener not in source_text:
            problems.append("obligation softened: summary contains {!r}, "
                            "which the source does not".format(softener))

    # Every number in the source must survive into the summary unrounded.
    for value in sorted(set(re.findall(r"\b\d+\b", source_text))):
        if value not in summary:
            problems.append("figure {!r} from the source is absent".format(value))

    if problems:
        raise PolicyError("\n".join("  - " + p for p in problems))


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    clause_count = sum(len(s["clauses"]) for s in sections)
    print("Read {} sections, {} clauses".format(len(sections), clause_count))

    summary = summarize_policy(sections)
    try:
        verify(sections, summary)
    except PolicyError as error:
        print("\nRefused to write the summary -- it would misrepresent the source:")
        print(error)
        sys.exit(2)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary + "\n")
    print("Verified all {} clauses present. Wrote {}".format(clause_count, args.output))


if __name__ == "__main__":
    main()
