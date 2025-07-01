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


def test_ai_suggestions_flag_false_on_import_failure(monkeypatch):
    import builtins
    import importlib

    original_import = builtins.__import__

    def fail_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "components.column_verification":
            raise ImportError("forced failure")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fail_import)
    module = importlib.reload(helpers)
    assert module.AI_SUGGESTIONS_AVAILABLE is False

    monkeypatch.setattr(builtins, "__import__", original_import)
    importlib.reload(helpers)
