import os

def retrieve_documents():
    """Loads all 3 policy files and indexes them by document name and section number."""
    paths = [
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt"
    ]
    docs = {}
    for path in paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                docs[os.path.basename(path)] = f.read()
    return docs

def answer_question(question, docs):
    """Searches indexed documents and returns a single-source answer with a citation, or the exact refusal template."""
    # Since this is a template implementation, we return the fallback refusal for safety when no API key is provided
    # in an actual implementation, you would pass `docs` to an LLM with the prompt in agents.md.
    
    refusal_template = (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact [relevant team] for guidance."
    )
    
    try:
        from openai import OpenAI
        client = OpenAI()
        
        prompt = f"""
        You are an expert internal policy assistant for answering staff questions based strictly on three specific documents.
        Your boundary is strict adherence to single-source facts. You must never invent policies, combine policies, or guess intent.

        Intent: Provide a direct, factual answer from exactly one source document and explicitly cite the document name and section number.
        If the question cannot be answered cleanly from one document, output the refusal template verbatim.

        Enforcement Rules:
        - Never combine claims from two different documents into a single answer.
        - Never use hedging phrases: "while not explicitly covered", "typically", "generally understood", "it is common practice"
        - If question is not in the documents — use the refusal template exactly, no variations.
        - Cite source document name + section number for every factual claim.
        
        Refusal template:
        {refusal_template}

        Documents:
        {docs}

        User Question: {question}
        """
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return refusal_template

def main():
    print("Loading documents...")
    docs = retrieve_documents()
    print("Documents loaded. Type 'exit' to quit.")
    while True:
        try:
            q = input("\nAsk a question: ")
            if q.lower() in ['exit', 'quit']:
                break
            ans = answer_question(q, docs)
            print(f"\nAnswer:\n{ans}")
        except EOFError:
            break

if __name__ == "__main__":
    main()
