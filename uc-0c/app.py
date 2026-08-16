"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyzer")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Specific ward to analyze")
    parser.add_argument("--category", required=False, help="Specific category to analyze")
    parser.add_argument("--growth-type", required=False, help="Type of growth (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    try:
        from google import genai
    except ImportError:
        print("Error: google-genai library is not installed.", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    with open(args.input, "r", encoding="utf-8") as f:
        budget_data = f.read()

    agents_md_path = os.path.join(os.path.dirname(__file__), "agents.md")
    with open(agents_md_path, "r", encoding="utf-8") as f:
        agents_content = f.read()

    prompt = f"""
Please act as the agent defined by the following instructions and rules:
{agents_content}

Here is the data:
{budget_data}

Requested Analysis:
Ward: {args.ward}
Category: {args.category}
Growth Type: {args.growth_type}

Return the analysis as a CSV formatted table (or a clear error if rules are violated).
"""

    print("Generating analysis...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(response.text)

    print(f"Done. Output written to {args.output}")

if __name__ == "__main__":
    main()
