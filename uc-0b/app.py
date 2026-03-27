"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import sys

def retrieve_policy(filepath: str) -> str:
    """loads .txt policy file, returns content as structured numbered sections"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Keep clauses and structural text intact. We can structure them into
        # a continuous text that is clearly numbered for the LLM.
        structured_content = ""
        for line in lines:
            line = line.strip()
            if line and not line.startswith("══"):
                structured_content += line + "\n"
        return structured_content
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        sys.exit(1)

def summarize_policy(structured_sections: str) -> str:
    """takes structured sections, produces compliant summary with clause references"""
    try:
        import openai
    except ImportError:
        print("Error: The 'openai' library is required. Please install it with `pip install openai`.")
        sys.exit(1)
        
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set. Please set it to proceed.")
        sys.exit(1)
        
    client = openai.OpenAI(api_key=api_key)
    
    # Load agents.md to construct system prompt dynamically
    agents_path = os.path.join(os.path.dirname(__file__), 'agents.md')
    try:
        import yaml
        with open(agents_path, 'r', encoding='utf-8') as f:
            agent_config = yaml.safe_load(f)
            
        role = agent_config.get('role', '').strip()
        intent = agent_config.get('intent', '').strip()
        context = agent_config.get('context', '').strip()
        enforcement_lines = [f"{i+1}. {rule}" for i, rule in enumerate(agent_config.get('enforcement', []))]
        enforcement = "\n".join(enforcement_lines)
        
        # Load skills.md to inject skill requirements into the prompt
        skills_path = os.path.join(os.path.dirname(__file__), 'skills.md')
        try:
            with open(skills_path, 'r', encoding='utf-8') as f:
                skills_config = yaml.safe_load(f)
            summarize_skill = next((s for s in skills_config.get('skills', []) if s.get('name') == 'summarize_policy'), None)
            skill_instruction = summarize_skill.get('description', '') if summarize_skill else ''
        except Exception as e:
            print(f"Warning: Error reading {skills_path}: {e}")
            skill_instruction = ""
            
        system_prompt = f"Role:\n{role}\n\nIntent:\n{intent}\n\nContext:\n{context}\n\nEnforcement Rules:\n{enforcement}\n\nTask:\n{skill_instruction}"
    except ImportError:
        print("Error: The 'PyYAML' library is required to read agents.md. Please install it with `pip install pyyaml`.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading {agents_path}: {e}")
        sys.exit(1)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please summarize the following policy document:\n\n{structured_sections}"}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error during LLM code summarization: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the output summary")
    args = parser.parse_args()

    print(f"Retrieving policy from {args.input}...")
    structured_content = retrieve_policy(args.input)
    
    print("Summarizing policy...")
    summary = summarize_policy(structured_content)
    
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Done. Summary written to {args.output}")
    except Exception as e:
        print(f"Error writing to {args.output}: {e}")

if __name__ == "__main__":
    main()
