import argparse
import os
import re
import json

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

def retrieve_policy(file_path: str) -> list:
    """
    Loads the HR leave policy .txt file and returns it as structured numbered sections.
    Raises an error if file not found or unreadable; validates numbered clauses.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise IOError(f"Could not read the file: {e}")

    sections = []
    lines = content.split('\n')
    current_clause = None
    current_text = []

    for line in lines:
        # Match clauses that start with numbers like "2.3", "5.2" etc.
        match = re.match(r"^(\d+\.\d+)\s*(.*)", line)
        if match:
            if current_clause:
                sections.append({
                    "clause": current_clause,
                    "text": "\n".join(current_text).strip()
                })
            current_clause = match.group(1)
            current_text = [match.group(2)]
        elif current_clause:
            current_text.append(line)

    if current_clause:
        sections.append({
            "clause": current_clause,
            "text": "\n".join(current_text).strip()
        })

    if not sections:
        raise ValueError("No valid numbered clauses found in the document.")

    return sections

def summarize_policy(sections: list) -> str:
    """
    Produces a compliant summary of the structured policy sections preserving all obligations.
    If a clause cannot be summarised without meaning loss, quotes it verbatim and flags it.
    """
    if not OpenAI:
        raise ImportError("The 'openai' Python package is required. Install it using 'pip install openai'.")
        
    client = OpenAI()
    
    agent_role = "A policy summarization agent whose operational boundary is strictly limited to extracting and condensing obligations from the provided HR leave policy document."
    agent_intent = "Produce a compliant and verifiable summary of the policy document that includes exact clause references and fully preserves all obligations without softening or dropping conditions."
    agent_context = "Allowed to use only the provided structured sections from the policy document. Must not use external knowledge, unstated assumptions, standard practices, or phrases implying typical expectations not found in the source text."
    agent_enforcement = """
- Every numbered clause must be present in the summary
- Multi-condition obligations must preserve ALL conditions — never drop one silently
- Never add information not present in the source document
- If a clause cannot be summarised without meaning loss — quote it verbatim and flag it
"""

    system_prompt = f"Role: {agent_role}\nIntent: {agent_intent}\nContext: {agent_context}\nEnforcement Rules:\n{agent_enforcement}"
    
    policy_input = json.dumps(sections, indent=2)
    user_prompt = f"Please summarize the following policy sections according to your strict enforcement rules:\n\n{policy_input}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Failed to generate summary via AI model: {e}")

def main():
    parser = argparse.ArgumentParser(description="Summarize HR leave policy using RICE framework.")
    parser.add_argument("--input", required=True, help="Path to the input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to the output summary text file")
    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
    except Exception as e:
        print(f"Error parsing policy: {e}")
        return

    try:
        summary = summarize_policy(sections)
    except Exception as e:
        print(f"Error during summarization: {e}")
        return

    try:
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    main()