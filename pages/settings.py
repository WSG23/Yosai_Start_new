"""Settings placeholder page"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html
from utils.unicode_handler import sanitize_unicode_input


def layout() -> html.Div:
    """Settings page layout."""
    header = html.H1(sanitize_unicode_input("Settings"), className="text-primary mb-4")
    form = dbc.Form(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("User Preferences"),
                            dbc.Input(placeholder="Coming soon", disabled=True),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("System Configuration"),
                            dbc.Input(placeholder="Coming soon", disabled=True),
                        ],
                        md=6,
                    ),
                ],
                className="mb-3",
            )
        ]
    )
    return dbc.Container([header, form], fluid=True)


__all__ = ["layout"]
