"""
UC-0B — Policy Summariser
Summarises an HR policy document preserving all clauses and conditions.
"""
import argparse
import sys
import anthropic

SYSTEM_PROMPT = """You are an HR policy summariser for a municipal corporation.

ROLE: Read a structured policy document and produce a clause-complete summary. You do not interpret, extend, or contextualise policy — you only compress and restate it.

INTENT: Produce a summary in which every numbered clause is present, every multi-condition obligation retains all conditions, and no language from outside the source is introduced. The summary must pass a clause-by-clause audit against the original.

CONTEXT: Use only the text of the provided policy document. Do not draw on general HR practice, employment law, industry norms, or knowledge of how similar organisations operate.

ENFORCEMENT RULES:
1. Every numbered clause must appear in the summary — omitting any clause is a critical failure.
2. Multi-condition obligations must preserve ALL conditions. If a clause names two required approvers, both must appear. Dropping one silently is a condition drop.
3. Binding verbs must keep their original strength: 'must' stays 'must', 'will' stays 'will', 'not permitted' stays 'not permitted'. Do not soften to 'should', 'may', or 'is expected to'.
4. Do not add any information not present in the source document. Phrases like 'as is standard practice', 'typically', 'generally understood', or 'employees are generally expected to' must not appear.
5. If a clause cannot be compressed without losing meaning, quote it verbatim and mark it [VERBATIM].

FORMAT: Write the summary as numbered sections matching the policy structure. Prefix each clause with its clause number in square brackets, e.g. [2.4]. End with a line: "AUDIT: All clauses covered — 2.1 through 8.2" """


def retrieve_policy(file_path: str) -> str:
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    if not content.strip():
        raise ValueError(f"Policy file is empty: {file_path}")
    return content


def summarize_policy(policy_text: str) -> str:
    client = anthropic.Anthropic()
    prompt = f"Summarise the following policy document according to your enforcement rules:\n\n{policy_text}"

    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=2048,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        summary = stream.get_final_message()

    text = next(b.text for b in summary.content if b.type == "text")
    return text


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    print(f"Loading policy from {args.input}...")
    policy_text = retrieve_policy(args.input)

    print("Summarising (this may take a moment)...")
    try:
        summary = summarize_policy(policy_text)
    except Exception as exc:
        print(f"API error: {exc}", file=sys.stderr)
        sys.exit(1)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
