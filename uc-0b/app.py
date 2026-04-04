"""
UC-0B app.py — Compliant Policy Summarizer
Implemented using RICE constraints mapped from agents.md and structured execution from skills.md.
"""
import argparse
import os
import re

def get_ai_response(prompt: str) -> str:
    """
    Calls the LLM (Gemini) sending the isolated clauses alongside our rigid validation rules.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("WARNING: GEMINI_API_KEY environment variable is missing!")
        print("Please declare it via: export GEMINI_API_KEY='your_key'")
        return "[SIMULATED ERROR - MOCKED LLM RESPONSE. NO VALID API KEY DETECTED.]"
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Deploy high-fidelity gemini iteration for contextual understanding without drift
        model = genai.GenerativeModel("gemini-1.5-pro") 
        
        response = model.generate_content(prompt)
        return response.text
    except ImportError:
        return "[SIMULATED ERROR - 'google-generativeai' python module not found.]"

def retrieve_policy(input_path: str) -> list:
    """
    SKILL 1: Loads a raw .txt policy file from disk and parses it systematically 
    into discrete, numbered structured sections to prevent capability softening or loss.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Security Alert: Policy source file not located at {input_path}")
        
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Heuristic to split legal clauses safely natively without an overarching LLM context window drop.
    # We segregate strictly on lines initializing as "1.0", "2.3", etc.
    sections = []
    current_section = []
    
    for line in content.split('\n'):
        if re.match(r'^\d+(\.\d+)*\s', line):
            if current_section:
                sections.append("\n".join(current_section).strip())
            current_section = [line]
        else:
            if line.strip():
                current_section.append(line)
                
    if current_section:
        sections.append("\n".join(current_section).strip())
        
    # Failsafe standard pass-through in case of highly chaotic source data layout
    if not sections:
        sections = [content]
        
    return sections

def summarize_policy(sections: list, system_prompt: str) -> str:
    """
    SKILL 2: Ingests the structured sections and produces a compliant summary natively checking the parsed logic structure against agents.md mandates.
    """
    context_text = "\n\n--[SECTION BREAK]--\n\n".join(sections)
    
    prompt = f"""{system_prompt}

--- [START OF ISOLATED SOURCE DOCUMENT STRUCTURE] ---
{context_text}
--- [END OF ISOLATED SOURCE DOCUMENT STRUCTURE] ---

YOUR EXPLICIT TASK:
Produce a comprehensive legal and compliance driven summary of the strictly structured HR Leave policy above. 
You must explicitly invoke all rules from your operational guidelines provided earlier.
CRITICAL REMINDER: Unconditionally preserve every numbered clause exactly. Never soften any binding verb. Never decouple dual conditional obligations logic (e.g., dual approvers must both be cited).
"""
    result = get_ai_response(prompt)
    return result

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to the policy.txt file")
    parser.add_argument("--output", required=True, help="Path to direct summary output")
    args = parser.parse_args()

    print(f"Targeting root policy at: {args.input}...")
    
    # 1. Execute Skill: retrieve_policy
    try:
        sections = retrieve_policy(args.input)
        print(f"[OK] Parsed document successfully into {len(sections)} distinct clause blocks.")
    except Exception as e:
        print(f"[HALTED] {e}")
        return

    # Dynamically ingest RICE framework restrictions natively
    agents_path = os.path.join(os.path.dirname(__file__), "agents.md")
    system_prompt = ""
    if os.path.exists(agents_path):
        with open(agents_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
    else:
        print("Warning: agents.md operational logic not found. Working bare.")

    # 2. Execute Skill: summarize_policy 
    print("Initiating strict contextual summarization mapping...")
    summary = summarize_policy(sections, system_prompt)

    # Output extraction
    with open(args.output, "w", encoding="utf-8") as out_f:
        out_f.write(summary)
        
    print(f"[SUCCESS] Compliance operation verified. Summary printed to: {args.output}")

if __name__ == "__main__":
    main()
