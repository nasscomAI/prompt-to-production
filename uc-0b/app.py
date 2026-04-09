"""
UC-0B app.py — Final Build.
This application builds the system prompt from agents.md and skills.md,
and applies the text summation process using OpenAI API.
"""
import argparse
import json
import os
import urllib.request
import urllib.error

def load_prompt_context(base_dir: str) -> str:
    """Reads agents.md and skills.md to build the system prompt."""
    agents_path = os.path.join(base_dir, "agents.md")
    skills_path = os.path.join(base_dir, "skills.md")
    
    with open(agents_path, 'r', encoding='utf-8') as f:
        agents_content = f.read()
    with open(skills_path, 'r', encoding='utf-8') as f:
        skills_content = f.read()
        
    return f"=== AGENT DEFINITION ===\n{agents_content}\n\n=== SKILLS DEFINITION ===\n{skills_content}"

def summarize_policy(api_key: str, system_prompt: str, policy_text: str) -> str:
    """Pass the policy text specifically to the LLM to get the summarized output."""
    user_prompt = f"Please process the following policy document:\n\n{policy_text}"
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.0
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            result_json = json.loads(response.read().decode('utf-8'))
            return result_json['choices'][0]['message']['content']
    except Exception as e:
        print(f"API Error classifying document: {e}")
        return f"Error: {e}"

def main():
    parser = argparse.ArgumentParser(description="UC-0B Document Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the summary output")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Failed to initialize: Please ensure you have set the OPENAI_API_KEY environment variable.")
        return

    # Check input file
    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
         print(f"Error: Input file {input_path} not found.")
         return
         
    with open(input_path, 'r', encoding='utf-8') as f:
         policy_text = f.read()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    system_prompt = load_prompt_context(base_dir)
    
    print(f"Summarizing document: {input_path}...")
    summary = summarize_policy(api_key, system_prompt, policy_text)
    
    output_path = os.path.abspath(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
         f.write(summary)
         
    print(f"Done. Summary written to {output_path}")

if __name__ == "__main__":
    main()
