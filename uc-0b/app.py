"""
UC-0B app.py — NAIVE BASELINE (Control step).
Mirrors what "Summarize the policy document." naively produces: picks a
few clauses that "feel important", paraphrases loosely (softening binding
verbs), and pads the intro with generic HR boilerplate not present in the
source. Kept here temporarily to document the Control run; see git history.
"""
import argparse


def summarize(text: str) -> str:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    picked = [l for l in lines if l[:1].isdigit() and "." in l[:4]][:6]

    out = []
    out.append("SUMMARY: Employee Leave Policy")
    out.append("")
    out.append(
        "As is standard practice in government organisations, employees are "
        "generally expected to plan their leave responsibly and in "
        "consultation with their manager."
    )
    out.append("")
    for line in picked:
        # loose paraphrase: strip the clause number and soften the verb
        text_only = line.split(" ", 1)[1] if " " in line else line
        text_only = text_only.replace("must", "should").replace("will be", "may be")
        out.append(f"- {text_only}")
    return "\n".join(out) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with open(args.input, encoding="utf-8") as f:
        text = f.read()
    summary = summarize(text)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
