"""
UC-X app.py — Document Q&A System
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import re
from typing import Dict, List, Tuple


REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact the HR or Finance Department for guidance."""


class PolicyDocuments:
    def __init__(self, docs_dir: str):
        self.docs_dir = docs_dir
        self.documents: Dict[str, str] = {}
        self.indexed: Dict[str, List[Tuple[str, str, str]]] = {}
        self._load_and_index()

    def _load_and_index(self):
        policy_files = {
            "policy_hr_leave.txt": "HR Leave Policy",
            "policy_it_acceptable_use.txt": "IT Acceptable Use Policy",
            "policy_finance_reimbursement.txt": "Finance Reimbursement Policy",
        }

        for filename, friendly_name in policy_files.items():
            filepath = os.path.join(self.docs_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                self.documents[friendly_name] = content
                self._index_sections(friendly_name, content)
            except FileNotFoundError:
                print(f"Warning: {filename} not found at {filepath}")

    def _index_sections(self, doc_name: str, content: str):
        section_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)$", re.MULTILINE)
        matches = list(section_pattern.finditer(content))

        if doc_name not in self.indexed:
            self.indexed[doc_name] = []

        for i, match in enumerate(matches):
            section_id = match.group(1)
            section_heading = match.group(2).strip()

            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)

            section_text = content[start:end].strip()

            self.indexed[doc_name].append((section_id, section_heading, section_text))

    def search(self, query: str) -> List[Tuple[str, str, str, str]]:
        """Search for query across all documents. Returns (doc_name, section_id, heading, text)."""
        results = []
        query_lower = query.lower()

        for doc_name, sections in self.indexed.items():
            for section_id, heading, text in sections:
                combined = (section_id + " " + heading + " " + text).lower()
                if query_lower in combined:
                    results.append((doc_name, section_id, heading, text))

        return results

    def answer_question(self, question: str) -> str:
        """Answer a question by searching documents. Enforce single-source rule."""
        results = self.search(question)

        if not results:
            return REFUSAL_TEMPLATE

        source_docs = set(r[0] for r in results)

        if len(source_docs) > 1:
            return (
                "This question appears to span multiple policy documents. "
                "Please ask about one specific policy area, or contact the relevant department. "
                "Available policies: HR Leave, IT Acceptable Use, Finance Reimbursement."
            )

        best_result = results[0]
        doc_name, section_id, heading, text = best_result

        answer = f"[Source: {doc_name}, Section {section_id}]\n\n{text}"
        return answer


def main():
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

    print("=" * 80)
    print("CITY MUNICIPAL CORPORATION — Policy Question Answering System")
    print("=" * 80)
    print("\nAvailable policy documents:")
    print("  • HR Leave Policy (policy_hr_leave.txt)")
    print("  • IT Acceptable Use Policy (policy_it_acceptable_use.txt)")
    print("  • Finance Reimbursement Policy (policy_finance_reimbursement.txt)")
    print("\nType 'exit' or 'quit' to end the session.")
    print("=" * 80)
    print()

    policies = PolicyDocuments(docs_dir)

    while True:
        try:
            question = input("\nYour question: ").strip()
        except KeyboardInterrupt:
            print("\n\nSession ended.")
            break
        except EOFError:
            print("\n\nSession ended (EOF).")
            break

        if question.lower() in {"exit", "quit", "q"}:
            print("Thank you for using the policy Q&A system. Goodbye!")
            break

        if not question:
            print("Please enter a question.")
            continue

        answer = policies.answer_question(question)
        print(f"\nAnswer:\n{answer}")


if __name__ == "__main__":
    main()
