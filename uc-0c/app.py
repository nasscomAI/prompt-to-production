"""
UC-0C app.py — Number That Looks Right
"""
import argparse
import csv
import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_system_prompt() -> str:
    prompt = "You are a Data Analyst Agent.\n\n"
    agents_path = os.path.join(os.path.dirname(__file__), "agents.md")
    if os.path.exists(agents_path):
        with open(agents_path, "r", encoding="utf-8") as f:
            prompt += f.read()
    prompt += "\n\nOutput ONLY a valid JSON object with the following structure:\n"
    prompt += "{\n"
    prompt += "  \"refusal\": \"(Optional) string if you must refuse\",\n"
    prompt += "  \"rows\": [{\"period\": \"...\", \"ward\": \"...\", \"category\": \"...\", \"actual_spend\": \"...\", \"growth\": \"...\", \"formula\": \"...\", \"flag\": \"...\"}]\n"
    prompt += "}"
    return prompt

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=False, default="None")
    parser.add_argument("--category", required=False, default="None")
    parser.add_argument("--growth-type", required=False, default="None")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    # Load dataset and filter
    data = []
    with open(args.input, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if args.ward != "None" and row['ward'] != args.ward:
                continue
            if args.category != "None" and row['category'] != args.category:
                continue
            data.append(row)

    if len(data) > 30:
        data = data[:5] # Truncate if it's a broad query to save tokens; the LLM will refuse anyway

    system_prompt = get_system_prompt()
    user_prompt = f"Calculate growth for the following request:\n"
    user_prompt += f"Ward: {args.ward}\n"
    user_prompt += f"Category: {args.category}\n"
    user_prompt += f"Growth Type: {args.growth_type}\n\n"
    if len(data) == 5:
        user_prompt += "Note: Dataset truncated because a broad query was requested.\n"
    user_prompt += "Dataset (JSON):\n" + json.dumps(data)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.0
    )

    result_json = response.choices[0].message.content
    try:
        result = json.loads(result_json)
    except json.JSONDecodeError:
        print("Failed to parse LLM response as JSON.")
        return

    if result.get("refusal"):
        print(f"Agent Refused: {result['refusal']}")
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("REFUSAL: " + result["refusal"] + "\n")
        return

    rows = result.get("rows", [])
    if not rows:
        print("No rows returned.")
        return

    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Growth output written to {args.output}")

if __name__ == "__main__":
    main()
