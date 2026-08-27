
import argparse
import re

def retrieve_policy(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    clauses = []
    current = None
    for line in text.splitlines():
        m = re.match(r"^(\d+\.\d+)\s+(.*)", line)
        if m:
            if current:
                clauses.append(current)
            current = {"id": m.group(1), "text": m.group(2).strip()}
        elif current and line.strip():
            current["text"] += " " + line.strip()
    if current:
        clauses.append(current)
    return clauses

def summarize_policy(clauses):
    out = []
    for c in clauses:
        t = c["text"]
        # Preserve critical wording.
        if any(x in t.lower() for x in [
            "must","requires","not permitted","not valid",
            "loss of pay","forfeited","approval"
        ]):
            out.append(f'{c["id"]}: {t}')
        else:
            out.append(f'{c["id"]}: {t}')
    return "\n".join(out)

def main():
    p = argparse.ArgumentParser(description="Meaning-preserving HR policy summarizer")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()
