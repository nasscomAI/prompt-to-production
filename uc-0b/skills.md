# UC-0B Skills Definition

## Skill: `retrieve_policy`
**Purpose:** Load a .txt policy file and return its content as structured numbered sections.

**Input:** File path to policy .txt file

**Output:** Dictionary mapping section numbers to
cat > /Users/mohammedshoaibimran/prompt-to-production/uc-0b/app.py << 'EOF'
"""
UC-0B — Summary That Changes Meaning
Summarizes HR policy documents clause-by-clause without omission or softening.
"""
import argparse
import anthropic
import os

SYSTEM_PROMPT = """You are a policy summarization agent. Your job is to summarize HR policy documents with complete accuracy.

STRICT ENFORCEMENT RULES:
1. Every numbered clause must appear in the summary — never skip any clause.
2. Multi-condition obligations must preserve ALL conditions. Example: if a clause requires approval from BOTH Department Head AND HR Director, both must appear.
3. Never add any information not present in the source document. No phrases like "as is standard practice", "typically", or "generally".
4. Binding verbs must be preserved exactly: "must" stays "must", "will" stays "will", "not permitted" stays "not permitted". Never soften them.
5. If a clause cannot be summarised without meaning loss — quote it verbatim and flag it with [VERBATIM].
6. Reference every clause number in your summary.

OUTPUT FORMAT:
For each section, write:
## [Section Name]
- Clause X.X: [summary preserving all conditions and binding verbs]

Do not add any introduction or conclusion outside the clause summaries."""


def retrieve_policy(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def summarize_policy(policy_text: str) -> str:
    client = anthropic.Anthropic()
    user_prompt = f"""Summarize the following policy document clause by clause.
Follow all enforcement rules in your system prompt strictly.

POLICY DOCUMENT:
{policy_text}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Output file path for summary")
    args = parser.parse_args()

    print(f"Loading policy from: {args.input}")
    policy_text = retrieve_policy(args.input)
    print(f"Policy loaded. ({len(policy_text)} characters)")

    print("Summarizing policy...")
    summary = summarize_policy(policy_text)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("UC-0B — HR Leave Policy Summary\n")
        f.write("=" * 50 + "\n\n")
        f.write(summary)

    print(f"Summary written to: {args.output}")
    print("\n--- SUMMARY PREVIEW ---\n")
    print(summary[:1000] + "..." if len(summary) > 1000 else summary)


if __name__ == "__main__":
    main()
