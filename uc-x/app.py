import os
import re

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

STOPWORDS = {
    "who","what","when","where","why","how",
    "can","i","we","you","do","does","did",
    "is","are","a","an","the","to","for","of",
    "on","in","from","my","our","your"
}


class DocumentRetriever:

    def __init__(self, file_paths):
        self.documents = {}
        self.load_documents(file_paths)

    def load_documents(self, file_paths):

        for path in file_paths:

            doc_name = os.path.basename(path)
            self.documents[doc_name] = {}

            if not os.path.exists(path):
                print(f"Warning: {path} does not exist")
                continue

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Detect either "Clause 2.3" OR "2.3"
            pattern = r"(Clause\s*\d+\.\d+|\b\d+\.\d+\b)"

            splits = re.split(pattern, content)

            for i in range(1, len(splits), 2):

                section = splits[i].strip()
                text = splits[i + 1].strip()

                self.documents[doc_name][section] = text

            print(f"{doc_name} loaded with {len(self.documents[doc_name])} clauses")

    def clean_question(self, question):

        words = re.findall(r'\b[a-zA-Z]+\b', question.lower())

        return [w for w in words if w not in STOPWORDS]

    def search(self, question):

        keywords = self.clean_question(question)

        best_match = None
        best_score = 0

        for doc_name, sections in self.documents.items():

            for section_number, text in sections.items():

                text_lower = text.lower()
                score = 0

                for word in keywords:
                    if word in text_lower:
                        score += 1

                if score > best_score:
                    best_score = score
                    best_match = (doc_name, section_number, text)

        if best_score > 0:
            return best_match

        return None


class PolicyAnswerer:

    def __init__(self, retriever):
        self.retriever = retriever

    def answer(self, question):

        result = self.retriever.search(question)

        if result:

            doc_name, section_number, text = result

            return f"{text}\n\n(Source: {doc_name}, {section_number})"

        return REFUSAL_TEMPLATE


def main():

    files = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]

    retriever = DocumentRetriever(files)
    answerer = PolicyAnswerer(retriever)

    print("\nWelcome to the Policy Q&A System (UC-X). Type 'exit' to quit.")

    while True:

        question = input("\nAsk a question: ").strip()

        if question.lower() in ["exit", "quit"]:
            break

        response = answerer.answer(question)

        print("\n" + response)


if __name__ == "__main__":
    main()