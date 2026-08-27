"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

def retrieve_policy(policy_path):
    with open(policy_path, 'r') as f:
        content = f.read()
    sections = re.findall(r'(\d+\.\d+)\s+(.*?)\n', content, re.DOTALL)
    return {num: text.strip() for num, text in sections}

def summarize_policy(sections):
    summary = []
    for num, text in sections.items():
        # Enforcement: preserve all conditions, quote verbatim if meaning loss
        summary.append(f"{num}: {text}")
    return "\n".join(summary)

def main():
    raise NotImplementedError("Build this using your AI tool + RICE prompt")

if __name__ == "__main__":
    import sys
    policy_path = sys.argv[1]
    output_path = sys.argv[2]
    sections = retrieve_policy(policy_path)
    summary = summarize_policy(sections)
    with open(output_path, 'w') as f:
        f.write(summary)
