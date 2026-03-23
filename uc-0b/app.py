"""
UC-0B app.py
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import sys
import ssl
import certifi

# Fix for MacOS Python certificate errors
os.environ['SSL_CERT_FILE'] = certifi.where()
ssl._create_default_https_context = ssl._create_unverified_context

try:
    from google import genai
except ImportError:
    print("ERROR: Required libraries not found.")
    print("Please install them using: pip install google-genai")
    sys.exit(1)


def get_system_prompt() -> str:
    """Read the system prompt from agents.md."""
    agents_path = os.path.join(os.path.dirname(__file__), 'agents.md')
    if os.path.exists(agents_path):
        with open(agents_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "role: Policy Summarizer AI."


def get_skills_prompt() -> str:
    """Read the skills definitions from skills.md."""
    skills_path = os.path.join(os.path.dirname(__file__), 'skills.md')
    if os.path.exists(skills_path):
        with open(skills_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def retrieve_policy(file_path: str) -> str:
    """Skill 1: Loads a .txt policy file and returns its content."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")
    with open(file_path, mode='r', encoding='utf-8') as f:
        return f.read()


def summarize_policy(input_path: str, output_path: str):
    """
    Skill 2: Read input file, invoke the Gemini API to summarize, 
    and write the result to the output file.
    """
    try:
        policy_text = retrieve_policy(input_path)
    except Exception as e:
        print(f"Error reading policy file: {e}")
        sys.exit(1)

    system_instruction = get_system_prompt()
    skills_instruction = get_skills_prompt()
    
    # Send the policy text along with explicit instruction to use the skills document properties.
    prompt = (
        f"Available Skills:\n{skills_instruction}\n\n"
        f"Task:\nUse the 'summarize_policy' skill on the following policy text.\n\n"
        f"Policy Document:\n{policy_text}"
    )

    try:
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                'system_instruction': system_instruction,
                'temperature': 0.1,  # Keep it low for standard/compliance tasks
            },
        )
        
        # Write the resulting summary string to the output path
        with open(output_path, mode='w', encoding='utf-8') as f:
            f.write(response.text)
            
        print(f"Success! Summary written to {output_path}")

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to the policy text file")
    parser.add_argument("--output", required=True, help="Path to write the summary text file")
    args = parser.parse_args()
    
    print(f"Processing {args.input}...")
    summarize_policy(args.input, args.output)
