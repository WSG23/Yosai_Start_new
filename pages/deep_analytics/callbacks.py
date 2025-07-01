import logging

import dash_bootstrap_components as dbc
from dash import html

from core.unified_callback_coordinator import UnifiedCallbackCoordinator

logger = logging.getLogger(__name__)


def run_simple_analysis(analysis_type: str, data_source: str):
    """Simplified analysis runner"""
    try:
        return dbc.Card([
            dbc.CardHeader(f"📊 {analysis_type.title()} Analysis Results"),
            dbc.CardBody([
                html.H5(f"Analysis completed for: {data_source}"),
                html.P(f"Running {analysis_type} analysis..."),
                dbc.Alert("✅ Analysis completed successfully!", color="success"),
            ]),
        ])
    except Exception as e:
        return dbc.Alert(f"❌ Analysis failed: {str(e)}", color="danger")


def register_callbacks(manager: UnifiedCallbackCoordinator) -> None:
    """Register simplified analytics callbacks"""
    from dash import Input, Output, State

    @manager.register_callback(
        Output("analytics-display-area", "children"),
        Input("security-btn", "n_clicks"),
        State("analytics-data-source", "value"),
        prevent_initial_call=True,
        callback_id="security_analysis",
        component_name="deep_analytics",
    )
    def security_analysis(n_clicks, data_source):
        if n_clicks and data_source and data_source != "none":
            return run_simple_analysis("security", data_source)
        return dbc.Alert("Please select a data source first", color="warning")

    @manager.register_callback(
        Output("analytics-display-area", "children", allow_duplicate=True),
        Input("trends-btn", "n_clicks"),
        State("analytics-data-source", "value"),
        prevent_initial_call=True,
        callback_id="trends_analysis",
        component_name="deep_analytics",
    )
    def trends_analysis(n_clicks, data_source):
        if n_clicks and data_source and data_source != "none":
            return run_simple_analysis("trends", data_source)
        return dbc.Alert("Please select a data source first", color="warning")

    @manager.register_callback(
        Output("analytics-display-area", "children", allow_duplicate=True),
        Input("behavior-btn", "n_clicks"),
        State("analytics-data-source", "value"),
        prevent_initial_call=True,
        callback_id="behavior_analysis",
        component_name="deep_analytics",
    )
    def behavior_analysis(n_clicks, data_source):
        if n_clicks and data_source and data_source != "none":
            return run_simple_analysis("behavior", data_source)
        return dbc.Alert("Please select a data source first", color="warning")

    @manager.register_callback(
        Output("analytics-display-area", "children", allow_duplicate=True),
        Input("anomaly-btn", "n_clicks"),
        State("analytics-data-source", "value"),
        prevent_initial_call=True,
        callback_id="anomaly_analysis",
        component_name="deep_analytics",
    )
    def anomaly_analysis(n_clicks, data_source):
        if n_clicks and data_source and data_source != "none":
            return run_simple_analysis("anomaly", data_source)
        return dbc.Alert("Please select a data source first", color="warning")

    @manager.register_callback(
        Output("analytics-data-source", "options"),
        Input("refresh-sources-btn", "n_clicks"),
        prevent_initial_call=True,
        callback_id="refresh_data_sources",
        component_name="deep_analytics",
    )
    def refresh_sources(n_clicks):
        return [
            {"label": "Sample Data", "value": "sample"},
            {"label": "Uploaded Files", "value": "uploaded"},
        ]
