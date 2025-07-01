import logging
from typing import Dict, Any
from dash import html, dcc
import dash_bootstrap_components as dbc

logger = logging.getLogger(__name__)


def create_suggests_display(suggests_data: Dict[str, Any]) -> html.Div:
    """Create suggests analysis display components."""
    if "error" in suggests_data:
        return dbc.Alert(f"Error: {suggests_data['error']}", color="danger")
    try:
        filename = suggests_data.get("filename", "Unknown")
        suggestions = suggests_data.get("suggestions", [])
        avg_confidence = suggests_data.get("avg_confidence", 0)
        confident_mappings = suggests_data.get("confident_mappings", 0)
        total_columns = suggests_data.get("total_columns", 0)
        total_rows = suggests_data.get("total_rows", 0)
        summary_card = dbc.Card([
            dbc.CardHeader([html.H5(f"🤖 AI Column Mapping Analysis - {filename}")]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H6("Dataset Info"),
                        html.P(f"File: {filename}"),
                        html.P(f"Rows: {total_rows:,}"),
                        html.P(f"Columns: {total_columns}")
                    ], width=4),
                    dbc.Col([
                        html.H6("Overall Confidence"),
                        dbc.Progress(
                            value=avg_confidence * 100,
                            label=f"{avg_confidence:.1%}",
                            color="success" if avg_confidence >= 0.7 else "warning" if avg_confidence >= 0.4 else "danger",
                        )
                    ], width=4),
                    dbc.Col([
                        html.H6("Confident Mappings"),
                        html.H3(
                            f"{confident_mappings}/{total_columns}",
                            className="text-success" if confident_mappings >= total_columns * 0.7 else "text-warning",
                        ),
                    ], width=4),
                ])
            ])
        ], className="mb-3")
        if suggestions:
            table_rows = []
            for suggestion in suggestions:
                confidence = suggestion["confidence"]
                table_rows.append(
                    html.Tr([
                        html.Td(suggestion["column"]),
                        html.Td(suggestion["suggested_field"]),
                        html.Td([
                            dbc.Progress(
                                value=confidence * 100,
                                label=f"{confidence:.1%}",
                                color="success" if confidence >= 0.7 else "warning" if confidence >= 0.4 else "danger",
                            )
                        ]),
                        html.Td(suggestion["status"]),
                        html.Td(html.Small(str(suggestion["sample_data"][:2]), className="text-muted")),
                    ])
                )
            suggestions_table = dbc.Card([
                dbc.CardHeader([html.H6("📋 Column Mapping Suggestions")]),
                dbc.CardBody([
                    dbc.Table([
                        html.Thead([
                            html.Tr([
                                html.Th("Column Name"),
                                html.Th("Suggested Field"),
                                html.Th("Confidence"),
                                html.Th("Status"),
                                html.Th("Sample Data"),
                            ])
                        ]),
                        html.Tbody(table_rows),
                    ], responsive=True, striped=True),
                ])
            ], className="mb-3")
        else:
            suggestions_table = dbc.Alert("No suggestions available", color="warning")
        return html.Div([summary_card, suggestions_table])
    except Exception as e:  # pragma: no cover
        return dbc.Alert(f"Error creating display: {str(e)}", color="danger")
            dbc.CardHeader([html.H5(f"🤖 AI Column Mapping Analysis - {filename}")]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H6("Dataset Info"),
                        html.P(f"File: {filename}"),
                        html.P(f"Rows: {total_rows:,}"),
                        html.P(f"Columns: {total_columns}")
                    ], width=4),
                    dbc.Col([
                        html.H6("Overall Confidence"),
                        dbc.Progress(
                            value=avg_confidence * 100,
                            label=f"{avg_confidence:.1%}",
                            color="success" if avg_confidence >= 0.7 else "warning" if avg_confidence >= 0.4 else "danger",
                        )
                    ], width=4),
                    dbc.Col([
                        html.H6("Confident Mappings"),
                        html.H3(
                            f"{confident_mappings}/{total_columns}",
                            className="text-success" if confident_mappings >= total_columns * 0.7 else "text-warning",
                        ),
                    ], width=4),
                ])
            ])
        ], className="mb-3")
        if suggestions:
            table_rows = []
            for suggestion in suggestions:
                confidence = suggestion["confidence"]
                table_rows.append(
                    html.Tr([
                        html.Td(suggestion["column"]),
                        html.Td(suggestion["suggested_field"]),
                        html.Td([
                            dbc.Progress(
                                value=confidence * 100,
                                label=f"{confidence:.1%}",
                                color="success" if confidence >= 0.7 else "warning" if confidence >= 0.4 else "danger",
                            )
                        ]),
                        html.Td(suggestion["status"]),
                        html.Td(html.Small(str(suggestion["sample_data"][:2]), className="text-muted")),
                    ])
                )
            suggestions_table = dbc.Card([
                dbc.CardHeader([html.H6("📋 Column Mapping Suggestions")]),
                dbc.CardBody([
                    dbc.Table([
                        html.Thead([
                            html.Tr([
                                html.Th("Column Name"),
                                html.Th("Suggested Field"),
                                html.Th("Confidence"),
                                html.Th("Status"),
                                html.Th("Sample Data"),
                            ])
                        ]),
                        html.Tbody(table_rows),
                    ], responsive=True, striped=True),
                ])
            ], className="mb-3")
        else:
            suggestions_table = dbc.Alert("No suggestions available", color="warning")
        return html.Div([summary_card, suggestions_table])
    except Exception as e:  # pragma: no cover
        return dbc.Alert(f"Error creating display: {str(e)}", color="danger")


def get_analysis_buttons_section() -> dbc.Col:
    """Return the analysis button section."""
    return dbc.Col([
        html.Label("Analysis Type", htmlFor="security-btn", className="fw-bold mb-3"),
        dbc.Row([
            dbc.Col(dbc.Button("🔒 Security Analysis", id="security-btn", color="danger", outline=True, size="sm", className="w-100 mb-2"), width=6),
            dbc.Col(dbc.Button("📈 Trends Analysis", id="trends-btn", color="info", outline=True, size="sm", className="w-100 mb-2"), width=6),
            dbc.Col(dbc.Button("👤 Behavior Analysis", id="behavior-btn", color="warning", outline=True, size="sm", className="w-100 mb-2"), width=6),
            dbc.Col(dbc.Button("🚨 Anomaly Detection", id="anomaly-btn", color="dark", outline=True, size="sm", className="w-100 mb-2"), width=6),
            dbc.Col(dbc.Button("🤖 AI Suggestions", id="suggests-btn", color="success", outline=True, size="sm", className="w-100 mb-2"), width=6),
            dbc.Col(dbc.Button("💰 Data Quality", id="quality-btn", color="secondary", outline=True, size="sm", className="w-100 mb-2"), width=6),
            dbc.Col(dbc.Button("Unique Patterns", id="unique-patterns-btn", color="primary", outline=True, size="sm", className="w-100 mb-2"), width=6),
        ])
    ], width=6)


def get_updated_button_group() -> dbc.ButtonGroup:
    """Return the refresh button group."""
    return dbc.ButtonGroup([
        dbc.Button("🔄 Refresh Data Sources", id="refresh-sources-btn", color="outline-secondary", size="lg")
    ])


def get_initial_message() -> dbc.Alert:
    """Initial message when no analysis has run."""
    return dbc.Alert([
        html.H6("👈 Get Started"),
        html.P("1. Select a data source from dropdown"),
        html.P("2. Click any analysis button to run immediately"),
        html.P("Each button runs its analysis type automatically"),
    ], color="info")


def create_data_quality_display_corrected(data_source: str) -> html.Div:
    """Data quality analysis with proper imports."""
    try:
        if data_source.startswith("upload:") or data_source == "service:uploaded":
            filename = data_source.replace("upload:", "") if data_source.startswith("upload:") else None
            from pages.file_upload import get_uploaded_data
            uploaded_files = get_uploaded_data()
            if not uploaded_files:
                return dbc.Alert("No uploaded files found", color="warning")
            if filename is None or filename not in uploaded_files:
                filename = list(uploaded_files.keys())[0]
            if filename in uploaded_files:
                df = uploaded_files[filename]
                total_rows = len(df)
                total_cols = len(df.columns)
                missing_values = df.isnull().sum().sum()
                duplicate_rows = df.duplicated().sum()
                quality_score = max(
                    0,
                    100 - (missing_values / (total_rows * total_cols) * 100) - (duplicate_rows / total_rows * 10),
                )
                return dbc.Card([
                    dbc.CardHeader([html.H5(f"📊 Data Quality Analysis - {filename}")]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H6("Dataset Overview"),
                                html.P(f"File: {filename}"),
                                html.P(f"Rows: {total_rows:,}"),
                                html.P(f"Columns: {total_cols}"),
                                html.P(f"Missing values: {missing_values:,}"),
                                html.P(f"Duplicate rows: {duplicate_rows:,}"),
                            ], width=6),
                            dbc.Col([
                                html.H6("Quality Score"),
                                dbc.Progress(
                                    value=quality_score,
                                    label=f"{quality_score:.1f}%",
                                    color="success" if quality_score >= 80 else ("warning" if quality_score >= 60 else "danger"),
                                ),
                            ], width=6),
                        ])
                    ])
                ])
        return dbc.Alert("Data quality analysis only available for uploaded files", color="info")
    except Exception as e:  # pragma: no cover
        return dbc.Alert(f"Quality analysis error: {str(e)}", color="danger")


def create_analysis_results_display(results: Dict[str, Any], analysis_type: str) -> html.Div:
    """Create display for different analysis types."""
    try:
        total_events = results.get("total_events", 0)
        unique_users = results.get("unique_users", 0)
        unique_doors = results.get("unique_doors", 0)
        success_rate = results.get("success_rate", 0)
        analysis_focus = results.get("analysis_focus", "")
        if analysis_type == "security":
            specific_content = [
                html.P(f"Security Score: {results.get('security_score', 0):.1f}/100"),
                html.P(f"Failed Attempts: {results.get('failed_attempts', 0):,}"),
                html.P(f"Risk Level: {results.get('risk_level', 'Unknown')}")
            ]
            color = "danger" if results.get("risk_level") == "High" else "warning" if results.get("risk_level") == "Medium" else "success"
        elif analysis_type == "trends":
            specific_content = [
                html.P(f"Daily Average: {results.get('daily_average', 0):.0f} events"),
                html.P(f"Peak Usage: {results.get('peak_usage', 'Unknown')}"),
                html.P(f"Trend: {results.get('trend_direction', 'Unknown')}")
            ]
            color = "info"
        elif analysis_type == "behavior":
            specific_content = [
                html.P(f"Avg Accesses/User: {results.get('avg_accesses_per_user', 0):.1f}"),
                html.P(f"Heavy Users: {results.get('heavy_users', 0)}"),
                html.P(f"Behavior Score: {results.get('behavior_score', 'Unknown')}")
            ]
            color = "success"
        elif analysis_type == "anomaly":
            specific_content = [
                html.P(f"Anomalies Detected: {results.get('anomalies_detected', 0):,}"),
                html.P(f"Threat Level: {results.get('threat_level', 'Unknown')}") ,
                html.P(f"Status: {results.get('suspicious_activities', 'Unknown')}")
            ]
            color = "danger" if results.get("threat_level") == "Critical" else "warning"
        else:
            specific_content = [html.P("Standard analysis completed")]
            color = "info"
        return dbc.Card([
            dbc.CardHeader([html.H5(f"📊 {results.get('analysis_type', analysis_type)} Results")]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H6("📈 Summary"),
                        html.P(f"Total Events: {total_events:,}"),
                        html.P(f"Unique Users: {unique_users:,}"),
                        html.P(f"Unique Doors: {unique_doors:,}"),
                        dbc.Progress(value=success_rate * 100, label=f"Success Rate: {success_rate:.1%}", color="success" if success_rate > 0.8 else "warning"),
                    ], width=6),
                    dbc.Col([
                        html.H6(f"🎯 {analysis_type.title()} Specific"),
                        html.Div(specific_content),
                    ], width=6),
                ]),
                html.Hr(),
                dbc.Alert([html.H6("Analysis Focus"), html.P(analysis_focus)], color=color),
            ])
        ])
    except Exception as e:  # pragma: no cover
        return dbc.Alert(f"Error displaying results: {str(e)}", color="danger")


def create_limited_analysis_display(data_source: str, analysis_type: str) -> html.Div:
    """Create limited analysis display when service unavailable."""
    return dbc.Card([
        dbc.CardHeader([html.H5(f"⚠️ Limited {analysis_type.title()} Analysis")]),
        dbc.CardBody([
            dbc.Alert(
                [
                    html.H6("Service Limitations"),
                    html.P("Full analytics service is not available."),
                    html.P("Basic analysis results would be shown here."),
                ],
                color="warning",
            ),
            html.P(f"Data source: {data_source}"),
            html.P(f"Analysis type: {analysis_type}"),
        ]),
    ])


def create_data_quality_display(data_source: str) -> html.Div:
    """Create data quality analysis display."""
    try:
        if data_source.startswith("upload:"):
            filename = data_source.replace("upload:", "")
            from components.file_upload import get_uploaded_data_store
            uploaded_files = get_uploaded_data_store()
            if filename in uploaded_files:
                df = uploaded_files[filename]
                total_rows = len(df)
                total_cols = len(df.columns)
                missing_values = df.isnull().sum().sum()
                duplicate_rows = df.duplicated().sum()
                return dbc.Card([
                    dbc.CardHeader([html.H5("📊 Data Quality Analysis")]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H6("Dataset Overview"),
                                html.P(f"Rows: {total_rows:,}"),
                                html.P(f"Columns: {total_cols}"),
                                html.P(f"Missing values: {missing_values:,}"),
                                html.P(f"Duplicate rows: {duplicate_rows:,}"),
                            ], width=6),
                            dbc.Col([
                                html.H6("Quality Score"),
                                dbc.Progress(
                                    value=max(
                                        0,
                                        100 - (missing_values / total_rows * 100) - (duplicate_rows / total_rows * 10),
                                    ),
                                    label="Quality",
                                    color="success",
                                ),
                            ], width=6),
                        ])
                    ])
                ])
        return dbc.Alert("Data quality analysis only available for uploaded files", color="info")
    except Exception as e:  # pragma: no cover
        return dbc.Alert(f"Quality analysis error: {str(e)}", color="danger")


def get_initial_message_safe() -> dbc.Alert:
    """Initial message with safe ASCII text."""
    return dbc.Alert([
        html.H6("Get Started"),
        html.P("1. Select a data source from dropdown"),
        html.P("2. Click any analysis button to run immediately"),
        html.P("Each button runs its analysis type automatically"),
    ], color="info")


def create_analysis_results_display_safe(results: Dict[str, Any], analysis_type: str) -> html.Div:
    """Create safe results display without Unicode issues."""
    try:
        if isinstance(results, dict) and "error" in results:
            return dbc.Alert(str(results["error"]), color="danger")
        content = [html.H5(f"{analysis_type.title()} Results"), html.Hr()]
        if analysis_type == "suggests" and "suggestions" in results:
            content.extend([
                html.P(f"File: {results.get('filename', 'Unknown')}"),
                html.P(f"Columns analyzed: {results.get('total_columns', 0)}"),
                html.P(f"Rows processed: {results.get('total_rows', 0)}"),
                html.H6("AI Column Suggestions:"),
                html.Div([
                    html.P(
                        f"{col}: {info.get('field', 'unknown')} (confidence: {info.get('confidence', 0):.1f})"
                    )
                    for col, info in results.get('suggestions', {}).items()
                ]),
            ])
        elif analysis_type == "quality":
            content.extend([
                html.P(f"Total rows: {results.get('total_rows', 0):,}"),
                html.P(f"Total columns: {results.get('total_columns', 0)}"),
                html.P(f"Missing values: {results.get('missing_values', 0):,}"),
                html.P(f"Duplicate rows: {results.get('duplicate_rows', 0):,}"),
                html.P(f"Quality score: {results.get('quality_score', 0):.1f}%"),
            ])
        else:
            content.extend([
                html.P(f"Total events: {results.get('total_events', 0):,}"),
                html.P(f"Unique users: {results.get('unique_users', 0):,}"),
                html.P(f"Success rate: {results.get('success_rate', 0):.1%}"),
            ])
        return dbc.Card([dbc.CardBody(content)])
    except Exception as e:  # pragma: no cover
        return dbc.Alert(f"Display error: {str(e)}", color="danger")

