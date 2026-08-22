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


def retrieve_policy(input_path: str) -> str:
    with open(input_path, encoding="utf-8") as f:
        return f.read()


def summarize_policy_naive(document_text: str) -> str:
    """NAIVE VERSION — deliberately weak, no enforcement yet."""
    prompt = f"Summarize the policy document.\n\n{document_text}"
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )
    return response.text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    document_text = retrieve_policy(args.input)
    summary = summarize_policy_naive(document_text)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()