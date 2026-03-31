"""
UC-0B — Policy Summarizer
Produces a clause-accurate summary of an HR leave policy document.
Reads OPENAI_API_KEY from .env in the project root.
"""
import argparse
import os
from pathlib import Path

import certifi
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).parent.parent / ".env")
os.environ["SSL_CERT_FILE"] = certifi.where()

SYSTEM_PROMPT = """You are a policy compliance writer for a City Municipal Corporation HR department.
Your task: produce a clause-accurate summary of the policy document provided.

ENFORCEMENT RULES — apply all without exception:

1. COMPLETENESS: Every numbered clause in the source document must appear in the summary,
   numbered identically. Do not skip or merge clauses.

2. CONDITION PRESERVATION: Multi-condition obligations must preserve ALL conditions.
   - If a clause requires TWO approvers, both must be named.
   - Example: "LWP requires approval from the Department Head AND the HR Director" —
     both names must appear. Writing "requires approval" without naming both is a CRITICAL FAILURE.

3. NO ADDITIONS: Never add information not present in the source document.
   Prohibited phrases: "as is standard practice", "typically in government organisations",
   "employees are generally expected to", "it is common practice", or any inference.

4. BINDING VERB PRESERVATION: Use original verbs exactly.
   - must → must (never: should, are advised to, are encouraged to)
   - will → will (never: may)
   - requires → requires (never: recommends)
   - not permitted → not permitted (never: discouraged, not recommended)
   - are forfeited → are forfeited (never: may be lost)

5. VERBATIM QUOTING: If a clause cannot be summarised without meaning loss, quote it
   verbatim and mark it [QUOTED].

FORMAT:
- Begin with: POLICY SUMMARY — [Document Reference] Version [Version]
- Group by the same sections as the source, preserving section headings
- Each clause: [clause number] [summary or verbatim quote]
- End with: SUMMARY COMPLETE — [N] clauses covered"""


def retrieve_policy(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError(f"Policy file is empty: {file_path}")
    return content


def summarize_policy(content: str, client: OpenAI) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Summarise the following policy document:\n\n{content}"},
        ],
    )
    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    client = OpenAI()

    print(f"Loading policy from {args.input}...")
    content = retrieve_policy(args.input)

    print("Summarising (clause-accurate mode)...")
    summary = summarize_policy(content, client)

    output_path = Path(args.output)

    output_path.write_text(summary, encoding="utf-8")
    print(f"Summary written to {output_path}")
    print("\n" + "=" * 60)
    print(summary)


if __name__ == "__main__":
    main()
