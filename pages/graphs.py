"""Graphs placeholder page"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html, dcc
from utils.unicode_handler import sanitize_unicode_input


def layout() -> html.Div:
    """Graphs page layout."""
    header = html.H1(sanitize_unicode_input("Graphs"), className="text-primary mb-4")
    tabs = dcc.Tabs(
        id="graph-tabs",
        children=[
            dcc.Tab(label="Bar", value="bar"),
            dcc.Tab(label="Line", value="line"),
            dcc.Tab(label="Pie", value="pie"),
        ],
    )
    placeholder = html.Div(id="graph-content", children=dbc.Alert("Charts will be added soon", color="info"))
    return dbc.Container([header, tabs, placeholder], fluid=True)


__all__ = ["layout"]
