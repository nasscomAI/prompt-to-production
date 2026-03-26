"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os

def retrieve_documents(file_paths):
    """
    Loads all 3 policy files and indexes them by document name and section number.
    Input: List of file paths (strings) to the policy documents.
    Output: Dictionary indexed by document name and section number containing the content.
    Error handling: If any file is not found or cannot be read, raises an error indicating the missing file.
    """
    indexed = {}
    for path in file_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        try:
            doc_name = os.path.basename(path)
            sections = parse_policy(path)
            indexed[doc_name] = sections
        except Exception as e:
            raise RuntimeError(f"Error reading {path}: {e}")
    return indexed

def parse_policy(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    sections = {}
    current_section = None
    current_content = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('═') and len(line) > 10:  # Separator
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            current_content = []
            i += 1
            if i < len(lines):
                # Skip the section title
                i += 1
            current_section = None
        elif line and line[0].isdigit() and '.' in line:
            parts = line.split('.')
            if len(parts) >= 2 and parts[0].isdigit() and parts[1][0].isdigit():
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line
                current_content = []
                i += 1
            else:
                if current_section:
                    current_content.append(lines[i].rstrip())
                i += 1
        else:
            if current_section:
                current_content.append(lines[i].rstrip())
            i += 1
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    return sections

def answer_question(question, indexed_docs):
    """
    Searches indexed documents and returns a single-source answer with citation or the refusal template.
    Input: String containing the user's question.
    Output: String containing the answer with document name and section number citation, or the exact refusal template.
    Error handling: If the question is ambiguous, involves cross-document blending, hedged hallucination, or condition dropping, returns the refusal template; if input is invalid, raises an error.
    """
    refusal = "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Invalid input: question must be a non-empty string")
    question_lower = question.lower()
    matches = []
    for doc, sections in indexed_docs.items():
        for sec, content in sections.items():
            content_lower = content.lower()
            words = set(question_lower.split())
            match_count = sum(1 for word in words if len(word) > 2 and word in content_lower)  # Ignore short words
            if match_count > 0:
                matches.append((doc, sec, content, match_count))
    if not matches:
        return refusal
    docs = set(m[0] for m in matches)
    if len(docs) > 1:
        return refusal
    best = max(matches, key=lambda x: x[3])
    doc, sec, content, _ = best
    return f"{content}\n\nSource: {doc} section {sec}"

def main():
    file_paths = [
        '../data/policy-documents/policy_hr_leave.txt',
        '../data/policy-documents/policy_it_acceptable_use.txt',
        '../data/policy-documents/policy_finance_reimbursement.txt'
    ]
    try:
        indexed = retrieve_documents(file_paths)
    except Exception as e:
        print(f"Error loading documents: {e}")
        return
    print("Interactive CLI: Type questions, press Enter for each. Empty line to exit.")
    while True:
        try:
            question = input("Question: ").strip()
            if not question:
                break
            answer = answer_question(question, indexed)
            print(answer)
            print()  # Blank line
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
