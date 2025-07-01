import pandas as pd
import pytest
from dash.development.base_component import Component

import pages.deep_analytics.analysis as da


def test_process_suggests_analysis(monkeypatch):
    df = pd.DataFrame({
        "Time": ["2024-01-01", "2024-01-02"],
        "User": ["u1", "u2"],
        "Door": ["d1", "d2"],
        "Result": ["ok", "fail"]
    })
    uploaded = {"sample.csv": df}
    suggestions = {
        "Time": {"field": "timestamp", "confidence": 0.8},
        "User": {"field": "person_id", "confidence": 0.7},
        "Door": {"field": "door_id", "confidence": 0.6},
        "Result": {"field": "access_result", "confidence": 0.9},
    }
    monkeypatch.setattr('pages.file_upload.get_uploaded_data', lambda: uploaded)
    monkeypatch.setattr(da, 'get_ai_suggestions_for_file', lambda _df, _fn: suggestions)

    result = da.process_suggests_analysis("upload:sample.csv")

    assert result["filename"] == "sample.csv"
    assert result["total_rows"] == 2
    assert result["total_columns"] == 4
    assert pytest.approx(result["avg_confidence"], 0.01) == 0.75
    assert result["confident_mappings"] == 4
    cols = {s["column"]: s for s in result["suggestions"]}
    assert cols["Time"]["suggested_field"] == "timestamp"
    assert cols["Result"]["suggested_field"] == "access_result"


def test_process_quality_analysis(monkeypatch):
    df = pd.DataFrame({"A": [1, None, 1], "B": ["x", "y", "x"]})
    uploaded = {"test.csv": df}
    monkeypatch.setattr('pages.file_upload.get_uploaded_data', lambda: uploaded)

    result = da.process_quality_analysis("upload:test.csv")

    assert result["total_rows"] == 3
    assert result["total_columns"] == 2
    assert result["missing_values"] == 1
    assert result["duplicate_rows"] == 1
    assert pytest.approx(result["quality_score"], 0.1) == 80.0
    assert pytest.approx(result["success_rate"], 0.01) == 0.8


def test_create_analysis_results_display():
    data = {
        "analysis_type": "Security",
        "total_events": 10,
        "unique_users": 2,
        "unique_doors": 1,
        "success_rate": 0.9,
        "analysis_focus": "focus",
        "security_score": 85,
        "failed_attempts": 1,
        "risk_level": "Low",
    }
    comp = da.create_analysis_results_display(data, "security")
    assert isinstance(comp, Component)
