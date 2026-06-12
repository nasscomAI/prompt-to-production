import traceback
from app import answer_question, retrieve_documents, parse_sections

try:
    documents = retrieve_documents()
    all_sections = []
    for doc_name, content in documents.items():
        if content:
            secs = parse_sections(doc_name, content)
            all_sections.extend(secs)

    print("Parsed sections:", len(all_sections))
    for s in all_sections:
        try:
            [int(x) for x in s["section_id"].split(".")]
        except Exception as e:
            print(f"Error sorting ID {s['section_id']} in {s['doc_name']}: {e}")

    # test some queries
    questions = [
        "can i wear unformal clothes in office",
        "who approves leave without pay?",
        "what is the allowance for work from home?",
        "can i use slack on my personal phone?",
    ]
    for q in questions:
        print("Q:", q)
        ans = answer_question(q, documents)
        print("A:", ans.replace("\n", " ")[:100])
except Exception as e:
    traceback.print_exc()
