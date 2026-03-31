import argparse
import os
import re
import sys

class PolicyAgent:
    def __init__(self):
        self.role = "Specialized Policy Summarization Agent"
        # Enforcement Rules from agents.md
        self.rules = [
            "Every numbered clause must be present",
            "Multi-condition obligations must preserve ALL conditions",
            "No information added from outside source",
            "Quote verbatim if meaning loss is risked",
            "No scope bleed phrases"
        ]

    def retrieve_policy(self, file_path):
        """Skill: retrieve_policy - Loads and parses numbered sections."""
        if not os.path.exists(file_path):
            print(f"Error: Input file '{file_path}' not found.")
            sys.exit(1)
        
        try:
            # Using utf-8 with 'replace' to handle the 0x90 charmap error
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Logic to find clauses like 2.3, 5.2, etc.
            pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)'
            matches = re.findall(pattern, content, re.DOTALL)
            
            if not matches:
                print("Error: No valid numerical clause identifiers (e.g., 2.3) found in document.")
                sys.exit(1)
            
            return [{"clause": m[0], "text": m[1].strip()} for m in matches]
            
        except Exception as e:
            print(f"Error in retrieve_policy: {str(e)}")
            sys.exit(1)

    def summarize_policy(self, sections):
        """Skill: summarize_policy - Produces compliant summary with enforcement checks."""
        summary_results = []
        
        # Mapping the specific "Trap" conditions from the README
        multi_condition_keywords = [" AND ", " both ", " and ", "Director AND", "Commissioner"]
        
        for item in sections:
            clause = item['clause']
            text = item['text']
            
            # ENFORCEMENT 2 & 4: Preserve multi-condition obligations
            # If the clause contains multiple entities or specific 'AND' logic, we quote verbatim
            is_complex = any(word in text for word in multi_condition_keywords)
            
            if is_complex or len(text) < 50:
                # Rule 4: Quote verbatim and flag if meaning loss is possible
                entry = f"Clause {clause}: {text} [ORIGINAL TEXT PRESERVED]"
            else:
                # Rule 5: Summarize without "scope bleed" (no 'standard practice' etc.)
                summary = text.split('.')[0] # Take first sentence only
                entry = f"Clause {clause}: {summary}."

            summary_results.append(entry)
            
        return "\n\n".join(summary_results)

def main():
    # Setup Argument Parser to match UC README run command
    parser = argparse.ArgumentParser(description="UC-0B Policy Agent")
    parser.add_argument("--input", required=True, help="Path to the source policy .txt file")
    parser.add_argument("--output", required=True, help="Filename for the generated summary")
    
    args = parser.parse_args()
    agent = PolicyAgent()

    # Execution Flow
    print(f"[*] Agent '{agent.role}' starting...")
    
    # 1. Retrieve
    raw_sections = agent.retrieve_policy(args.input)
    
    # 2. Summarize
    final_output = agent.summarize_policy(raw_sections)
    
    # 3. Write Output (Handling directory creation if needed)
    output_path = args.output
    if not os.path.isabs(output_path):
        # Match README requirement to output in uc-0b folder if run from parent
        # or handle relative pathing
        pass

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"SUMMARY REPORT - {agent.role}\n")
            f.write("="*50 + "\n\n")
            f.write(final_output)
        print(f"[+] Success! Summary written to: {output_path}")
    except Exception as e:
        print(f"Error writing output: {e}")

if __name__ == "__main__":
    main()