"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import sys
import json

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def get_system_instruction() -> str:
    """Read agents.md to act as the RICE system instruction."""
    agent_path = os.path.join(os.path.dirname(__file__), 'agents.md')
    if os.path.exists(agent_path):
        with open(agent_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Fallback prompt if agents.md not found: Summarize the document precisely."

def retrieve_policy(file_path: str) -> list[dict]:
    """SKILL: Loads a .txt policy file and returns its content as structured sections."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    
    sections = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    paragraphs = content.split('\n\n')
    for p in paragraphs:
        if p.strip():
            sections.append({"text": p.strip()})
    return sections

def summarize_policy_llm(sections: list[dict], client) -> str:
    """SKILL: Takes structured policy sections and produces a compliant summary with clause references using Gemini."""
    sys_inst = get_system_instruction()
    
    text_to_summarize = "\n\n".join([s['text'] for s in sections])
    prompt = f"Summarize the following policy document:\n\n{text_to_summarize}"
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={
            'system_instruction': sys_inst,
            'temperature': 0.0,
        },
    )
    return response.text

def summarize_policy_fallback(sections: list[dict]) -> str:
    """Fallback rule-based logic to emulate the RICE instructions if API fails/missing."""
    summary_lines = []
    for i, section in enumerate(sections):
        summary_lines.append(f"Section {i+1}: {section['text'][:50]}...")
    return "Fallback summary (API not available):\n" + "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write the summary .txt file")
    args = parser.parse_args()

    print("Retrieving policy...")
    try:
        sections = retrieve_policy(args.input)
    except Exception as e:
        print(f"Error reading input: {e}")
        sys.exit(1)

    client = None
    if HAS_GENAI and os.environ.get("GEMINI_API_KEY"):
        client = genai.Client()
        print("Using Gemini API for structured summarization...")
        summary = summarize_policy_llm(sections, client)
    else:
        print("No GEMINI_API_KEY found or google-genai not installed. Using fallback substitution.")
        print("Ensure you run 'pip install google-genai' and set GEMINI_API_KEY to use the AI tool.")
        summary = summarize_policy_fallback(sections)

    print(f"Writing output to {args.output}...")
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print("Done.")

if __name__ == "__main__":
    main()
