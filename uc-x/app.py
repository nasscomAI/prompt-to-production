import os
import yaml
import re

# Define your document paths explicitly
file_paths = [
    "C:/Users/Shaik/OneDrive/Documents/GitHub/prompt-to-production/uc-x/data/policy-documents/policy_hr_leave.txt",
    "C:/Users/Shaik/OneDrive/Documents/GitHub/prompt-to-production/uc-x/data/policy-documents/policy_it_acceptable_use.txt",
    "C:/Users/Shaik/OneDrive/Documents/GitHub/prompt-to-production/uc-x/data/policy-documents/policy_finance_reimbursement.txt"
]

# Test document loading (example)
def test_document_loading():
    for path in file_paths:
        try:
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
                print(f"Successfully loaded: {path}")
                # You can also print out part of the document content for debugging
                print(content[:200])  # Print first 200 characters for confirmation
        except FileNotFoundError:
            print(f"File not found: {path}")

# Load agents.md and skills.md
def load_config_files():
    with open('agents.md', 'r') as f:
        agents_config = yaml.safe_load(f)

    with open('skills.md', 'r') as f:
        skills_config = yaml.safe_load(f)

    return agents_config, skills_config

# Load the policy documents
def load_policy_documents():
    documents = {}
    for file_path in file_paths:  # Use updated file paths
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                documents[file_path] = f.read()
        else:
            print(f"Warning: {file_path} not found.")
    
    return documents

# Index the documents by section
def index_documents(documents):
    indexed_docs = {}
    section_pattern = r'^(\d+(\.\d+)?)\.\s*(.*)'  # Regex pattern to capture section headings

    for doc_name, doc_content in documents.items():
        indexed_docs[doc_name] = {}
        lines = doc_content.split("\n")
        current_section = None
        section_text = []
        
        for line in lines:
            clean_line = line.strip()
            
            # Skip borders or empty lines
            if not clean_line or "═══" in clean_line:
                continue
                
            match = re.match(section_pattern, clean_line)
            if match:
                if current_section:
                    indexed_docs[doc_name][current_section] = "\n".join(section_text).strip()
                
                # Use section number and title as the key
                current_section = f"{match.group(1)} {match.group(3)}".strip()
                section_text = []
            elif current_section:
                section_text.append(clean_line)
        
        if current_section:
            indexed_docs[doc_name][current_section] = "\n".join(section_text).strip()
    
    return indexed_docs

# Normalize text by making it lowercase
def normalize_text(text):
    return re.sub(r'\s+', ' ', text.lower()).strip()

# Retrieve the answer for a question
def answer_question(question, indexed_docs, refusal_template):
    normalized_question = normalize_text(question)  # Normalize the input question for better matching

    for doc_name, sections in indexed_docs.items():
        for section, content in sections.items():
            # Normalize the content of each section too
            normalized_content = normalize_text(content)
            
            # Check if the normalized question is found in the content
            if normalized_question in normalized_content:
                # Return the matched answer with citation from the document and section
                return f"Answer from {doc_name} - Section {section}:\n{content.strip()}"
    
    # If no match is found, return the refusal template verbatim
    return refusal_template

# Main interactive loop
def interactive_loop():
    # Load agents and skills configurations
    agents_config, skills_config = load_config_files()
    refusal_template = agents_config['enforcement']['refusal_template']
    
    # Load and index policy documents
    documents = load_policy_documents()
    indexed_docs = index_documents(documents)
    print("DEBUG: I found", len(indexed_docs), "documents.")

    print("\nWelcome to the UC-X Interactive Terminal!")
    print("Type 'exit' to quit the program.")
    
    while True:
        # Prompt the user for a question
        question = input("\nAsk a question: ")
        
        if question.lower() == 'exit':
            break
        
        # Answer the question based on indexed documents
        answer = answer_question(question, indexed_docs, refusal_template)
        print("\nAnswer:\n", answer)

if __name__ == "__main__":
    # Test the document loading first before running the main loop
    test_document_loading()
    
    # If all documents are successfully loaded, proceed with the interactive loop
    interactive_loop()
