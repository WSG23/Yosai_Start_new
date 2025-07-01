"""Dashboard placeholder page"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html
from utils.unicode_handler import sanitize_unicode_input


def layout() -> html.Div:
    """Dashboard page layout."""
    heading = html.H1(sanitize_unicode_input("Dashboard"), className="text-primary mb-4")
    metrics = dbc.Row(
        [
            dbc.Col(dbc.Card(dbc.CardBody([html.H5("Metric 1"), html.P("Coming soon")]), className="text-center"), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([html.H5("Metric 2"), html.P("Coming soon")]), className="text-center"), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([html.H5("Metric 3"), html.P("Coming soon")]), className="text-center"), md=3),
            dbc.Col(dbc.Card(dbc.CardBody([html.H5("Metric 4"), html.P("Coming soon")]), className="text-center"), md=3),
        ],
        className="mb-4",
    )
    placeholder = dbc.Alert("Real-time widgets will appear here", color="info")
    return dbc.Container([heading, metrics, placeholder], fluid=True)


__all__ = ["layout"]
