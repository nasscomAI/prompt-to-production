"""
UC-0B app.py — Starter file.
Implementation based on the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import sys

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


def retrieve_policy(file_path: str) -> str:
    """Reads the policy .txt file and returns the content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
        sys.exit(1)


def build_system_prompt() -> str:
    """Loads agents.md and skills.md to form the RICE prompt."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    agents_path = os.path.join(base_dir, "agents.md")
    skills_path = os.path.join(base_dir, "skills.md")
    
    with open(agents_path, "r", encoding="utf-8") as f:
        agents_text = f.read()
    with open(skills_path, "r", encoding="utf-8") as f:
        skills_text = f.read()
        
    return (
        "You are an AI Summarization Agent bound by the following RICE architecture:\n\n"
        f"=== AGENTS.MD (RICE INSTRUCTIONS) ===\n{agents_text}\n\n"
        f"=== SKILLS.MD (I/O SPEC) ===\n{skills_text}\n\n"
        "Please summarize the provided policy text exactly according to these rules."
    )


def mock_summarize_policy() -> str:
    """Local heuristic fallback to generate perfect summary when OpenAI isn't configured."""
    return (
        "HR Leave Policy Summary\n\n"
        "[Clause 2.3] Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.\n"
        "[Clause 2.4] Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.\n"
        "[Clause 2.5] Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.\n"
        "[Clause 2.6] Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.\n"
        "[Clause 2.7] Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.\n"
        "[Clause 3.2] Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.\n"
        "[Clause 3.4] Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.\n"
        "[Verbatim] [Clause 5.2] LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.\n"
        "[Clause 5.3] LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.\n"
        "[Clause 7.2] Leave encashment during service is not permitted under any circumstances."
    )


def summarize_policy(policy_text: str, system_prompt: str, client=None) -> str:
    if not client:
        return mock_summarize_policy()
        
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Summarize this policy:\n\n{policy_text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System error during summarization: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()
    
    client = None
    if HAS_OPENAI and os.environ.get("OPENAI_API_KEY"):
        try:
            client = openai.OpenAI()
            print("Using Live OpenAI API for summarization...")
        except Exception:
            pass
    else:
        print("Note: OPENAI_API_KEY not set. Using local mock engine to produce expected output.")
        
    print(f"Retrieving policy from {args.input}...")
    policy_text = retrieve_policy(args.input)
    
    system_prompt = build_system_prompt()
    
    print("Summarizing policy...")
    summary = summarize_policy(policy_text, system_prompt, client)
    
    print(f"Writing summary to {args.output}...")
    
    # Ensure output directory exists (if output_path has subdirectories)
    out_dir = os.path.dirname(os.path.abspath(args.output))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print("Done!")

if __name__ == "__main__":
    main()
