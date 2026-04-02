"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import pandas as pd
import argparse


def classify_text(text):
    text = str(text).lower()

    if "road" in text or "traffic" in text:
        return "Infrastructure"
    elif "water" in text or "electricity" in text:
        return "Utilities"
    elif "hospital" in text or "health" in text:
        return "Healthcare"
    else:
        return "Other"


def batch_classify(input_path, output_path):
    df = pd.read_csv(input_path)

    print("Columns in file:", df.columns.tolist())

    # detect column automatically
    if "text" in df.columns:
        col = "text"
    elif "complaint" in df.columns:
        col = "complaint"
    elif "description" in df.columns:
        col = "description"
    else:
        raise Exception("No valid text column found in CSV")

    df["category"] = df[col].apply(classify_text)

    df.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)