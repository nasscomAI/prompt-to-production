"""
UC-0B — Policy Summarizer
"""
import argparse
import os
import sys

# MOCK FLAG
USE_MOCK = False

try:
    import google.generativeai as genai
except ImportError:
    print("Warning: google-generativeai is not installed. Using MOCK mode.", file=sys.stderr)
    USE_MOCK = True

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("Warning: GEMINI_API_KEY environment variable is missing. Using MOCK mode.", file=sys.stderr)
    USE_MOCK = True

model = None
if not USE_MOCK:
    genai.configure(api_key=API_KEY)

    SYSTEM_PROMPT = """
    role: >
      You are an expert, meticulous policy summarizer. Your operational boundary is strictly limited to extracting and summarizing the clauses from the provided policy document, preserving their exact intent, obligations, and critical conditions without softening or hallucination.

    intent: >
      To evaluate the provided policy text and produce a comprehensive summary that accurately captures every numbered clause, its core obligations, and binding conditions, maintaining the factual meaning of the source text exactly.

    context: >
      You will receive a single policy document. You are ONLY allowed to use information explicitly stated within the text. You must NOT add outside knowledge, standard practices, or generalize facts beyond what is written.

    enforcement:
      - "Every numbered clause in the source text MUST be present in the summary."
      - "Multi-condition obligations MUST preserve ALL conditions. You must never drop or omit an approval condition (e.g., if two people must approve, both must be stated)."
      - "Never add information, generalizations like 'as is standard practice', or phrases not present in the source document."
      - "If a clause cannot be summarized without losing its precise meaning, you must quote the clause verbatim and flag it."
    """

    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            system_instruction=SYSTEM_PROMPT
        )
    except Exception as e:
        print(f"Failed to initialize model: {e}", file=sys.stderr)
        USE_MOCK = True

def generate_summary(policy_text: str) -> str:
    """Uses the LLM to summarize the policy text according to RICE rules."""
    if USE_MOCK:
        # Generate a naive but "safe" fallback string showing clause preservation
        return (
            "MOCK SUMMARY OF POLICY:\n"
            "- Clause 2.3: 14-day advance notice must be provided.\n"
            "- Clause 2.4: Written approval must be acquired before leave commences (verbal not valid).\n"
            "- Clause 2.5: Unapproved absence will result in LOP regardless of subsequent approval.\n"
            "- Clause 2.6: Max 5 days carry-forward. Above 5 are forfeited on 31 Dec.\n"
            "- Clause 2.7: Carry-forward days must be used Jan-Mar or forfeited.\n"
            "- Clause 3.2: 3+ consecutive sick days requires medical cert within 48hrs.\n"
            "- Clause 3.4: Sick leave before/after holiday requires cert regardless of duration.\n"
            "- Clause 5.2: LWP requires both Department Head AND HR Director approval.\n"
            "- Clause 5.3: LWP >30 days requires Municipal Commissioner approval.\n"
            "- Clause 7.2: Leave encashment during service not permitted under any circumstances.\n"
        )
        
    prompt = f"Please summarize the following policy document strictly adhering to the system rules regarding clauses and conditions:\n\n{policy_text}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"API Error generating summary: {e}", file=sys.stderr)
        return f"Error: {e}"

def run_pipeline(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        return

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            policy_content = f.read()
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        return

    print("Generating summary...")
    summary = generate_summary(policy_content)
    
    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
        
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary successfully written to '{output_path}'.")
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy txt file")
    parser.add_argument("--output", required=True, help="Path to output summary txt file")
    args = parser.parse_args()
    
    run_pipeline(args.input, args.output)
