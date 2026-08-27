import argparse
import os


# =========================
# Logic Layer
# =========================
def summarize_text(text: str) -> str:
    """
    Simple safe summarization:
    - Keeps all important lines
    - Avoids removing clauses
    """

    lines = text.split("\n")
    summary_lines = []

    for line in lines:
        line = line.strip()
        if line:
            summary_lines.append(line)

    return "\n".join(summary_lines)


# =========================
# Processing
# =========================
def process_file(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        print("Error: Input file not found")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    summary = summarize_text(text)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary saved to {output_path}")


# =========================
# Entry Point (CLI args)
# =========================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument("--output", required=True, help="Output file name")

    args = parser.parse_args()

    process_file(args.input, args.output)