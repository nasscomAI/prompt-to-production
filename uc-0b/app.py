"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os

# -------------------------------
# Skill 1: retrieve_policy
# -------------------------------
def retrieve_policy(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError("Input file not found")

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            data = file.read().strip()
            if not data:
                raise ValueError("File is empty")
            return data
    except Exception as e:
        raise Exception(f"Error reading file: {str(e)}")


# -------------------------------
# Skill 2: summarize_policy
# -------------------------------
def summarize_policy(text):
    sentences = [s.strip() for s in text.split('.') if s.strip()]

    if len(sentences) < 3:
        raise ValueError("Not enough content")

    summary = []

    for sentence in sentences:
        summary.append(sentence)

        # keep enough content but not too long
        if len(summary) >= max(3, len(sentences)//2):
            break

    final_summary = '. '.join(summary)

    if len(final_summary) < len(text) * 0.2:
        print("⚠️ Warning: Summary may be too short")

    return final_summary


# -------------------------------
# Main
# -------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)

    args = parser.parse_args()

    try:
        data = retrieve_policy(args.input)
        summary = summarize_policy(data)

        with open(args.output, 'w', encoding='utf-8') as file:
            file.write(summary)

        print("✅ Summary generated successfully!")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()