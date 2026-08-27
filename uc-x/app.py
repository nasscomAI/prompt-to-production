"""
UC-X — Ask My Documents
Interactive policy Q&A agent that answers from three source documents only.
Uses keyword-based retrieval to send only relevant sections to the LLM,
making it reliable with smaller local models (Ollama).
"""
import os
import re
import sys

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai")
    sys.exit(1)


POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)


def get_client_and_model():
    """Get the appropriate OpenAI client and model.
    Priority: OLLAMA_MODEL > GEMINI_API_KEY > OPENAI_API_KEY
    """
    ollama_model = os.environ.get("OLLAMA_MODEL")
    if ollama_model:
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        client = OpenAI(api_key="ollama", base_url=base_url)
        return client, ollama_model

    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        client = OpenAI(
            api_key=gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
        return client, model

    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        client = OpenAI(api_key=openai_key)
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        return client, model

    print("Error: No LLM provider configured.")
    print("Set one of these environment variables:")
    print("  $env:OLLAMA_MODEL='llama3'          (local Ollama, free)")
    print("  $env:GEMINI_API_KEY='your-key'      (Google Gemini)")
    print("  $env:OPENAI_API_KEY='your-key'      (OpenAI)")
    sys.exit(1)


def retrieve_documents(policy_dir):
    """Load all 3 policy files, parse into sections for retrieval."""
    documents = {}
    missing = []

    for filename in POLICY_FILES:
        path = os.path.join(policy_dir, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            documents[filename] = parse_sections(content)
        else:
            missing.append(filename)

    if missing:
        print(f"[WARNING] Missing policy files: {missing}")

    total_sections = sum(len(secs) for secs in documents.values())
    print(f"[retrieve_documents] Loaded {len(documents)} documents, {total_sections} sections")
    return documents


def parse_sections(content):
    """Parse a policy document into a list of {section_number, heading, text} dicts."""
    sections = []
    current_section = None
    current_text_lines = []

    for line in content.split("\n"):
        stripped = line.strip()
        # Detect section headings like "2. ANNUAL LEAVE"
        heading_match = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if heading_match and not re.match(r"^\d+\.\d+", stripped):
            # Save previous section
            if current_section:
                current_section["text"] = "\n".join(current_text_lines).strip()
                sections.append(current_section)
            current_section = {
                "section_number": heading_match.group(1),
                "heading": stripped,
                "text": ""
            }
            current_text_lines = []
        elif current_section and stripped and not stripped.startswith("="):
            current_text_lines.append(stripped)

    # Last section
    if current_section:
        current_section["text"] = "\n".join(current_text_lines).strip()
        sections.append(current_section)

    return sections


def retrieve_relevant_sections(documents, question, max_sections=5):
    """Simple keyword-based retrieval: find sections most relevant to the question."""
    question_lower = question.lower()
    # Extract meaningful words (skip very short ones)
    query_words = [w for w in re.findall(r'\b\w+\b', question_lower) if len(w) > 2]

    scored_sections = []
    for filename, sections in documents.items():
        for section in sections:
            text_lower = section["text"].lower()
            heading_lower = section["heading"].lower()
            # Score based on keyword matches
            score = 0
            for word in query_words:
                if word in text_lower:
                    score += text_lower.count(word)
                if word in heading_lower:
                    score += 3  # Heading matches are weighted higher
            if score > 0:
                scored_sections.append({
                    "filename": filename,
                    "section": section,
                    "score": score
                })

    # Sort by score descending, take top N
    scored_sections.sort(key=lambda x: x["score"], reverse=True)
    return scored_sections[:max_sections]


def answer_question(client, model, documents, question):
    """Retrieve relevant sections and ask LLM to answer from them only."""
    relevant = retrieve_relevant_sections(documents, question)

    if not relevant:
        return REFUSAL_TEMPLATE

    # Build context from retrieved sections only
    context_parts = []
    for item in relevant:
        sec = item["section"]
        context_parts.append(
            f"[Source: {item['filename']}, Section {sec['section_number']}. "
            f"{sec['heading']}]\n{sec['text']}"
        )
    context_text = "\n\n---\n\n".join(context_parts)

    system_prompt = f"""You are a Policy Document Question-Answering Agent. Answer ONLY from the provided source sections below.

ENFORCEMENT RULES:
1. Answer ONLY using information explicitly stated in the source sections below.
2. Never combine claims from two different documents into a single answer.
3. Never use hedging phrases like "while not explicitly covered", "typically", "generally understood", "it is common practice".
4. If the answer is not found in the sections below, respond with EXACTLY:
   "{REFUSAL_TEMPLATE}"
5. Cite the document name + section number for every claim (e.g., "According to policy_hr_leave.txt, Section 2.6:").
6. Do NOT add, infer, or imply anything not explicitly written in the source sections.
7. Quote the relevant text directly from the source when answering.

SOURCE SECTIONS:
{context_text}"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        temperature=0.0
    )
    return response.choices[0].message.content


def main():
    client, model = get_client_and_model()

    print("[UC-X] Ask My Documents - Policy Q&A Agent")
    print("=" * 50)
    documents = retrieve_documents(POLICY_DIR)

    if not documents:
        print("Error: No policy documents loaded.")
        sys.exit(1)

    print(f"[model] Using: {model}")
    print("\nType your question (or 'quit' to exit):\n")

    while True:
        try:
            question = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        print("\n[answer_question] Searching documents...")
        try:
            answer = answer_question(client, model, documents, question)
            print(f"\nA: {answer}\n")
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
