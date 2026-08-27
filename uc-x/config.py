import os
from dotenv import load_dotenv

load_dotenv()

# Document paths
POLICY_DOCUMENTS = {
    'policy_hr_leave.txt': '../data/policy-documents/policy_hr_leave.txt',
    'policy_it_acceptable_use.txt': '../data/policy-documents/policy_it_acceptable_use.txt',
    'policy_finance_reimbursement.txt': '../data/policy-documents/policy_finance_reimbursement.txt'


}
for name, path in POLICY_DOCUMENTS.items():
    if os.path.isfile(path) and os.access(path, os.R_OK):
        print(f"✅ {name} is readable.")
    else:
        print(f"❌ {name} is missing or not readable.")

        
# Refusal template
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# AWS Configuration
AWS_CONFIG = {
    'access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
    'secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
    'region_name': os.getenv('AWS_REGION', 'us-east-1')
}

# Hedging phrases to detect
HEDGING_PHRASES = [
    'while not explicitly covered',
    'typically',
    'generally understood',
    'it is common practice',
    'usually',
    'generally',
    'often',
    'may be',
    'seems to',
]
