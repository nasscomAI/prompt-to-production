import argparse
import sys
import os

def parse_simple_yaml(filepath: str) -> dict:
    """Basic YAML parser for simple key-value and list structures."""
    config = {"enforcement": []}
    with open(filepath, "r", encoding="utf-8") as f:
        for auto_line in f:
            line = auto_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("- "):
                rule = line[2:].strip("\"' ")
                config["enforcement"].append(rule)
            elif ":" in auto_line:
                key, val = auto_line.split(":", 1)
                key = key.strip()
                val = val.strip().strip("\"' ")
                if key and key != "enforcement":
                    config[key] = val
    return config

def retrieve_policy(filepath: str) -> str:
    """
    Skill: retrieve_policy
    Loads a .txt policy file and returns the content as structured numbered sections.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"ParseError: Could not read document structure: {e}")
        sys.exit(1)

def summarize_policy(content: str, agent_config: dict) -> str:
    """
    Skill: summarize_policy
    Takes structured sections and produces a compliant summary with clause references.
    """
    # Build System Prompt from Documented RICE structure
    role = agent_config.get("role", "Summarization Agent")
    intent = agent_config.get("intent", "Summarize policy documents.")
    context = agent_config.get("context", "")
    enforcement_list = agent_config.get("enforcement", [])
    enforcement_text = "\n".join([f"- {rule}" for rule in enforcement_list])
    
    system_prompt = f"ROLE: {role}\nINTENT: {intent}\nCONTEXT: {context}\nENFORCEMENT RULES:\n{enforcement_text}\n\nYou must strictly adhere to all enforcement rules."

    # Look for API keys
    openai_key = os.environ.get("OPENAI_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")

    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Summarize the following policy document:\n\n{content}"}
                ],
                temperature=0.0
            )
            return response.choices[0].message.content
        except ImportError:
            print("Error: 'openai' library not installed. Generating fallback...")
            return _fallback_summary(content, enforcement_list)
    
    elif gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_prompt)
            response = model.generate_content(f"Summarize the following policy document:\n\n{content}")
            return response.text
        except ImportError:
            print("Error: 'google-generativeai' library not installed. Generating fallback...")
            return _fallback_summary(content, enforcement_list)

    else:
        print("WARNING: No LLM API key (OPENAI_API_KEY or GEMINI_API_KEY) found in environment.")
        print("Running fallback parser for testing purposes to generate output...")
        return _fallback_summary(content, enforcement_list)

def _fallback_summary(content: str, rules: list) -> str:
    """A fallback manual summary extractor if no AI keys are present."""
    import re
    summary = "HR Policy Summary (Fallback Regex Output)\n"
    summary += "==== RULES ENFORCED ====\n" + "\n".join(f"* {r}" for r in rules) + "\n========================\n\n"
    
    clauses = re.findall(r'(\d+\.\d+\s+.*?)(?=\n\d+\.\d+|\Z)', content, re.DOTALL)
    for clause in clauses:
        clause_clean = " ".join(clause.strip().split())
        summary += f"Clause Reference: {clause_clean[:3]}\n"
        summary += f"- {clause_clean}\n\n"
    return summary

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Input policy document (.txt)")
    parser.add_argument("--output", required=True, help="Output summary file (.txt)")
    args = parser.parse_args()

    # Load agent configuration
    agent_path = os.path.join(os.path.dirname(__file__), "agents.md")
    try:
        agent_config = parse_simple_yaml(agent_path)
    except FileNotFoundError:
        print(f"Error: {agent_path} not found.")
        sys.exit(1)

    # Execute Skills
    content = retrieve_policy(args.input)
    summary = summarize_policy(content, agent_config)

    # Output Generation
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
    
    print(f"Success! Summary written to {args.output}")

if __name__ == "__main__":
    main()
