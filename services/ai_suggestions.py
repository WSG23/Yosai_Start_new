"""Simple column suggestion heuristics used across the app."""
from typing import Dict, List, Any

from config.config import get_ai_suggestions_config

# Load default confidences from configuration
_CFG = get_ai_suggestions_config()

PERSON_ID_CONFIDENCE = _CFG.person_id_confidence
DOOR_ID_CONFIDENCE = _CFG.door_id_confidence
TIMESTAMP_CONFIDENCE = _CFG.timestamp_confidence
ACCESS_RESULT_CONFIDENCE = _CFG.access_result_confidence
TOKEN_ID_CONFIDENCE = _CFG.token_id_confidence


def reload_constants() -> None:
    """Reload constants from configuration."""
    cfg = get_ai_suggestions_config()
    global PERSON_ID_CONFIDENCE, DOOR_ID_CONFIDENCE, TIMESTAMP_CONFIDENCE, ACCESS_RESULT_CONFIDENCE, TOKEN_ID_CONFIDENCE
    PERSON_ID_CONFIDENCE = cfg.person_id_confidence
    DOOR_ID_CONFIDENCE = cfg.door_id_confidence
    TIMESTAMP_CONFIDENCE = cfg.timestamp_confidence
    ACCESS_RESULT_CONFIDENCE = cfg.access_result_confidence
    TOKEN_ID_CONFIDENCE = cfg.token_id_confidence


def generate_column_suggestions(columns: List[str]) -> Dict[str, Dict[str, Any]]:
    """Return suggested standard fields for each column name."""
    suggestions: Dict[str, Dict[str, Any]] = {}

    for column in columns:
        column_lower = column.lower()
        suggestion = {"field": "", "confidence": 0.0}

        if any(keyword in column_lower for keyword in ["person", "user", "employee", "name"]):
            suggestion = {"field": "person_id", "confidence": PERSON_ID_CONFIDENCE}
        elif any(keyword in column_lower for keyword in ["door", "location", "device", "room"]):
            suggestion = {"field": "door_id", "confidence": DOOR_ID_CONFIDENCE}
        elif any(keyword in column_lower for keyword in ["time", "date", "stamp"]):
            suggestion = {"field": "timestamp", "confidence": TIMESTAMP_CONFIDENCE}
        elif any(keyword in column_lower for keyword in ["result", "status", "access"]):
            suggestion = {"field": "access_result", "confidence": ACCESS_RESULT_CONFIDENCE}
        elif any(keyword in column_lower for keyword in ["token", "badge", "card"]):
            suggestion = {"field": "token_id", "confidence": TOKEN_ID_CONFIDENCE}

        suggestions[column] = suggestion

    return suggestions


__all__ = ["generate_column_suggestions", "reload_constants"]
