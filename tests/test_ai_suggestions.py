import pytest
from services.ai_suggestions import generate_column_suggestions, reload_constants
from config.config import reload_config


def test_basic_suggestions():
    columns = ["Time", "Person ID", "Token ID", "Door Name", "Result", "Other"]
    suggestions = generate_column_suggestions(columns)
    assert suggestions["Time"]["field"] == "timestamp"
    assert suggestions["Person ID"]["field"] == "person_id"
    assert suggestions["Token ID"]["field"] == "token_id"
    assert suggestions["Door Name"]["field"] == "door_id"
    assert suggestions["Result"]["field"] == "access_result"
    assert suggestions["Other"]["field"] == ""


def test_unknown_column_returns_empty():
    suggestions = generate_column_suggestions(["Mystery"])
    assert suggestions["Mystery"]["field"] == ""
    assert suggestions["Mystery"]["confidence"] == 0.0


def test_confidence_values_reloadable():
    """Confidence values should reflect configuration changes."""
    cfg = reload_config()
    cfg.config.ai_suggestions.person_id_confidence = 0.9
    reload_constants()

    suggestions = generate_column_suggestions(["person id"])
    assert suggestions["person id"]["confidence"] == 0.9
