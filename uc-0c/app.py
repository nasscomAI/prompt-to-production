"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
from google import genai

def load_dataset(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV dataset.")
    parser.add_argument("--ward", required=False, help="Target ward for calculation.")
    parser.add_argument("--category", required=False, help="Target category for calculation.")
    parser.add_argument("--growth-type", required=False, help="Type of growth to compute (e.g., MoM, YoY).")
    parser.add_argument("--output", required=True, help="Path to output CSV document.")
    args = parser.parse_args()

    # Load agent instructions (RICE)
    agents_path = os.path.join(os.path.dirname(__file__), 'agents.md')
    with open(agents_path, 'r', encoding='utf-8') as f:
        system_instruction = f.read()

    dataset_content = load_dataset(args.input)
    
    # Check if growth-type is provided
    growth_type_str = f"Growth Type: {args.growth_type}" if args.growth_type else "Growth Type: Not specified."

    prompt = f"""
Please calculate the growth metric from the data below.

Parameters:
Ward: {args.ward if args.ward else 'All Wards (aggregate)'}
Category: {args.category if args.category else 'All Categories (aggregate)'}
{growth_type_str}

Dataset:
{dataset_content}

Output strictly as a CSV table with columns: Ward, Category, Period, Actual Spend, Growth, Formula/Notes. Do not include markdown code block ticks.
"""

    client = genai.Client()
    # Using gemini-3.5-flash-lite to avoid restrictive model quotas on free tier
    response = client.models.generate_content(
        model='gemini-3.5-flash-lite',
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.0
        )
    )

    result_text = response.text.strip()
    if result_text.startswith('```csv'):
        result_text = result_text[6:]
    elif result_text.startswith('```'):
        result_text = result_text[3:]
    if result_text.endswith('```'):
        result_text = result_text[:-3]

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(result_text.strip() + "\n")

    print(f"Done. Output written to {args.output}")

if __name__ == "__main__":
    main()
