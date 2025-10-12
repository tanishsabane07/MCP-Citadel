# backend/services/gemini_service.py
import json
import logging
from gemini_client import chat_send

logger = logging.getLogger(__name__)
MODEL = "gemini-2.0-flash-001"

def build_prompt(user_query: str, example: dict) -> str:
    """
    Build a prompt for Gemini including example from dataset.
    Ask Gemini to respond with JSON ONLY.
    """
    prompt = f"""
You are a senior security analyst. Given the user's query and the example vulnerability below,
respond with a JSON object (no extra text) exactly with these keys:
 - classification: short tag (e.g., sql-injection, xss, ssrf, misconfiguration)
 - severity: integer 0-10 (higher = more severe)
 - explanation: detailed explanation of why in 4-5 numbered points with each point on a new line
 - remediation: list of 9-10 numbered detailed actionable steps with each point on a new line

User query:
\"\"\"{user_query}\"\"\"

Example vulnerability:
ID: {example.get('id')}
Title: {example.get('title')}
Details: {example.get('details')}
Tag: {example.get('tag')}
Impact: {example.get('impact')}

Return JSON ONLY. Example response format:
{{"classification":"sql-injection","severity":9,"explanation":"...","remediation":["step1","step2"]}}
"""
    return prompt.strip()


def analyze_example_with_gemini(user_query: str, example: dict) -> dict:
    """
    Calls Gemini and returns a dict with keys:
    classification, severity, explanation, remediation (list of strings)
    """
    prompt = build_prompt(user_query, example)
    try:
        raw = chat_send(MODEL, prompt)
        raw_clean = raw.strip()
        
        # Extract JSON from text even if extra lines exist
        start = raw_clean.find("{")
        end = raw_clean.rfind("}") + 1
        if start == -1 or end == -1:
            raise ValueError("No JSON object detected in Gemini output")
        parsed = json.loads(raw_clean[start:end])

        # Ensure remediation is always a list
        remediation = parsed.get("remediation")
        if isinstance(remediation, str):
            remediation = [line.strip() for line in remediation.split("\n") if line.strip()]
        elif not isinstance(remediation, list):
            remediation = ["Investigate and remediate according to best practices."]

        return {
            "classification": parsed.get("classification", example.get("tag", "unknown")),
            # "severity": int(parsed.get("severity", 5)),
            "explanation": parsed.get("explanation", ""),
            "remediation": remediation
        }

    except Exception as e:
        logger.warning("Gemini parse failed (%s). Returning fallback analysis.", e)
        # fallback with dataset info
        return {
            "classification": example.get("tag", "unknown"),
            # "severity": 5,
            "explanation": "Fallback analysis: the LLM output could not be parsed. Review manually.",
            "remediation": [
                "Check the input query and try again with proper formatting.",
                "Ensure the API key and environment variables are correct.",
                "Consult the dataset to understand the vulnerability context.",
                "Log and review any potentially suspicious queries.",
                "Notify security analyst if the query seems malicious."
            ]
        }
