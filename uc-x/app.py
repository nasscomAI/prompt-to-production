"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
"""
UC-X app.py — Policy Q&A agent
Build this using RICE + agents.md + skills.md
Interactive CLI: asks questions, returns single-source answers or refusal template.
"""
# UC-X app.py — Improved interactive policy Q&A
import os
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact HR/IT/Finance team for guidance."
)

# -----------------------------
# Skill 1: retrieve_documents
# -----------------------------
def retrieve_documents(file_paths):
    """
    Loads policy documents, indexes by document name and section number.
    Works with numbered headings like '7. LEAVE ENCASHMENT'.
    Returns: {doc_name: {section_number: section_text}}
    """
    indexed = {}
    for path in file_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Policy file missing: {path}")
        doc_name = os.path.basename(path)
        indexed[doc_name] = {}

        with open(path, "r", encoding="utf-8") as f:
            section_number = None
            section_text = []

            for line in f:
                line = line.strip()
                # Match numbered headings like '7. LEAVE ENCASHMENT'
                match = re.match(r"^(\d+)\.\s", line)
                if match:
                    if section_number is not None:
                        # Save previous section
                        indexed[doc_name][section_number] = " ".join(section_text)
                    section_number = match.group(1)
                    section_text = [line]  # include heading
                else:
                    if line:
                        section_text.append(line)

            # Save last section
            if section_number is not None:
                indexed[doc_name][section_number] = " ".join(section_text)
    return indexed

# -----------------------------
# Skill 2: answer_question
# -----------------------------
def answer_question(indexed_documents, question):
    """
    Searches documents using weighted keyword + heading scoring.
    Returns: {'answer': text, 'citation': doc_name + section_number} or refusal template.
    """
    keywords = [w.lower() for w in re.findall(r"\w+", question) if len(w) > 2]

    best_match = None
    best_score = 0

    for doc_name, sections in indexed_documents.items():
        for sec_num, text in sections.items():
            # Count keyword matches in section text
            text_lower = text.lower()
            score = sum(2 if k in text_lower else 0 for k in keywords)

            # Extra weight if keyword appears in section heading
            heading_match = re.match(r"^(\d+)\.\s(.+)", text)
            if heading_match:
                heading = heading_match.group(2).lower()
                # give higher weight to critical phrase matches
                for k in keywords:
                    if k in heading:
                        score += 5  # strong boost for heading match

                        # -----------------
            # Document-based weighting
            # -----------------
            question_lower = question.lower()
            doc_score_boost = 0

            # IT-related questions
            if any(x in question_lower for x in ["personal phone", "BYOD", "work files", "email", "device"]):
                if "it" in doc_name.lower():
                    doc_score_boost += 10
                else:
                    doc_score_boost -= 5

            # HR-related questions
            if any(x in question_lower for x in ["annual leave", "leave encashment", "carry forward leave"]):
                if "hr" in doc_name.lower():
                    doc_score_boost += 10
                else:
                    doc_score_boost -= 5

            # Finance-related questions
            if any(x in question_lower for x in ["reimbursement", "DA", "allowance", "claim"]):
                if "finance" in doc_name.lower():
                    doc_score_boost += 10
                else:
                    doc_score_boost -= 5

            score += doc_score_boost

            if score > best_score:
                best_score = score
                best_match = {"answer": text, "citation": f"{doc_name} · Section {sec_num}"}

    if best_match and best_score > 0:
        return best_match
    else:
        return {"answer": REFUSAL_TEMPLATE, "citation": None}

# -----------------------------
# Main CLI
# -----------------------------
def main():
    file_paths = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]

    try:
        indexed_docs = retrieve_documents(file_paths)
    except Exception as e:
        print(f"❌ Error loading documents: {e}")
        return

    print("Type 'exit' to quit.\n")

    while True:
        question = input("Question: ").strip()
        if question.lower() == "exit":
            break
        if not question:
            continue

        result = answer_question(indexed_docs, question)
        print("\nAnswer:")
        print("═══════════════════════════════════════════════════════════")
        print(result["answer"])
        print("═══════════════════════════════════════════════════════════")
        if result["citation"]:
            print(f"Citation: {result['citation']}")
        print("-" * 50)

if __name__ == "__main__":
    main()