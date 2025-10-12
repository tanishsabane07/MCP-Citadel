
# tools/test_scoring.py
# Quick script to test scoring locally and inspect why results are low/high.
# Run: python tools/test_scoring.py  (ensure PYTHONPATH includes backend or run from repo root)

from services.scoring import calculate_severity, analyze_query_with_cvss, _build_keyword_map
import json

TEST_QUERIES = [
    "Inject malware into system through email attachment",
    "What is the current time",
    "Bypass authentication on admin login form",
    "Execute arbitrary SQL on production database",
    "Upload malicious payload to server",
    "How to test for XSS in user comment field",
    "Is my site vulnerable to SQL injection?",
    "Delete logs on server",
    "List all files in local directory",
    "Remote code execution via file upload vulnerability"
]

def pretty_print(q):
    score, details = calculate_severity(q)
    print("="*80)
    print("QUERY:", q)
    print("SCORE:", score)
    print("DETAILS:")
    print(json.dumps(details, indent=2))
    print()

if __name__ == "__main__":
    # show top keywords (sanity)
    print("Building keyword map (sample):")
    km = _build_keyword_map()
    sample = list(sorted(km.items(), key=lambda kv: -kv[1]))[:30]
    for k, v in sample:
        print(f"{k} -> {v:.3f}")
    print("\nRunning tests:\n")
    for q in TEST_QUERIES:
        pretty_print(q)
