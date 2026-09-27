from pathlib import Path
import re
import sys


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = BASE_DIR.parent / "data" / "policy-documents" / "policy_hr_leave.txt"
DEFAULT_OUTPUT = BASE_DIR / "summary_hr_leave.txt"


REQUIRED_SECTIONS = [
    "2.3",
    "2.4",
    "2.5",
    "2.6",
    "2.7",
    "3.2",
    "3.4",
    "5.2",
    "5.3",
    "7.2",
]


def parse_args():
    input_file = DEFAULT_INPUT
    output_file = DEFAULT_OUTPUT

    args = sys.argv[1:]
    i = 0

    while i < len(args):
        if args[i] == "--input" and i + 1 < len(args):
            input_file = Path(args[i + 1])
            i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output_file = Path(args[i + 1])
            i += 2
        else:
            raise ValueError(f"Unknown or incomplete argument: {args[i]}")

    return input_file, output_file


def load_policy(path):
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {path}")

    return path.read_text(encoding="utf-8")


def extract_sections(text):
    lines = text.splitlines()
    sections = {}
    current = None
    buffer = []

    pattern = re.compile(r"^(\d+\.\d+)\s+")

    for line in lines:
        match = pattern.match(line.strip())

        if match:
            if current is not None:
                sections[current] = " ".join(buffer).strip()

            current = match.group(1)
            buffer = [line.strip()]
        elif current is not None and line.strip():
            buffer.append(line.strip())

    if current is not None:
        sections[current] = " ".join(buffer).strip()

    return sections


def build_summary(sections):
    missing = [section for section in REQUIRED_SECTIONS if section not in sections]

    if missing:
        raise ValueError(
            "Required policy sections are missing: " + ", ".join(missing)
        )

    summary_lines = [
        "CITY MUNICIPAL CORPORATION — EMPLOYEE LEAVE POLICY SUMMARY",
        "",
        "Annual Leave",
        f"- {sections['2.3']}",
        f"- {sections['2.4']}",
        f"- {sections['2.5']}",
        f"- {sections['2.6']}",
        f"- {sections['2.7']}",
        "",
        "Sick Leave",
        f"- {sections['3.2']}",
        f"- {sections['3.4']}",
        "",
        "Leave Without Pay (LWP)",
        f"- {sections['5.2']}",
        f"- {sections['5.3']}",
        "",
        "Leave Encashment",
        f"- {sections['7.2']}",
        "",
        "Source: policy_hr_leave.txt",
    ]

    return "\n".join(summary_lines) + "\n"


def validate_summary(summary):
    for section in REQUIRED_SECTIONS:
        if section not in summary:
            raise ValueError(f"Section {section} is missing from the summary.")

    required_phrases = [
        "14 calendar days",
        "written approval",
        "Verbal approval is not valid",
        "Loss of Pay (LOP)",
        "maximum of 5",
        "31 December",
        "January–March",
        "3 or more consecutive days",
        "48 hours",
        "regardless of duration",
        "Department Head and the HR Director",
        "Manager approval alone is not sufficient",
        "30 continuous days",
        "Municipal Commissioner",
        "not permitted under any circumstances",
    ]

    for phrase in required_phrases:
        if phrase not in summary:
            raise ValueError(
                f"Required condition missing from summary: {phrase}"
            )


def main():
    input_file, output_file = parse_args()

    policy_text = load_policy(input_file)
    sections = extract_sections(policy_text)

    summary = build_summary(sections)
    validate_summary(summary)

    output_file.write_text(summary, encoding="utf-8")

    print(f"Summary generated successfully: {output_file}")


if __name__ == "__main__":
    main()