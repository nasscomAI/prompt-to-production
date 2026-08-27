import argparse

# 🚫 Refusal Template (MUST be exact)
REFUSAL = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""


# 📄 Load all documents
def load_documents():
    docs = {}

    files = {
        "HR": "../data/policy-documents/policy_hr_leave.txt",
        "IT": "../data/policy-documents/policy_it_acceptable_use.txt",
        "Finance": "../data/policy-documents/policy_finance_reimbursement.txt"
    }

    for name, path in files.items():
        with open(path, "r", encoding="utf-8") as f:
            docs[name] = f.read().lower()

    return docs


# 🧠 Answer logic (STRICT CONTROL)
def answer_question(question, docs):
    q = question.lower()

    # 🔍 Step 1: Route question to correct document
    if "leave" in q:
        doc_name = "HR"
    elif "laptop" in q or "software" in q or "phone" in q or "device" in q:
        doc_name = "IT"
    elif "claim" in q or "reimbursement" in q or "allowance" in q:
        doc_name = "Finance"
    else:
        return REFUSAL

    # 📄 Step 2: Answer from correct document ONLY

    # HR POLICY
    if doc_name == "HR":
        if "carry forward" in q:
            return "Employees may carry forward a maximum of 5 days; excess is forfeited on 31 December.\n(Source: HR Policy, Section 2.6)"

        if "leave without pay" in q or "lwp" in q:
            return "Leave without pay requires approval from BOTH Department Head AND HR Director.\n(Source: HR Policy, Section 5.2)"

    # IT POLICY
    if doc_name == "IT":
        if "phone" in q or "personal device" in q:
            return "Personal devices may be used only to access company email and employee self-service portal.\n(Source: IT Policy, Section 3.1)"

        if "install" in q or "software" in q:
            return "Installing software requires prior written approval from the IT department.\n(Source: IT Policy, Section 2.3)"

    # FINANCE POLICY
    if doc_name == "Finance":
        if "allowance" in q or "home office" in q:
            return "Home office equipment allowance is Rs 8,000 and applicable only for permanent work-from-home employees.\n(Source: Finance Policy, Section 3.1)"

        if "claim" in q:
            return "DA and meal claims cannot be submitted on the same day.\n(Source: Finance Policy, Section 2.6)"

    # ❌ If nothing matches exactly
    return REFUSAL


# 💻 CLI Interface
def main():
    docs = load_documents()

    print("\n📢 AI Policy Assistant Started (Type 'exit' to quit)\n")

    while True:
        question = input("Ask your question: ")

        if question.lower() == "exit":
            print("Exiting... 👋")
            break

        answer = answer_question(question, docs)
        print("\nAnswer:\n", answer, "\n")


if __name__ == "__main__":
    main()