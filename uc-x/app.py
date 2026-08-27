import os
import re
import sys

POLICY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'policy-documents')
DOCUMENTS = ('policy_hr_leave.txt', 'policy_it_acceptable_use.txt', 'policy_finance_reimbursement.txt')

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# ── Domain classifier ──────────────────────────────────────────────
DOMAIN_KEYWORDS = {
    'policy_hr_leave.txt': [
        'annual leave', 'carry forward', 'forfeit', 'sick leave',
        'maternity', 'paternity', 'leave without pay', 'lwp',
        'public holiday', 'compensatory off', 'leave encashment',
        'leave grievance', 'loss of pay',
    ],
    'policy_it_acceptable_use.txt': [
        'corporate device', 'personal device', 'byod', 'install software',
        'acceptable use', 'password', 'mfa', 'multi-factor',
        'endpoint security', 'remote access', 'it department approval',
        'cmc email', 'employee self-service portal', 'classified data',
        'guest wifi', 'remote wipe', 'device lock',
    ],
    'policy_finance_reimbursement.txt': [
        'reimbursement', 'travel', 'daily allowance', 'da',
        'outstation', 'home office equipment', 'accommodation',
        'hotel', 'mileage', 'meal receipt', 'training expense',
        'mobile phone reimbursement', 'internet reimbursement',
        'expense claim',
    ],
}

SINGLES = {
    'policy_hr_leave.txt': {'leave', 'holiday', 'encash', 'grievance', 'lop',
                             'annual', 'sick', 'maternity', 'paternity'},
    'policy_it_acceptable_use.txt': {'laptop', 'software', 'install', 'email',
                                      'password', 'wifi', 'byod', 'device', 'data',
                                      'internet', 'monitor', 'phone', 'personal',
                                      'network', 'access'},
    'policy_finance_reimbursement.txt': {'receipt', 'claim', 'allowance', 'expense',
                                          'travel', 'hotel', 'meal', 'reimburse',
                                          'da'},
}


def _classify_domain(question):
    q_lower = question.lower()
    scores = {}

    def word_in_q(word):
        return bool(re.search(r'\b' + re.escape(word) + r'\b', q_lower))

    for doc_name, keywords in DOMAIN_KEYWORDS.items():
        scores[doc_name] = sum(1 for kw in keywords if kw in q_lower)
    for doc_name, words in SINGLES.items():
        scores[doc_name] = scores.get(doc_name, 0) + sum(1 for w in words if word_in_q(w))

    best_doc = max(scores, key=scores.get)
    best_score = scores[best_doc]
    return best_doc if best_score > 0 else None


# ── Document parsing ────────────────────────────────────────────────
def retrieve_documents():
    index = {}
    for doc_name in DOCUMENTS:
        path = os.path.join(POLICY_DIR, doc_name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Policy file not found: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        index[doc_name] = _parse_sections(text, doc_name)
    return index


def _parse_sections(text, doc_name):
    HEADER, HEADING, CONTENT = 'HEADER', 'HEADING', 'CONTENT'
    sections = []
    lines = text.split('\n')
    state = HEADER
    current_heading = None
    section_lines = []

    for line in lines:
        is_sep = bool(re.match(r'^═+$', line.strip()))
        if is_sep:
            if state == HEADER:
                state = HEADING
            elif state == HEADING:
                state = CONTENT
            elif state == CONTENT:
                if current_heading:
                    sections.extend(_chop_subsections(doc_name, current_heading, section_lines))
                    section_lines = []
                    current_heading = None
                state = HEADING
            continue
        stripped = line.strip()
        if not stripped:
            continue
        if state == HEADING:
            current_heading = stripped
        elif state == CONTENT:
            section_lines.append(stripped)

    if current_heading and section_lines:
        sections.extend(_chop_subsections(doc_name, current_heading, section_lines))
    return sections


def _chop_subsections(doc_name, heading, section_lines):
    sub_re = re.compile(r'^(\d+(?:\.\d+)?)\s')
    subs = []
    current_num = None
    current_lines = []

    for line in section_lines:
        m = sub_re.match(line)
        if m:
            if current_num is not None:
                subs.append({
                    'document': doc_name,
                    'section_number': current_num,
                    'heading': heading,
                    'text': '\n'.join(current_lines).strip(),
                })
            current_num = m.group(1)
            rest = line[m.end():]
            current_lines = [rest.strip()] if rest.strip() else []
        else:
            current_lines.append(line)

    if current_num is not None and current_lines:
        subs.append({
            'document': doc_name,
            'section_number': current_num,
            'heading': heading,
            'text': '\n'.join(current_lines).strip(),
        })
    return subs if subs else [{
        'document': doc_name,
        'section_number': _extract_section_number(heading),
        'heading': heading,
        'text': '\n'.join(section_lines).strip(),
    }]


def _extract_section_number(heading):
    m = re.match(r'(\d+(?:\.\d+)?)', heading)
    return m.group(1) if m else ''


# ── Signal keywords for within-domain section disambiguation ────────
SECTION_SIGNALS = {
    ('policy_hr_leave.txt', '2.6'): {'carry', 'forward', 'forfeit'},
    ('policy_hr_leave.txt', '3.1'): {'sick', 'day'},
    ('policy_hr_leave.txt', '4.3'): {'paternity'},
    ('policy_hr_leave.txt', '5.1'): {'lwp'},
    ('policy_hr_leave.txt', '5.2'): {'approve', 'head', 'director', 'lwp'},
    ('policy_hr_leave.txt', '7.3'): {'encash'},
    ('policy_hr_leave.txt', '8.1'): {'grievance'},
    ('policy_it_acceptable_use.txt', '2.3'): {'install', 'software', 'approve'},
    ('policy_it_acceptable_use.txt', '3.1'): {'personal', 'device', 'email', 'portal'},
    ('policy_finance_reimbursement.txt', '2.6'): {'da', 'meal', 'simultan'},
    ('policy_finance_reimbursement.txt', '3.1'): {'allowance', 'equip', 'permanent'},
    ('policy_finance_reimbursement.txt', '4.1'): {'training'},
}

# ── Question answering ──────────────────────────────────────────────
STOP_WORDS = {
    'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'can', 'could',
    'shall', 'should', 'may', 'might', 'must', 'to', 'of', 'in', 'for', 'on',
    'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during', 'before',
    'after', 'above', 'below', 'between', 'out', 'off', 'over', 'under',
    'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
    'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
    'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
    'so', 'than', 'too', 'very', 'just', 'because', 'but', 'and', 'or',
    'if', 'while', 'about', 'up', 'what', 'which', 'who', 'whom', 'this',
    'that', 'these', 'those', 'am', 'it', 'its', 'my', 'your', 'our',
    'their', 'his', 'her', 'i', 'me', 'we', 'us', 'they', 'them',
    'please', 'tell', 'me',
}


def _words(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return [w for w in text.split() if w not in STOP_WORDS and len(w) > 2]


_NORM_OVERRIDES = {
    'approves': 'approve',
    'approval': 'approve',
    'approved': 'approve',
    'simultaneously': 'simultaneous',
    'grievances': 'grievance',
    'entitled': 'entitle',
    'entitlements': 'entitlement',
    'encashed': 'encash',
    'reimbursement': 'reimburse',
    'reimbursable': 'reimburse',
    'equipment': 'equip',
    'permitted': 'permit',
    'moderation': 'moderate',
    'classified': 'classify',
    'certificate': 'certify',
    'practitioner': 'practition',
    'exhausting': 'exhaust',
    'applicable': 'apply',
}


def _normalize(word):
    s = word.lower()
    if s in _NORM_OVERRIDES:
        return _NORM_OVERRIDES[s]
    if s.endswith('ies') and len(s) > 3:
        s = s[:-3] + 'y'
    elif s.endswith('val') and len(s) > 4:
        s = s[:-3] + 've'
    elif s.endswith('es') and len(s) > 3:
        s = s[:-2]
    elif s.endswith('s') and len(s) > 3:
        s = s[:-1]
    return s


def _norm_set(words):
    return {_normalize(w) for w in words}


def _body_tokens(sec):
    text = (sec['heading'] + ' ' + sec['text']).lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return [w for w in text.split() if len(w) > 2]


def _body_norms(sec):
    return _norm_set(_body_tokens(sec))


def _heading_norms(sec):
    heading = sec['heading'].lower()
    heading = re.sub(r'[^\w\s]', ' ', heading)
    words = [w for w in heading.split() if len(w) > 2]
    return _norm_set(words)


def answer_question(question, index):
    domain = _classify_domain(question)

    q_words = _words(question)
    q_norms = _norm_set(q_words)
    q_bigrams = [' '.join(q_words[i:i + 2]) for i in range(len(q_words) - 1)]

    if not q_norms:
        return REFUSAL_TEMPLATE

    if domain:
        candidates = index[domain]
    else:
        candidates = []
        for secs in index.values():
            candidates.extend(secs)

    best_score = -1
    best_sec = None

    for sec in candidates:
        body_n = _body_norms(sec)
        heading_n = _heading_norms(sec)
        body_hits = len(q_norms & body_n)
        heading_hits = len(q_norms & heading_n)
        score = body_hits + heading_hits * 2

        for bg in q_bigrams:
            bg_words = bg.split()
            bg_norms = {_normalize(w) for w in bg_words if len(w) > 2}
            if bg_norms and bg_norms.issubset(body_n):
                score += 2

        key = (sec['document'], sec['section_number'])
        if key in SECTION_SIGNALS:
            signal_hits = len(q_norms & SECTION_SIGNALS[key])
            score += signal_hits * 5

        if score > best_score:
            best_score = score
            best_sec = sec

    if best_sec is None:
        return REFUSAL_TEMPLATE
    if domain is None and best_score <= 1:
        return REFUSAL_TEMPLATE
    if domain is not None and best_score < 1:
        return REFUSAL_TEMPLATE

    return (
        f"{best_sec['document']} section {best_sec['section_number']}\n"
        f"{best_sec['heading']}\n\n"
        f"{best_sec['text']}"
    )


# ── CLI ─────────────────────────────────────────────────────────────
def main():
    print("UC-X — Ask My Documents (type 'exit' to quit)\n")
    try:
        index = retrieve_documents()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in ('exit', 'quit'):
            break
        print()
        print(answer_question(question, index))
        print()


if __name__ == '__main__':
    main()
