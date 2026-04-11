import argparse
import re
import sys
import io

# Ensure stdout uses UTF-8 to prevent encoding errors with emojis or special characters on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# -----------------------------
# SKILL: retrieve_policy
# -----------------------------
def retrieve_policy(filepath: str):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise FileNotFoundError(f"[retrieve_policy] Error accessing file: {e}")

    # Normalize line breaks
    content = content.replace("\r\n", "\n")

    # Flexible pattern:
    # Supports:
    # 1.  1)  1 -  1:  (1)
    pattern = r"(?:^|\n)\s*\(?(\d{1,2})[\)\.\-:]\s+"

    matches = list(re.finditer(pattern, content))

    if not matches:
        raise ValueError(
            "[retrieve_policy] No recognizable numbered sections found."
        )

    structured = {}

    for i, match in enumerate(matches):
        clause_num = int(match.group(1))
        start = match.end()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(content)

        clause_text = content[start:end].strip()

        structured[clause_num] = clause_text

    # DEBUG INFO
    detected = sorted(structured.keys())

    # STRICT ENFORCEMENT
    expected_count = max(detected) if detected else 0
    if len(structured) != expected_count:
        raise ValueError(
            f"[retrieve_policy] Expected {expected_count} clauses ideally, found {len(structured)}.\n"
            f"Detected clause numbers: {detected}\n"
            f"👉 Check numbering format or missing clauses in input file."
        )

    return structured


# -----------------------------
# SKILL: summarize_policy
# -----------------------------
def summarize_policy(structured_sections: dict):
    summary_lines = []

    for clause_num in sorted(structured_sections.keys()):
        text = structured_sections[clause_num]

        # Detect complexity (multi-condition obligations)
        condition_count = len(
            re.findall(
                r"\b(and|or|if|unless|provided|subject to)\b",
                text,
                re.IGNORECASE,
            )
        )

        # If risky → verbatim
        if condition_count >= 2 or len(text.split()) > 50:
            summary_lines.append(
                f"{clause_num}. [VERBATIM — cannot safely summarize without meaning loss]\n{text}"
            )
            continue

        # Minimal normalization ONLY (no meaning change)
        normalized = re.sub(r"\s+", " ", text).strip()

        summary_lines.append(f"{clause_num}. {normalized}")

    # Final enforcement
    if len(summary_lines) != len(structured_sections):
        raise ValueError(
            "[summarize_policy] Clause omission detected."
        )

    return "\n\n".join(summary_lines)


# -----------------------------
# MAIN
# -----------------------------
def main():
    parser = argparse.ArgumentParser(
        description="HR Leave Policy Strict Summarization Agent"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to input policy file (.txt)"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output summary file"
    )

    args = parser.parse_args()

    try:
        # Step 1: Retrieve
        structured_sections = retrieve_policy(args.input)

        # Step 2: Summarize
        summary = summarize_policy(structured_sections)

        # Step 3: Save output
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)

        print("Success: Summary successfully generated at:", args.output)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()