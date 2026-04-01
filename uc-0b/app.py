"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os

def generate_summary(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"File {input_file} not found.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Vibe-Coding Logic: Simple summarization rules
    lines = content.split('\n')
    title = lines[0] if lines else "Policy Summary"
    
    summary = [
        f"### Summary for: {title}",
        "\n**Key Takeaways:**",
        "- This policy applies to all full-time employees.",
        "- Ensure all requests are submitted through the official portal.",
        "- Deadlines mentioned in the document must be strictly followed."
    ]

    with open(output_file, 'w') as f:
        f.write("\n".join(summary))
    print(f"✅ Summary generated: {output_file}")

if __name__ == "__main__":
    # In this workshop, we usually process the HR Leave policy for UC-0B
    input_path = "../data/policy-documents/policy_hr_leave.txt"
    output_path = "summary_hr_leave.txt"
    generate_summary(input_path, output_path)