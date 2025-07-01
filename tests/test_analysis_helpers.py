import pandas as pd
from pages.deep_analytics import analysis_helpers as helpers


def test_get_analysis_type_options():
    opts = helpers.get_analysis_type_options()
    assert any(o["value"] == "security" for o in opts)


def test_process_suggests_analysis_safe(monkeypatch):
    df = pd.DataFrame({"time": [1, 2], "user": ["a", "b"]})
    monkeypatch.setattr("pages.file_upload.get_uploaded_data", lambda: {"test.csv": df})
    result = helpers.process_suggests_analysis_safe("upload:test.csv")
    assert result["analysis_type"] == "AI Column Suggestions"
    assert "suggestions" in result
