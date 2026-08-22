"""
UC-0C app.py
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
from google import genai
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def load_dataset_naive(input_path: str) -> str:
    with open(input_path, encoding="utf-8") as f:
        return f.read()


def compute_growth_naive(csv_text: str) -> str:
    """NAIVE VERSION — deliberately weak, no enforcement yet."""
    prompt = f"Calculate growth from the data.\n\n{csv_text}"
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )
    return response.text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--ward", required=False)
    parser.add_argument("--category", required=False)
    parser.add_argument("--growth-type", required=False)
    args = parser.parse_args()

    csv_text = load_dataset_naive(args.input)
    result = compute_growth_naive(csv_text)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"Done. Written to {args.output}")


if __name__ == "__main__":
    main()