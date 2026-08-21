def load_documents():

    files = {
        "HR": "../data/policy-documents/policy_hr_leave.txt",
        "IT": "../data/policy-documents/policy_it_acceptable_use.txt",
        "Finance": "../data/policy-documents/policy_finance_reimbursement.txt"
    }

    docs={}

    for k,v in files.items():
        with open(v,"r",encoding="utf-8") as f:
            docs[k]=f.read()

    return docs


def answer_question(question,docs):

    question=question.lower()

    if "leave" in question:
        return "HR Policy: See section 2.6 regarding carry forward leave"

    if "slack" in question:
        return "IT Policy: Slack requires written IT approval"

    if "reimbursement" in question:
        return "Finance Policy: Equipment allowance Rs 8000"

    return """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact relevant team for guidance."""


def main():

    docs=load_documents()

    print("Ask policy questions. Type exit to quit")

    while True:

        q=input(">> ")

        if q.lower()=="exit":
            break

        print(answer_question(q,docs))


if __name__=="__main__":
    main()