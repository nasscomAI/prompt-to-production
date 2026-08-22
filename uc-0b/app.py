"""UC-0B app.py — meaning-preserving policy summariser (retrieve_policy + summarize_policy)."""
import argparse
import os
import re
import sys

from openai import OpenAI

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^\d+\.\s+\S")
DECOR_RE = re.compile(r"^═+\s*$")
SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "standard practice",
    "typically in government",
    "government organisations",
    "employees are generally expected",
    "generally expected",
    "it is customary",
    "usually",
    "commonly",
]

SYSTEM_PROMPT = """You are a policy-document summariser for City Municipal Corporation HR policies.
Your operational boundary is strictly the content of the supplied source document. You do not
interpret, advise, compare with other organisations, or supplement the policy in any way.

Produce a summary that satisfies ALL of these rules:
1. Every numbered clause present in the source must be represented in the summary with its exact clause reference.
2. Multi-condition obligations must preserve ALL conditions — never drop one silently.
3. Never add information not present in the source document: no outside knowledge, no assumptions
   about "standard practice", no generalisations about government organisations or employers,
   no invented thresholds, approvers, timeframes, forms, or entitlements, no advice or opinions.
4. Binding force is unchanged: must stays must, may stays may, "not permitted" stays not permitted,
   forfeited stays forfeited, LOP stays LOP. Never soften an obligation.
5. If a clause cannot be summarised without meaning loss, quote it verbatim and flag it with [VERBATIM]
   instead of paraphrasing.

Output format: plain text grouped under the source section headings only. One entry per clause, each
entry beginning with its exact clause reference (e.g. "2.3"). Do not merge clauses. Do not invent headings."""


def retrieve_policy(path):
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        sys.exit(f"ERROR retrieve_policy: cannot read input file '{path}': {exc}")
    if not any(line.strip() for line in lines):
        sys.exit(f"ERROR retrieve_policy: input file '{path}' is empty")
    sections = {}
    current = None
    for line in lines:
        stripped = line.strip()
        if DECOR_RE.match(stripped) or not stripped:
            continue
        if SECTION_RE.match(stripped):
            continue
        match = CLAUSE_RE.match(stripped)
        if match:
            current = match.group(1)
            sections[current] = [match.group(2)]
        elif current:
            sections[current].append(stripped)
    if not sections:
        sys.exit("ERROR retrieve_policy: no numbered clauses found in input document")
    return {cid: " ".join(parts).strip() for cid, parts in sections.items()}


def summarize_policy(client, model, sections):
    source_text = "\n".join(f"{cid} {text}" for cid, text in sections.items())
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Summarise this policy document:\n\n{source_text}"},
    ]
    summary = call_llm(client, model, messages)
    for _ in range(2):
        missing = [cid for cid in sections if cid not in summary]
        if not missing:
            break
        repair = (
            "The following clause references are MISSING from your summary. Regenerate the "
            f"complete summary including every one of them with all their conditions intact: "
            f"{', '.join(missing)}.\n\nSource document:\n{source_text}"
        )
        messages.append({"role": "assistant", "content": summary})
        messages.append({"role": "user", "content": repair})
        summary = call_llm(client, model, messages)
    return summary


def call_llm(client, model, messages):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0,
    )
    content = response.choices[0].message.content
    if not content or not content.strip():
        sys.exit("ERROR summarize_policy: model returned an empty response")
    return content.strip()


def audit(summary, sections):
    print("\n=== UC-0B verification report ===")
    covered = [cid for cid in sections if cid in summary]
    missing = [cid for cid in sections if cid not in summary]
    print(f"Clause coverage: {len(covered)}/{len(sections)}")
    if missing:
        print(f"MISSING CLAUSES: {', '.join(missing)}")
    flagged_bleed = sorted({p for p in SCOPE_BLEED_PHRASES if p in summary.lower()})
    if flagged_bleed:
        print(f"SCOPE-BLEED PHRASES FOUND: {', '.join(flagged_bleed)}")
    else:
        print("Scope-bleed phrases: none found")
    return missing


def main():
    parser = argparse.ArgumentParser(description="Summarise an HR policy document without changing meaning.")
    parser.add_argument("--input", required=True, help="Path to the .txt policy document")
    parser.add_argument("--output", required=True, help="Path to write the summary .txt file")
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    print(f"retrieve_policy: parsed {len(sections)} clauses from {args.input}")

    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("ERROR: OPENAI_API_KEY environment variable is not set")
    client = OpenAI()
    summary = summarize_policy(client, args.model, sections)

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(summary + "\n")
    print(f"summarize_policy: summary written to {args.output}")

    missing = audit(summary, sections)
    if missing:
        sys.exit(2)


if __name__ == "__main__":
    main()
