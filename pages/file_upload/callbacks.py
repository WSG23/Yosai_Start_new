import base64
import logging
from typing import Any, List, Tuple

import pandas as pd
from dash import html, no_update
import dash_bootstrap_components as dbc

from services.file_processor_service import FileProcessorService
from core.unified_callback_coordinator import UnifiedCallbackCoordinator

logger = logging.getLogger(__name__)


def process_uploaded_file_simple(content: str, filename: str) -> dict:
    """Simplified file processing"""
    try:
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)

        processor = FileProcessorService()
        validation = processor.validate_file(filename, len(decoded))
        if not validation['valid']:
            return {
                'success': False,
                'error': f"Validation failed: {'; '.join(validation['issues'])}"
            }

        df = processor.process_file(decoded, filename)

        return {
            'success': True,
            'data': df,
            'filename': filename,
            'rows': len(df),
            'columns': list(df.columns)
        }
    except Exception as e:
        logger.error(f"Error processing {filename}: {e}")
        return {'success': False, 'error': str(e)}


def handle_file_upload_simple(contents, filenames):
    """Simplified upload handler"""
    if not contents:
        return no_update, no_update, no_update

    if not isinstance(contents, list):
        contents = [contents]
        filenames = [filenames]

    results: List[Any] = []
    previews: List[Any] = []
    file_info: dict = {}

    for content, filename in zip(contents, filenames):
        result = process_uploaded_file_simple(content, filename)
        if result['success']:
            df = result['data']
            results.append(
                dbc.Alert(
                    f"✅ Successfully uploaded {filename}: {len(df)} rows, {len(df.columns)} columns",
                    color="success",
                )
            )
            previews.append(
                dbc.Card([
                    dbc.CardHeader(f"📄 {filename}"),
                    dbc.CardBody([
                        html.P(f"Rows: {len(df)} | Columns: {len(df.columns)}"),
                        html.P(f"Columns: {', '.join(df.columns.tolist())}"),
                        html.Div([
                            html.H6("Preview (first 5 rows):"),
                            dbc.Table.from_dataframe(df.head(), striped=True, bordered=True, hover=True, size="sm"),
                        ])
                    ])
                ], className="mb-3")
            )
            file_info[filename] = {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist()
            }
        else:
            results.append(
                dbc.Alert(f"❌ Failed to upload {filename}: {result['error']}", color="danger")
            )

    return results, previews, file_info


def register_callbacks(manager: UnifiedCallbackCoordinator) -> None:
    """Register simplified callbacks"""
    from dash import Input, Output

    @manager.register_callback(
        [
            Output("upload-results", "children"),
            Output("file-preview", "children"),
            Output("file-info-store", "data"),
        ],
        [Input("upload-data", "contents")],
        [Input("upload-data", "filename")],
        prevent_initial_call=True,
        callback_id="handle_file_upload",
        component_name="file_upload",
    )
    def upload_callback(contents, filenames):
        return handle_file_upload_simple(contents, filenames)
