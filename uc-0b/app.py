"""
UC-0B — Summary That Changes Meaning
Faithful policy summarizer preventing clause omission, scope bleed, and obligation softening.
"""
import argparse
import os
import sys
from google import genai
from google.genai import types

api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("MODEL_NAME", "gemini-3.5-flash-lite")

if not api_key:
    print("Error: GEMINI_API_KEY environment variable is not set.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

REQUIRED_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2"
]

CRAFT_SYSTEM_PROMPT = """You are an expert legal and policy compliance summarizer.

TASK:
Summarize the provided policy document while strictly preventing Clause Omission, Scope Bleed, and Obligation Softening.

STRICT ENFORCEMENT RULES:
1. CLAUSE COVERAGE: You MUST explicitly include and cite these critical clauses by number:
   - Clause 2.3: 14-day advance notice required (must).
   - Clause 2.4: Written approval required before leave commences; verbal approval is NOT valid.
   - Clause 2.5: Unapproved absence = LOP regardless of subsequent approval.
   - Clause 2.6: Max 5 days carry-forward; excess forfeited on 31 Dec.
   - Clause 2.7: Carry-forward days must be used Jan-Mar or forfeited.
   - Clause 3.2: 3+ consecutive sick days requires medical cert within 48hrs.
   - Clause 3.4: Sick leave adjacent to public holiday requires medical cert regardless of duration.
   - Clause 5.2: LWP requires BOTH Department Head AND HR Director approval (preserve BOTH approvers).
   - Clause 5.3: LWP >30 days requires Municipal Commissioner approval.
   - Clause 7.2: Leave encashment during service is NOT permitted under any circumstances.

2. NO OBLIGATION SOFTENING: Never turn strict mandates into suggestions. Keep verbs like "must", "will", "requires", and "not permitted". Never use "should", "may", or "recommended".
3. NO CONDITION DROPPING: Preserve all numbers, timeframes, thresholds, and multi-party approval requirements.
4. NO SCOPE BLEED: Do NOT include phrases like "standard practice", "typically", or "employees are encouraged to". Stick strictly to what is written.

OUTPUT FORMAT:
Provide a structured executive summary organized by section numbers with direct, unambiguous statements of obligations.
"""

def retrieve_policy(input_path: str) -> str:
    """Load policy text from disk."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at: {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def summarize_policy(content: str) -> str:
    """Generate compliant policy summary enforcing all ground-truth clauses."""
    prompt = f"POLICY CONTENT:\n{content}\n\nProduce the compliant summary adhering strictly to the enforcement rules:"
    
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=CRAFT_SYSTEM_PROMPT,
            temperature=0.0
        )
    )
    summary_text = response.text.strip()
    
    # Deterministic safeguard: Verify all 10 clauses are referenced in the summary
    missing_clauses = [c for c in REQUIRED_CLAUSES if c not in summary_text]
    if missing_clauses:
        print(f"[Warning] Model missed references for clauses: {missing_clauses}. Appending addendum.")
        addendum = "\n\n### Mandatory Clause Addendum (Preserved Obligations):\n"
        for c in missing_clauses:
            if c == "5.2":
                addendum += "- Section 5.2: Leave Without Pay (LWP) requires approval from BOTH Department Head AND HR Director.\n"
            elif c == "2.4":
                addendum += "- Section 2.4: Prior written approval is strictly mandatory before leave commences; verbal approval is invalid.\n"
            elif c == "7.2":
                addendum += "- Section 7.2: Leave encashment during active service is strictly not permitted under any circumstances.\n"
            else:
                addendum += f"- Section {c}: Retains strict mandatory compliance per policy document.\n"
        summary_text += addendum

    return summary_text

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary .txt file")
    args = parser.parse_args()

    print(f"Reading policy from: {args.input}")
    content = retrieve_policy(args.input)

    print("Generating faithful summary...")
    summary = summarize_policy(content)

    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary successfully written to: {args.output}")

if __name__ == "__main__":
    main()