# # services/cvss_calculator.py
# from cvss import CVSS3

# # Map common attack types to CVSS base metrics
# CVSS_PRESETS = {
#     "sql-injection": {"AV": "N", "AC": "L", "PR": "N", "UI": "N", "C": "H", "I": "H", "A": "H"},
#     "xss": {"AV": "N", "AC": "L", "PR": "N", "UI": "R", "C": "L", "I": "L", "A": "N"},
#     "command-injection": {"AV": "N", "AC": "L", "PR": "N", "UI": "N", "C": "H", "I": "H", "A": "H"},
#     "file-inclusion": {"AV": "N", "AC": "L", "PR": "N", "UI": "N", "C": "H", "I": "H", "A": "H"},
#     "path-traversal": {"AV": "N", "AC": "L", "PR": "N", "UI": "N", "C": "H", "I": "H", "A": "H"},
#     # Add other tags as needed
# }

# def calculate_cvss(tag: str, custom_metrics: dict = None) -> dict:
#     """
#     Returns dynamic severity for a vulnerability based on CVSS3.
#     - tag: vulnerability type (sql-injection, xss, etc.)
#     - custom_metrics: override any CVSS base metric (AV, AC, PR, UI, C, I, A)
    
#     Returns:
#         dict: {"base_score": float, "severity_label": str}
#     """
#     metrics = CVSS_PRESETS.get(tag, {
#         "AV": "N", "AC": "H", "PR": "N", "UI": "N", "C": "H", "I": "H", "A": "H"
#     })
    
#     # Override with custom metrics if provided
#     if custom_metrics:
#         metrics.update(custom_metrics)
    
#     # Build CVSS vector string
#     vector = f"CVSS:3.1/{'/'.join([f'{k}:{v}' for k, v in metrics.items()])}"
    
#     try:
#         score = CVSS3(vector).base_score
#     except Exception:
#         print("Error")
#         score = 5.0  # fallback score
    
#     # Convert numeric score to qualitative
#     if score >= 9:
#         label = "Critical"
#     elif score >= 7:
#         label = "High"
#     elif score >= 4:
#         label = "Medium"
#     else:
#         label = "Low"
    
#     return {"base_score": score, "severity_label": label}

# services/cvss_calculator.py
from cvss import CVSS3

def calculate_cvss(metrics: dict) -> dict:
    """
    Calculate CVSS3 score dynamically from given base metrics.
    Expects all required metrics: AV, AC, PR, UI, S, C, I, A
    Returns: {"base_score": float, "severity_label": str}
    """
    # Ensure 'S' (Scope) is always set
    if "S" not in metrics:
        metrics["S"] = "U"  # Unchanged scope by default

    vector = f"CVSS:3.1/{'/'.join([f'{k}:{v}' for k, v in metrics.items()])}"

    try:
        score = CVSS3(vector).base_score
    except Exception:
        score = 5.0  # fallback score

    # Qualitative label (optional, not sent to frontend since we only need numeric CVSS)
    if score >= 9:
        label = "Critical"
    elif score >= 7:
        label = "High"
    elif score >= 4:
        label = "Medium"
    else:
        label = "Low"

    return {"base_score": float(score), "severity_label": label}
