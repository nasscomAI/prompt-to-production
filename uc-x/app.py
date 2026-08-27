REFUSAL = (
"This question is not covered in the available policy documents "
"(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
"Please contact the relevant team for guidance."
)

def load_documents():

    docs={}

    files={
        "HR":"data/policy-documents/policy_hr_leave.txt",
        "IT":"data/policy-documents/policy_it_acceptable_use.txt",
        "Finance":"data/policy-documents/policy_finance_reimbursement.txt"
    }

    for name,path in files.items():
        with open(path,"r",encoding="utf-8") as f:
            docs[name]=f.read().lower()

    return docs


def answer_question(q,docs):

    q=q.lower()

    for name,text in docs.items():
        if any(word in text for word in q.split()):
            return f"Answer found in {name} policy."

    return REFUSAL


def main():

    docs=load_documents()

    print("Ask questions (type exit to quit)")

    while True:

        q=input("Question: ")

        if q.lower()=="exit":
            break

        print(answer_question(q,docs))


if __name__=="__main__":
    main()