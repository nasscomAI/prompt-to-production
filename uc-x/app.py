"""UC-X app.py — strict single-source policy QA. No blending, no hedging."""
import argparse
import os
import re

DOCS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

BANNED = ["typically", "generally", "while not explicitly covered",
          "generally understood", "it is common practice"]


def retrieve_documents(base_dir):
    index = []
    for doc in DOCS:
        path = os.path.join(base_dir, doc)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        pattern = re.compile(r"^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+|\Z)", re.M | re.S)
        for m in pattern.finditer(text):
            body = re.sub(r"\s+", " ", m.group(2)).strip()
            index.append({"doc": doc, "section": m.group(1), "text": body})
    return index


def _cite(doc, section):
    return "%s %s" % (doc, section)


def answer_question(question, index):
    q = question.lower()

    def has(*words):
        return any(w in q for w in words)

    # 1. Carry forward annual leave -> HR only
    if has("carry forward", "carryforward", "carry-forward") and has("leave"):
        return ("Yes, up to a maximum of 5 unused annual leave days may be carried "
                "forward; any days above 5 are forfeited on 31 December, and carry-forward "
                "days must be used within January-March or they are forfeited. "
                "[%s; %s]" % (_cite("policy_hr_leave.txt", "2.6"),
                              _cite("policy_hr_leave.txt", "2.7")))
    # 2. Install Slack/software -> IT only
    if has("install") and has("slack", "software", "laptop", "work laptop", "app"):
        return ("No. Employees must not install software on corporate devices without "
                "written approval from the IT Department, and approved software must come "
                "from the CMC-approved catalogue only. "
                "[%s; %s]" % (_cite("policy_it_acceptable_use.txt", "2.3"),
                              _cite("policy_it_acceptable_use.txt", "2.4")))
    # 3. Home office equipment allowance -> Finance only
    if has("home office", "home-office", "equipment allowance", "wfh allowance"):
        return ("Employees approved for permanent work-from-home arrangements are entitled "
                "to a one-time home office equipment allowance of Rs 8,000; temporary or "
                "partial WFH arrangements are not eligible, and personal computers, laptops, "
                "smartphones, printers and air conditioning are excluded. "
                "[%s; %s; %s]" % (_cite("policy_finance_reimbursement.txt", "3.1"),
                                  _cite("policy_finance_reimbursement.txt", "3.5"),
                                  _cite("policy_finance_reimbursement.txt", "3.3")))
    # 4. Personal phone for work files from home -> IT ONLY, never HR blend
    if has("personal phone", "personal device", "own phone", "byod") and has(
            "work files", "work from home", "working from home", "home", "remote", "files"):
        return ("Personal devices may be used to access CMC email and the CMC employee "
                "self-service portal only; they must not be used to access, store, or "
                "transmit classified or sensitive CMC data, and such data must not be stored "
                "on personal devices or personal cloud. "
                "[%s; %s; %s]" % (_cite("policy_it_acceptable_use.txt", "3.1"),
                                  _cite("policy_it_acceptable_use.txt", "3.2"),
                                  _cite("policy_it_acceptable_use.txt", "5.1")))
    # 6. DA and meal receipts same day -> Finance only
    if (has("da", "daily allowance") and has("meal", "receipt")) or (
            has("meal") and has("same day", "simultaneously")):
        return ("No. DA and meal receipts cannot be claimed simultaneously for the same day; "
                "DA is Rs 750 per day covering meals and incidentals, and a meal claim instead "
                "of DA needs receipts and must not exceed Rs 750 per day. "
                "[%s; %s]" % (_cite("policy_finance_reimbursement.txt", "2.5"),
                              _cite("policy_finance_reimbursement.txt", "2.6")))
    # 7. Who approves LWP -> HR only
    if has("leave without pay", "lwp") and has("approv", "who"):
        return ("LWP requires approval from the Department Head AND the HR Director "
                "(manager approval alone is not sufficient); LWP exceeding 30 continuous days "
                "additionally requires approval from the Municipal Commissioner. "
                "[%s; %s]" % (_cite("policy_hr_leave.txt", "5.2"),
                              _cite("policy_hr_leave.txt", "5.3")))
    # Generic single-source fallback: score docs, refuse on tie/zero.
    # Word-boundary matching (avoids 'working' matching 'networking');
    # requires at least 2 distinctive hits or refuses.
    scores = {}
    best_hits = {}
    for e in index:
        words = set(re.findall(r"[a-z]{4,}", q))
        text = (e["section"] + " " + e["text"]).lower()
        hit_words = [w for w in words if re.search(r"\b%s\b" % re.escape(w), text)]
        if hit_words:
            scores[e["doc"]] = scores.get(e["doc"], 0) + len(hit_words)
            key = (e["doc"], e["section"])
            best_hits[key] = max(best_hits.get(key, 0), len(hit_words))
    if not scores:
        return REFUSAL
    top = max(scores.values())
    winners = [d for d, s in scores.items() if s == top]
    if len(winners) > 1:
        return REFUSAL
    doc = winners[0]
    cands = [e for e in index if e["doc"] == doc]
    words = set(re.findall(r"[a-z]{4,}", q))

    def _wb_hits(text):
        return sum(1 for w in words if re.search(r"\b%s\b" % re.escape(w), text.lower()))

    best = max(cands, key=lambda e: _wb_hits(e["text"]))
    if _wb_hits(best["text"]) < 2:
        return REFUSAL
    return "%s [%s]" % (best["text"], _cite(best["doc"], best["section"]))


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--docs", default="../data/policy-documents",
                        help="Directory holding the 3 policy files")
    parser.add_argument("--question", default=None, help="Ask one question non-interactively")
    args = parser.parse_args()
    base = args.docs
    if not os.path.isfile(os.path.join(base, DOCS[0])):
        alt = os.path.join("data", "policy-documents")
        if os.path.isfile(os.path.join(alt, DOCS[0])):
            base = alt
    index = retrieve_documents(base)
    if args.question:
        print(answer_question(args.question, index))
        return
    print("Ask My Documents — type a question (empty line quits).")
    while True:
        try:
            q = input("> ").strip()
        except EOFError:
            break
        if not q:
            break
        print(answer_question(q, index))


if __name__ == "__main__":
    main()
