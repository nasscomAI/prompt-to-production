import argparse
import os
import google.generativeai as genai

def read_file(filepath):
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return None

def write_file(filepath, content):
    with open(filepath, 'w') as f:
        f.write(content)

def get_agent_instructions():
    try:
        with open('agents.md', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "You are an expert strict legal or policy summarizer. Your operational boundary is strictly limited to extracting and summarizing policies from the provided source text without adding, omitting, or softening any condition.\n\nA correct output must cover all required clauses related to leave policies, preserving every single condition (especially multi-approver requirements) without changing the strictness (e.g., must, will, requires, not permitted). The output should be a plain text summary matching the clauses.\n\nYou are only allowed to use the provided policy document (`policy_hr_leave.txt`). You are explicitly excluded from using outside knowledge, assuming standard government or corporate practices, or adding generalized phrasing like 'as is standard practice'.\n\nEnforcement:\n- Every numbered clause must be present in the summary\n- Multi-condition obligations must preserve ALL conditions — never drop one silently\n- Never add information not present in the source document\n- If a clause cannot be summarised without meaning loss — quote it verbatim and flag it"

def get_skills_instructions():
    try:
        with open('skills.md', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "skills:\n  - name: retrieve_policy\n    description: Loads a .txt policy file and returns the content as structured numbered sections.\n    input: File path of the policy document (string).\n    output: Parsed document content organized by structured numbered sections (dictionary or list of strings).\n    error_handling: If the file is not found or cannot be read, raise a FileNotFoundError or ValueError with a clear message indicating the file access issue.\n\n  - name: summarize_policy\n    description: Takes structured sections from a policy document and produces a compliant summary with clause references strictly adhering to the enforcement rules.\n    input: Structured numbered sections of the policy (dictionary or list of strings).\n    output: A plain text summary of the policy preserving all conditions and meanings (string).\n    error_handling: If the structured sections are empty or unparseable, return an error message indicating that the input data is insufficient for summarization."

def summarize_policy(api_key, text):
    genai.configure(api_key=api_key)
    
    agent_instructions = get_agent_instructions()
    skills_instructions = get_skills_instructions()

    prompt = f"""
    Please follow your predefined role and the exact provided skills.
    
    Agent Instructions:
    {agent_instructions}
    
    Skills Definitions:
    {skills_instructions}
    
    Using the 'retrieve_policy' and 'summarize_policy' skills conceptually, summarize the following policy document according to the strict enforcement rules.
    Provide only the final summary.

    Policy Document:
    {text}
    """
    
    generation_config = genai.types.GenerationConfig(
        temperature=0.0
    )
    
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config=generation_config)
    response = model.generate_content(prompt)
    return response.text

def main():
    parser = argparse.ArgumentParser(description="UC-0B: Summary That Changes Meaning")
    parser.add_argument('--input', type=str, required=True, help="Input policy text file")
    parser.add_argument('--output', type=str, required=True, help="Output summary text file")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        return

    print(f"Reading input file: {args.input}")
    policy_text = read_file(args.input)
    if policy_text is None:
        return

    print("Generating summary based on agents.md and skills.md...")
    summary = summarize_policy(api_key, policy_text)
    
    if summary:
        print(f"Writing output to: {args.output}")
        write_file(args.output, summary)
        print("Done!")
    else:
        print("Failed to generate summary.")

if __name__ == "__main__":
    main()
