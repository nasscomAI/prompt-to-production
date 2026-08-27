import os
import re
import sys
import argparse
from typing import List, Dict
from google import genai
from google.genai import types

class PolicyAssistant:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            print("Error: GOOGLE_API_KEY not found in environment.")
            sys.exit(1)
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-2.0-flash"
        
        self.agents_config = self._load_agents_config()
        self.documents = self.retrieve_documents()

    def _load_agents_config(self) -> str:
        with open("agents.md", "r", encoding="utf-8") as f:
            return f.read()

    def retrieve_documents(self) -> List[Dict]:
        """Loads and indexes the 3 policy files by document name and section."""
        policy_files = [
            "../data/policy-documents/policy_hr_leave.txt",
            "../data/policy-documents/policy_it_acceptable_use.txt",
            "../data/policy-documents/policy_finance_reimbursement.txt"
        ]
        
        indexed_data = []
        for file_path in policy_files:
            if not os.path.exists(file_path):
                print(f"Error: Missing file {file_path}")
                sys.exit(1)
            
            doc_name = os.path.basename(file_path)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Simple section splitting: look for lines starting with numbers like "1. " or "1.1 "
            sections = re.split(r'\n(?=\d+\.?\d*\s+[A-Z\s]+\n)', content)
            for section in sections:
                # Try to extract section number
                match = re.search(r'^(\d+\.?\d*)\s+', section)
                section_num = match.group(1) if match else "General"
                indexed_data.append({
                    "source": doc_name,
                    "section": section_num,
                    "text": section.strip()
                })
        return indexed_data

    def answer_question(self, question: str) -> str:
        """Searches indexed documents and returns answer + citation OR refusal."""
        # For simplicity in this prototype, we send all relevant context to Gemini.
        # Since the files are small (~18KB total), we can include them all or filter by keyword.
        
        context_str = ""
        for doc in self.documents:
            context_str += f"--- DOCUMENT: {doc['source']} | SECTION: {doc['section']} ---\n{doc['text']}\n\n"

        prompt = f"""
{self.agents_config}

CONTEXT FROM DOCUMENTS:
{context_str}

USER QUESTION:
{question}
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error communicating with AI: {e}"

def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Assistant")
    parser.add_argument("--api-key", help="Google Generative AI API Key")
    args = parser.parse_args()

    assistant = PolicyAssistant(api_key=args.api_key)
    
    print("UC-X Policy Assistant — Ask My Documents")
    print("Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            question = input("Question: ").strip()
            if question.lower() in ["exit", "quit"]:
                break
            if not question:
                continue
                
            answer = assistant.answer_question(question)
            print(f"\nAnswer:\n{answer}\n")
            print("-" * 40)
        except KeyboardInterrupt:
            break
        except EOFError:
            break

if __name__ == "__main__":
    main()
