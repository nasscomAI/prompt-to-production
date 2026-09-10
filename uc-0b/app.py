import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


MODEL = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """
You are a strict policy summarization agent.

Summarize ONLY the supplied policy document.

The source contains numbered clauses from 1.1 through 8.2.
You MUST include every numbered clause exactly once.

Required clause sequence:

1.1, 1.2,
2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7,
3.1, 3.2, 3.3, 3.4,
4.1, 4.2, 4.3, 4.4,
5.1, 5.2, 5.3, 5.4,
6.1, 6.2, 6.3,
7.1, 7.2, 7.3,
8.1, 8.2.

Rules:
1. Every required clause must appear in the output.
2. Preserve the original clause number.
3. Preserve every number, deadline, threshold, exception, condition,
   approval requirement, and prohibition.
4. Preserve strong wording such as must, requires, will,
   cannot, and is not permitted.
5. Never invent information.
6. Never use external knowledge.
7. Do not merge clauses.
8. Clause 5.2 must preserve BOTH Department Head and HR Director approval.
9. If a clause cannot be shortened safely, repeat its original wording.
10. Before finishing, check that all required clause numbers are present.

Output only the numbered summary.
"""


def retrieve_policy(input_path):
    """Read and validate the policy document."""
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    if not path.is_file():
        raise ValueError(f"Input path is not a file: {input_path}")

    content = path.read_text(encoding="utf-8").strip()

    if not content:
        raise ValueError("Policy file is empty.")

    return content


def summarize_policy(policy_text):
    """Generate a policy summary using Groq."""
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set.")

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        max_tokens=4000,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "Summarize the following policy document.\n\n"
                    "POLICY DOCUMENT:\n"
                    f"{policy_text}"
                ),
            },
        ],
    )

    return response.choices[0].message.content.strip()


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summarizer"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the policy text file",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path where the summary will be written",
    )

    args = parser.parse_args()

    try:
        policy = retrieve_policy(args.input)
        summary = summarize_policy(policy)

        output_path = Path(args.output)
        output_path.write_text(summary + "\n", encoding="utf-8")

        print(f"Summary written to: {output_path}")

    except Exception as error:
        print(f"Error: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()