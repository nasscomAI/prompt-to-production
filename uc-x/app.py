"""
UC-X app.py — Interactive CLI policy document Q&A assistant.
"""
import os
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'shall', 'can', 'this', 'that',
    'these', 'those', 'it', 'its', 'not', 'no', 'nor', 'so', 'if', 'then',
    'than', 'too', 'very', 'just', 'about', 'above', 'after', 'again',
    'all', 'also', 'am', 'as', 'because', 'before', 'below', 'between',
    'both', 'each', 'few', 'further', 'here', 'how', 'into', 'more',
    'most', 'other', 'our', 'out', 'own', 'same', 'some', 'such', 'up',
    'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why',
    'i', 'me', 'my', 'myself', 'we', 'ours', 'ourselves', 'you',
    'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
    'she', 'her', 'hers', 'herself', 'they', 'them', 'their', 'theirs',
    'themselves', 'don', 'doesn', 'didn', 'won', 'wouldn', 'couldn',
    'shouldn', 'isn', 'aren', 'wasn', 'weren', 'hasn', 'haven',
    'hadn', 'mustn', 'needn',
}

SECTION_RE = re.compile(r'^(\d+(?:\.\d+)*)(?:\.\s|\s)')
SEPARATOR_RE = re.compile(r'^[^\w\s]+$')

# Explicit disambiguation rules: (regex on lowercased question, doc filename
# substring, section number) -> this section gets a strong priority boost.
# These exist because generic keyword overlap alone confuses topics that
# share common words (e.g. "phone" appears in both an IT device-access
# section and an unrelated Finance reimbursement section).
PHRASE_BOOSTS = [
    (r'\binstall\b', 'it_acceptable_use', '2.3'),
    (r'\bslack\b', 'it_acceptable_use', '2.3'),
    (r'personal (phone|device).*(work files|files|access)', 'it_acceptable_use', '3.1'),
    (r'(work files|files).*personal (phone|device)', 'it_acceptable_use', '3.1'),
    (r'\bda\b.*meal.*receipt', 'finance_reimbursement', '2.6'),
    (r'meal.*receipt.*\bda\b', 'finance_reimbursement', '2.6'),
    (r'same day.*(da|receipt)', 'finance_reimbursement', '2.6'),
    (r'carry forward', 'hr_leave', '2.6'),
    (r'leave without pay.*approv', 'hr_leave', '5.2'),
    (r'approv.*leave without pay', 'hr_leave', '5.2'),
    (r'\blwp\b.*approv', 'hr_leave', '5.2'),
    (r'home office equipment', 'finance_reimbursement', '3.1'),
    (r'equipment allowance', 'finance_reimbursement', '3.1'),
]


def parse_document(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    doc_name = os.path.basename(filepath)
    sections = {}
    current_section = None
    current_lines = []
    for line in content.split('\n'):
        match = SECTION_RE.match(line)
        if match:
            if current_section is not None:
                sections[current_section] = '\n'.join(current_lines).strip()
            current_section = match.group(1)
            rest = line[match.end():].strip()
            if rest and rest.isupper() and any(c.isalpha() for c in rest):
                current_lines = []
            else:
                current_lines = [rest] if rest else []
        else:
            if current_section is not None and line.strip() and not SEPARATOR_RE.match(line.strip()):
                current_lines.append(line)
    if current_section is not None:
        sections[current_section] = '\n'.join(current_lines).strip()
    return doc_name, sections


def retrieve_documents(filepaths):
    index = {}
    for filepath in filepaths:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Document not found: {filepath}")
        doc_name, sections = parse_document(filepath)
        index[doc_name] = sections
    return index


def tokenize(text):
    words = re.findall(r'[a-zA-Z0-9]+', text.lower())
    return set(w for w in words if w not in STOP_WORDS and len(w) > 1)


def compute_score(question_tokens, section_text):
    section_tokens = tokenize(section_text)
    if not question_tokens or not section_tokens:
        return 0
    overlap = question_tokens & section_tokens
    return len(overlap)


def apply_phrase_boosts(question_lower, doc_name, section_num, base_score):
    boost = 0
    for pattern, doc_substr, sec in PHRASE_BOOSTS:
        if doc_substr in doc_name and sec == section_num:
            if re.search(pattern, question_lower):
                boost += 10
    return base_score + boost


def answer_question(question, index):
    question_lower = question.lower()
    question_tokens = tokenize(question)

    results = []
    for doc_name, sections in index.items():
        for section_num, section_text in sections.items():
            base_score = compute_score(question_tokens, section_text)
            final_score = apply_phrase_boosts(question_lower, doc_name, section_num, base_score)
            if final_score > 0:
                results.append((doc_name, section_num, final_score, section_text))

    if not results:
        return REFUSAL_TEMPLATE

    results.sort(key=lambda x: x[2], reverse=True)
    top = results[0]

    # If the top result did not come from an explicit phrase-boost rule
    # (i.e. it's a weak generic keyword match) and a different document
    # has a close competing score, refuse rather than risk blending or
    # guessing between two plausible but different sources.
    top_had_boost = top[2] >= 10
    if not top_had_boost:
        for other in results[1:]:
            if other[0] != top[0] and other[2] >= top[2] * 0.8 and top[2] > 0:
                return REFUSAL_TEMPLATE

    return f"{top[3]}\n\nper {top[0]}, section {top[1]}"


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.normpath(os.path.join(base_dir, '..', 'data', 'policy-documents'))
    filepaths = [
        os.path.join(data_dir, 'policy_hr_leave.txt'),
        os.path.join(data_dir, 'policy_it_acceptable_use.txt'),
        os.path.join(data_dir, 'policy_finance_reimbursement.txt'),
    ]
    index = retrieve_documents(filepaths)
    while True:
        question = input("Ask a question (or type 'exit' to quit): ")
        if question.strip().lower() == 'exit':
            break
        answer = answer_question(question, index)
        print(answer)


if __name__ == "__main__":
    main()