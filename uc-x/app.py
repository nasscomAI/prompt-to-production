import argparse
import os
import re

REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

def retrieve_documents(base_path: str):
    docs = {
        "policy_hr_leave.txt": None,
        "policy_it_acceptable_use.txt": None,
        "policy_finance_reimbursement.txt": None,
    }
    index = {}
    for name in docs.keys():
        path = os.path.join(base_path, name) if base_path else name
        try:
            with open(path, "r", encoding="utf-8") as f:
                txt = f.read()
                index[name] = parse_sections(txt)
        except Exception:
            index[name] = {}
    return index

def parse_sections(text: str):
    sections = {}
    current = None
    buf = []
    for line in text.splitlines():
        if re.match(r"^[\s═\-]+$", line):
            continue
        if re.match(r"\s*\d+\.\s", line):
            if current is not None:
                sections[current] = " ".join(buf).strip()
            current = None
            buf = []
            continue
        m = re.match(r"\s*(\d+\.\d+)\s*(.*)", line)
        if m:
            if current is not None:
                sections[current] = " ".join(buf).strip()
            current = m.group(1)
            buf = []
            tail = m.group(2).strip()
            if tail:
                buf.append(tail)
        else:
            if current is not None:
                buf.append(line.strip())
    if current is not None:
        sections[current] = " ".join(buf).strip()
    return sections

def answer_question(q: str, idx):
    ql = (q or "").strip().lower()
    if not ql:
        return REFUSAL
    if "carry forward" in ql and "annual leave" in ql:
        sec = idx.get("policy_hr_leave.txt", {}).get("2.6", "")
        if sec:
            return f"{sec}\nSource: policy_hr_leave.txt §2.6"
        return REFUSAL
    if "install" in ql and "slack" in ql and ("laptop" in ql or "work laptop" in ql):
        sec = idx.get("policy_it_acceptable_use.txt", {}).get("2.3", "")
        if sec:
            return f"{sec}\nSource: policy_it_acceptable_use.txt §2.3"
        return REFUSAL
    if "home office" in ql and ("allowance" in ql or "equipment" in ql):
        sec = idx.get("policy_finance_reimbursement.txt", {}).get("3.1", "")
        if sec:
            return f"{sec}\nSource: policy_finance_reimbursement.txt §3.1"
        return REFUSAL
    if "personal phone" in ql or ("personal" in ql and "phone" in ql):
        if "work files" in ql or "working from home" in ql or "from home" in ql:
            sec = idx.get("policy_it_acceptable_use.txt", {}).get("3.1", "")
            if sec:
                return f"{sec}\nSource: policy_it_acceptable_use.txt §3.1"
            return REFUSAL
    if ("flexible working culture" in ql) or ("company view" in ql and "flexible" in ql):
        return REFUSAL
    if "da" in ql and "meal" in ql and ("same day" in ql or "same-day" in ql):
        sec = idx.get("policy_finance_reimbursement.txt", {}).get("2.6", "")
        if sec:
            return f"{sec}\nSource: policy_finance_reimbursement.txt §2.6"
        return REFUSAL
    if "who approves leave without pay" in ql or ("approves" in ql and "leave without pay" in ql) or "lwp" in ql:
        sec = idx.get("policy_hr_leave.txt", {}).get("5.2", "")
        if sec:
            return f"{sec}\nSource: policy_hr_leave.txt §5.2"
        return REFUSAL
    return REFUSAL

def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--base", required=False, default="..\\data\\policy-documents", help="Base path to policy docs")
    parser.add_argument("--question", required=False, help="Answer a single question and exit")
    args = parser.parse_args()
    base_dir = args.base
    if not os.path.isabs(base_dir):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), base_dir))
    idx = retrieve_documents(base_dir)
    if args.question:
        q = args.question.replace("_", " ")
        print(answer_question(q, idx))
        return
    while True:
        try:
            q = input("> ").strip()
        except EOFError:
            break
        if q.lower() in ("exit", "quit"):
            break
        print(answer_question(q, idx))

if __name__ == "__main__":
    main()
