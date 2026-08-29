import sys; sys.path.insert(0, '.')
from app import retrieve_documents, tokenize, compute_score
import os
base_dir = os.path.dirname(os.path.abspath('app.py'))
data_dir = os.path.normpath(os.path.join(base_dir, '..', 'data', 'policy-documents'))
filepaths = [os.path.join(data_dir, 'policy_hr_leave.txt'), os.path.join(data_dir, 'policy_it_acceptable_use.txt'), os.path.join(data_dir, 'policy_finance_reimbursement.txt')]
index = retrieve_documents(filepaths)

q = 'Can I claim DA and meal receipts on the same day?'
qt = tokenize(q)

# Get section_text from index
sec_text = index['policy_finance_reimbursement.txt']['2.6']
print('Section 2.6 repr:', repr(sec_text[:200]))
print()
st = tokenize(sec_text)
print('Section 2.6 tokens:', sorted(st))
print('claim in tokens:', 'claim' in st)
print()

score, exact = compute_score(qt, sec_text, None)
print('Score with section_text from index: %.2f, exact=%d' % (score, exact))
print()

# Also check what compute_token_doc_freq produces
from app import compute_token_doc_freq
freq = compute_token_doc_freq(index)
print('token_doc_freq for claim:', freq.get('claim', 'NOT FOUND'))
print('token_doc_freq for da:', freq.get('da', 'NOT FOUND'))
print()

# Now call compute_score with token_doc_freq
score2, exact2 = compute_score(qt, sec_text, freq)
print('Score with token_doc_freq: %.2f, exact=%d' % (score2, exact2))
