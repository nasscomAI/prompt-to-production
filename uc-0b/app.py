import argparse
import re


CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.+)$")


def summarize_policy(policy_text: str) -> str:
    """Return every numbered policy clause with its conditions preserved."""
    clauses = []
    current_number = None
    current_text = []

    for raw_line in policy_text.splitlines():
        line = raw_line.strip()
        match = CLAUSE_PATTERN.match(line)
        if match:
            if current_number is not None:
                clauses.append((current_number, " ".join(current_text)))
            current_number = match.group(1)
            current_text = [match.group(2)]
        elif current_number is not None and line:
            current_text.append(line)

    if current_number is not None:
        clauses.append((current_number, " ".join(current_text)))

    return "\n".join(f"Clause {number}: {text}" for number, text in clauses)


def classify_signal_report(location: str, description: str) -> dict[str, str]:
    """Understand a free-form streetlight or traffic-signal report."""
    location_value = (location or "").strip() or "Unknown"
    text = (description or "").strip().lower()

    traffic_signal = re.search(r"\b(traffic\s+signal|traffic\s+light|signal)\b", text)
    streetlight = re.search(r"\b(street\s*light|street\s*lamp|lamp\s*post)\b", text)
    if traffic_signal:
        fault = "Traffic Signal"
        situation = "signal is damaged" if re.search(r"(damaged|broken|hit|knocked|destroyed)", text) else "signal is malfunctioning"
    elif streetlight:
        fault = "Streetlight"
        situation = "light is damaged" if re.search(r"(damaged|broken|fallen|destroyed)", text) else "light is not working"
    else:
        fault = "Unknown"
        situation = "Unknown"

    return {"Location": location_value, "Fault": fault, "Situation": situation}


def extract_location(text: str) -> str:
    match = re.search(r"\b(?:near|in|at|on)\s+([A-Za-z][A-Za-z .'-]*?)(?=\s+(?:is|was|and|but|not|working|damaged|broken)\b|[,.!?]|$)", text, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def main():
    parser = argparse.ArgumentParser(description="Summarize the HR leave policy.")
    parser.add_argument("--input", help="Path to the source policy text file")
    parser.add_argument("--output", help="Path to write the policy summary")
    parser.add_argument("--location", help="Location for a signal or streetlight report")
    parser.add_argument("--description", help="Description of a signal or streetlight report")
    parser.add_argument("--text", help="Complete natural-language signal or streetlight report")
    args = parser.parse_args()

    if args.text:
        print(classify_signal_report(extract_location(args.text), args.text))
        return
    if args.location is not None or args.description is not None:
        print(classify_signal_report(args.location or "", args.description or ""))
        return
    if not args.input or not args.output:
        parser.error("provide --text, --location/--description, or both --input and --output")

    with open(args.input, encoding="utf-8") as input_file:
        summary = summarize_policy(input_file.read())

    with open(args.output, "w", encoding="utf-8") as output_file:
        output_file.write(summary + "\n")

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
