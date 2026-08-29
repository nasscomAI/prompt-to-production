import sys; sys.path.insert(0, '.')
from app import retrieve_documents, tokenize, compute_score, stem, words_match
import os
base_dir = os.path.dirname(os.path.abspath('app.py'))
data_dir = os.path.normpath(os.path.join(base_dir, '..', 'data', 'policy-documents'))
filepaths = [os.path.join(data_dir, 'policy_hr_leave.txt'), os.path.join(data_dir, 'policy_it_acceptable_use.txt'), os.path.join(data_dir, 'policy_finance_reimbursement.txt')]
index = retrieve_documents(filepaths)

q = 'Can I claim DA and meal receipts on the same day?'
qt = tokenize(q)

# Section 2.6
sec_text = index['policy_finance_reimbursement.txt']['2.6']
st = tokenize(sec_text)
print('Section 2.6 tokens:', st)
print('Claim in tokens:', 'claim' in st)
print()

for q_word in sorted(qt):
    found = False
    for s_word in sorted(st):
        if q_word == s_word:
            print('  %s == %s (exact)' % (q_word, s_word))
            found = True
            break
        elif stem(q_word) == stem(s_word):
            print('  %s ~= %s (stem)' % (q_word, s_word))
            found = True
            break
        elif words_match(q_word, s_word):
            print('  %s ~ %s (words_match)' % (q_word, s_word))
            found = True
            break
    if not found:
        print('  %s -> NO MATCH' % q_word)

score, exact = compute_score(qt, sec_text, None)
print()
print('Score: %.2f, Exact: %d' % (score, exact))
