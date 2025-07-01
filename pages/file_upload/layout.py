import pandas as pd
from dash import html, dcc
import dash_bootstrap_components as dbc
from services.upload_service import create_file_preview


def build_success_alert(
    filename: str,
    rows: int,
    cols: int,
    *,
    prefix: str = "Successfully uploaded",
    processed: bool = True,
) -> dbc.Alert:
    """Return a Bootstrap alert describing a successful file upload."""

    details = f"\U0001F4CA {rows:,} rows × {cols} columns"
    if processed:
        details += " processed"

    return dbc.Alert(
        [
            html.H6(
                [html.I(className="fas fa-check-circle me-2"), f"{prefix} {filename}"],
                className="alert-heading",
            ),
            html.P(details),
        ],
        color="success",
        className="mb-3",
    )


def build_failure_alert(message: str) -> dbc.Alert:
    """Return a Bootstrap alert describing a failed file upload."""

    return dbc.Alert(
        [html.H6("Upload Failed", className="alert-heading"), html.P(message)],
        color="danger",
    )


def build_file_preview_component(df: pd.DataFrame, filename: str) -> html.Div:
    """Return a preview card and configuration buttons for an uploaded file."""

    return html.Div(
        [
            create_file_preview(df.head(5), filename),
            dbc.Card(
                [
                    dbc.CardHeader([html.H6("📋 Data Configuration", className="mb-0")]),
                    dbc.CardBody(
                        [
                            html.P("Configure your data for analysis:", className="mb-3"),
                            dbc.ButtonGroup(
                                [
                                    dbc.Button(
                                        "📋 Verify Columns",
                                        id="verify-columns-btn-simple",
                                        color="primary",
                                        size="sm",
                                    ),
                                    dbc.Button(
                                        "🤖 Classify Devices",
                                        id="classify-devices-btn",
                                        color="info",
                                        size="sm",
                                    ),
                                ],
                                className="w-100",
                            ),
                        ]
                    ),
                ],
                className="mb-3",
            ),
        ]
    )


def layout():
    """File upload page layout with persistent storage"""
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H1("📁 File Upload", className="text-primary mb-2"),
                            html.P(
                                "Upload CSV, Excel, or JSON files for analysis",
                                className="text-muted mb-4",
                            ),
                        ]
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [html.H5("📤 Upload Data Files", className="mb-0")]
                                    ),
                                    dbc.CardBody(
                                        [
                                            dcc.Upload(
                                                id="upload-data",
                                                children=html.Div(
                                                    [
                                                        html.I(
                                                            className="fas fa-cloud-upload-alt fa-4x mb-3 text-primary"
                                                        ),
                                                        html.H5(
                                                            "Drag and Drop or Click to Upload",
                                                            className="text-primary",
                                                        ),
                                                        html.P(
                                                            "Supports CSV, Excel (.xlsx, .xls), and JSON files",
                                                            className="text-muted mb-0",
                                                        ),
                                                    ]
                                                ),
                                                style={
                                                    "width": "100%",
                                                    "border": "2px dashed #007bff",
                                                    "borderRadius": "8px",
                                                    "textAlign": "center",
                                                    "cursor": "pointer",
                                                    "backgroundColor": "#f8f9fa",
                                                },
                                                multiple=True,
                                            )
                                        ]
                                    ),
                                ]
                            )
                        ]
                    )
                ]
            ),
            dbc.Row([dbc.Col([html.Div(id="upload-results")])], className="mb-4"),
            dbc.Row([dbc.Col([html.Div(id="file-preview")])]),
            dbc.Row([dbc.Col([html.Div(id="upload-nav")])]),
            html.Div(id="toast-container"),
            html.Div(
                [
                    dbc.Button("", id="verify-columns-btn-simple", style={"display": "none"}),
                    dbc.Button("", id="classify-devices-btn", style={"display": "none"}),
                ],
                style={"display": "none"},
            ),
            dcc.Store(id="file-info-store", data={}),
            dcc.Store(id="current-file-info-store"),
            dcc.Store(id="current-session-id", data="session_123"),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Column Mapping")),
                    dbc.ModalBody("Configure column mappings here", id="modal-body"),
                    dbc.ModalFooter(
                        [
                            dbc.Button("Cancel", id="column-verify-cancel", color="secondary"),
                            dbc.Button("Confirm", id="column-verify-confirm", color="success"),
                        ]
                    ),
                ],
                id="column-verification-modal",
                is_open=False,
                size="xl",
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Device Classification")),
                    dbc.ModalBody("", id="device-modal-body"),
                    dbc.ModalFooter(
                        [
                            dbc.Button("Cancel", id="device-verify-cancel", color="secondary"),
                            dbc.Button("Confirm", id="device-verify-confirm", color="success"),
                        ]
                    ),
                ],
                id="device-verification-modal",
                is_open=False,
                size="xl",
            ),
        ],
        fluid=True,
    )


__all__ = ["layout", "build_success_alert", "build_failure_alert", "build_file_preview_component"]
