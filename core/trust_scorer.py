
"""
core/trust_scorer.py
Trust scoring engine for marketplace listings.
"""
from __future__ import annotations
from typing import Optional, Tuple
from config.settings import PLATFORM_TRUST_SCORES


def compute_trust(marketplace: str, rating: Optional[float] = None) -> Tuple[int, str]:
    """
    Returns (score 0-100, label Low/Medium/High) for a listing.

    Scoring factors:
    - Platform base score     (60 % weight)
    - Seller rating if known  (40 % weight, mapped to 0-100)
    """
    platform_score = PLATFORM_TRUST_SCORES.get(marketplace, 50)

    if rating is not None:
        # Normalise star rating to 0-100
        normalised_rating = min(max((rating / 5.0) * 100, 0), 100)
        final_score = int(platform_score * 0.6 + normalised_rating * 0.4)
    else:
        final_score = platform_score

    label = _score_to_label(final_score)
    return final_score, label


def _score_to_label(score: int) -> str:
    if score >= 75:
        return "High"
    elif score >= 50:
        return "Medium"
    return "Low"


def trust_emoji(label: str) -> str:
    return {"High": "🟢", "Medium": "🟡", "Low": "🔴"}.get(label, "⚪")
