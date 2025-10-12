# backend/services/severity.py

def impact_to_score(impact: str) -> int:
    """
    Convert textual impact into a severity score (0–10).
    """
    if not impact:
        return 5

    normalized = impact.strip().lower()

    mapping = {
        "info": 1,
        "informational": 1,
        "low": 3,
        "medium": 5,
        "moderate": 6,
        "high": 8,
        "critical": 10,
    }

    return mapping.get(normalized, 5)


def fuse_scores(score1: int, score2: int, impact_weight: float = 0.5) -> int:
    """
    Fuse two severity scores: one from impact, one from LLM.
    Weighted average, then rounded to int.
    """
    fused = (impact_weight * score1) + ((1 - impact_weight) * score2)
    return max(0, min(10, int(round(fused))))


def enrich_results_with_severity(results: list) -> list:
    """
    Take a list of dataset results and enrich each with a severity score.
    Adds a 'severity_score' field to each result.
    """
    enriched = []
    for r in results:
        impact_score = impact_to_score(r.get("impact"))
        r["severity_score"] = impact_score
        enriched.append(r)
    return enriched
