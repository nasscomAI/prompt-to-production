"""
UC-0B app.py
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import os
import re
from google import genai
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.+)$", re.MULTILINE)


def retrieve_policy(input_path: str) -> dict:
    """
    Loads the policy file and extracts numbered clauses (e.g. 2.3, 5.2)
    into a dict of {clause_number: clause_text}.
    """
    with open(input_path, encoding="utf-8") as f:
        raw = f.read()

    # Join wrapped lines so multi-line clauses become one block per clause number
    lines = raw.split("\n")
    clauses = {}
    current_num = None
    current_text = []

    for line in lines:
        match = re.match(r"^(\d+\.\d+)\s+(.*)$", line.strip())
        if match:
            if current_num:
                clauses[current_num] = " ".join(current_text).strip()
            current_num = match.group(1)
            current_text = [match.group(2)]
        elif current_num and line.strip() and not line.strip().startswith("═"):
            current_text.append(line.strip())

    if current_num:
        clauses[current_num] = " ".join(current_text).strip()

    return clauses


def summarize_policy(clauses: dict) -> str:
    """
    ENFORCED VERSION — forces the model to output one line per clause,
    explicitly instructed to preserve every condition and binding word.
    Then verifies every clause number made it into the output.
    """
    clause_list_text = "\n".join(f"{num}: {text}" for num, text in clauses.items())

    prompt = f"""You are summarizing a policy document, clause by clause.

STRICT RULES:
1. Output exactly one line per clause, in the format: "[CLAUSE_NUM] summary text"
2. Every clause number listed below MUST appear in your output — do not skip any.
3. If a clause has multiple conditions (e.g. "requires approval from X AND Y"), you MUST preserve every condition. Do not drop any approver, deadline, or exception.
4. Preserve the original binding strength (must/will/may/requires/not permitted) — do not soften "will" into "may" or drop "regardless of X" type qualifiers.
5. Do not add any information, context, or "standard practice" framing not present in the clause text.
6. If you cannot summarize a clause without losing meaning, output it verbatim instead, prefixed with "[VERBATIM]".

Clauses:
{clause_list_text}

Output ONLY the clause-by-clause summary lines, nothing else."""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )
    summary = response.text.strip()

    # --- ENFORCEMENT: verify every clause number is present ---
    missing = [num for num in clauses if num not in summary]
    if missing:
        summary += "\n\n[ENFORCEMENT WARNING] The following clauses were missing from the AI output and are appended verbatim:\n"
        for num in missing:
            summary += f"[VERBATIM - {num}] {clauses[num]}\n"

    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}. {len(clauses)} clauses processed.")


if __name__ == "__main__":
    main()