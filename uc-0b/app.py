import argparse
import os

def retrieve_policy(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def summarize_policy(text):
    # RICE Prompt
    prompt = f"""
Role:
You are a compliance-grade policy summarization system.

Input:
{text}

Constraints:
1. Every numbered clause must be included
2. Preserve ALL conditions in each clause
3. Do NOT soften obligations (must ≠ should)
4. Do NOT add external information
5. If meaning may be lost, quote the clause verbatim

Expected Output:
Numbered summary preserving clause numbers.
"""

    # For now, simulate AI output (you can later plug OpenAI API)
    return prompt  # Replace this with actual AI response if needed

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)

    args = parser.parse_args()

    text = retrieve_policy(args.input)
    summary = summarize_policy(text)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)

    print("✅ Summary generated successfully!") # You can replace this with a more detailed message if needed

if __name__ == "__main__":
    main()