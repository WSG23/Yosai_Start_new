import logging
from datetime import datetime
from typing import Any, Dict, List, Tuple

from dash import html, dcc
from dash.dash import no_update
from dash._callback_context import callback_context
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc

from core.unified_callback_coordinator import UnifiedCallbackCoordinator
from services.upload_service import process_uploaded_file
from utils.upload_store import uploaded_data_store as _uploaded_data_store
from services.ai_suggestions import generate_column_suggestions

from .layout import build_success_alert, build_failure_alert, build_file_preview_component
from .helpers import analyze_device_name_with_ai, get_uploaded_data, learning_service

logger = logging.getLogger(__name__)


def highlight_upload_area(n_clicks):
    if n_clicks:
        return {
            "width": "100%",
            "border": "3px dashed #28a745",
            "borderRadius": "8px",
            "textAlign": "center",
            "cursor": "pointer",
            "backgroundColor": "#d4edda",
            "animation": "pulse 1s infinite",
        }
    return {
        "width": "100%",
        "border": "2px dashed #007bff",
        "borderRadius": "8px",
        "textAlign": "center",
        "cursor": "pointer",
        "backgroundColor": "#f8f9fa",
    }


def restore_upload_state(pathname: str) -> Tuple[Any, Any, Any, Any, Any, Any, Any]:
    if pathname != "/file-upload" or not _uploaded_data_store:
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
        )

    upload_results: List[Any] = []
    file_preview_components: List[Any] = []
    current_file_info: Dict[str, Any] = {}

    for filename, df in _uploaded_data_store.get_all_data().items():
        rows = len(df)
        cols = len(df.columns)

        upload_results.append(
            build_success_alert(
                filename,
                rows,
                cols,
                prefix="Previously uploaded:",
                processed=False,
            )
        )

        file_preview_components.append(build_file_preview_component(df, filename))

        current_file_info = {
            "filename": filename,
            "rows": rows,
            "columns": cols,
            "column_names": df.columns.tolist(),
            "ai_suggestions": generate_column_suggestions(df.columns.tolist()),
        }

    upload_nav = html.Div(
        [
            html.Hr(),
            html.H5("Ready to analyze?"),
            dbc.Button("🚀 Go to Analytics", href="/analytics", color="success", size="lg"),
        ]
    )

    return (
        upload_results,
        file_preview_components,
        {},
        upload_nav,
        current_file_info,
        False,
        False,
    )


def process_uploaded_files(contents_list: List[str] | str, filenames_list: List[str] | str) -> Tuple[Any, Any, Any, Any, Any, Any, Any]:
    if not contents_list:
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
        )

    _uploaded_data_store.clear_all()

    if not isinstance(contents_list, list):
        contents_list = [contents_list]
    if not isinstance(filenames_list, list):
        filenames_list = [filenames_list]

    upload_results: List[Any] = []
    file_preview_components: List[Any] = []
    file_info_dict: Dict[str, Any] = {}
    current_file_info: Dict[str, Any] = {}

    for content, filename in zip(contents_list, filenames_list):
        try:
            result = process_uploaded_file(content, filename)

            if result["success"]:
                df = result["data"]
                rows = len(df)
                cols = len(df.columns)

                _uploaded_data_store.add_file(filename, df)

                upload_results.append(build_success_alert(filename, rows, cols))

                file_preview_components.append(build_file_preview_component(df, filename))

                column_names = df.columns.tolist()
                file_info_dict[filename] = {
                    "filename": filename,
                    "rows": rows,
                    "columns": cols,
                    "column_names": column_names,
                    "upload_time": result["upload_time"].isoformat(),
                    "ai_suggestions": generate_column_suggestions(column_names),
                }
                current_file_info = file_info_dict[filename]

                try:
                    user_mappings = learning_service.get_user_device_mappings(filename)
                    if user_mappings:
                        from services.ai_mapping_store import ai_mapping_store

                        ai_mapping_store.clear()
                        for device, mapping in user_mappings.items():
                            mapping["source"] = "user_confirmed"
                            ai_mapping_store.set(device, mapping)
                        logger.info(f"✅ Loaded {len(user_mappings)} saved mappings - AI SKIPPED")
                    else:
                        logger.info("🆕 First upload - AI will be used")
                        from services.ai_mapping_store import ai_mapping_store

                        ai_mapping_store.clear()
                except Exception as e:
                    logger.info(f"⚠️ Error: {e}")

            else:
                upload_results.append(build_failure_alert(result["error"]))

        except Exception as e:
            upload_results.append(build_failure_alert(f"Error processing {filename}: {str(e)}"))

    upload_nav = []
    if file_info_dict:
        upload_nav = html.Div(
            [
                html.Hr(),
                html.H5("Ready to analyze?"),
                dbc.Button("🚀 Go to Analytics", href="/analytics", color="success", size="lg"),
            ]
        )

    return (
        upload_results,
        file_preview_components,
        file_info_dict,
        upload_nav,
        current_file_info,
        no_update,
        no_update,
    )


def handle_modal_dialogs(
    verify_clicks: int | None,
    classify_clicks: int | None,
    confirm_clicks: int | None,
    cancel_col_clicks: int | None,
    cancel_dev_clicks: int | None,
) -> Tuple[Any, Any, Any]:
    ctx = callback_context
    trigger_id = ctx.triggered[0]["prop_id"] if ctx.triggered else ""

    if "verify-columns-btn-simple" in trigger_id and verify_clicks:
        return no_update, True, no_update

    if "classify-devices-btn" in trigger_id and classify_clicks:
        return no_update, no_update, True

    if "column-verify-confirm" in trigger_id and confirm_clicks:
        success_alert = dbc.Toast(
            [html.P("✅ Column mappings saved!")],
            header="Saved",
            is_open=True,
            dismissable=True,
            duration=3000,
        )
        return success_alert, False, no_update

    if "column-verify-cancel" in trigger_id or "device-verify-cancel" in trigger_id:
        return no_update, False, False

    return no_update, no_update, no_update


def apply_ai_suggestions(n_clicks, file_info):
    if not n_clicks or not file_info:
        return [no_update]

    ai_suggestions = file_info.get("ai_suggestions", {})
    columns = file_info.get("columns", [])

    logger.info(f"🤖 Applying AI suggestions for {len(columns)} columns")

    suggested_values = []
    for column in columns:
        suggestion = ai_suggestions.get(column, {})
        confidence = suggestion.get("confidence", 0.0)
        field = suggestion.get("field", "")

        if confidence > 0.3 and field:
            suggested_values.append(field)
            logger.info(f"   ✅ {column} -> {field} ({confidence:.0%})")
        else:
            suggested_values.append(None)
            logger.info(f"   ❓ {column} -> No confident suggestion ({confidence:.0%})")

    return [suggested_values]


def populate_device_modal_with_learning(is_open, file_info):
    if not is_open:
        return "Modal closed"

    logger.info("🔧 Populating device modal...")

    try:
        uploaded_data = get_uploaded_data()
        if not uploaded_data:
            return dbc.Alert("No uploaded data found", color="warning")

        all_devices = set()
        device_columns = ["door_id", "device_name", "location", "door", "device"]

        for filename, df in uploaded_data.items():
            logger.info(f"📄 Processing {filename} with {len(df)} rows")

            for col in df.columns:
                col_lower = col.lower().strip()
                if any(device_col in col_lower for device_col in device_columns):
                    unique_vals = df[col].dropna().unique()
                    all_devices.update(str(val) for val in unique_vals)
                    logger.info(f"   Found {len(unique_vals)} devices in column '{col}'")

                    logger.debug(f"🔍 DEBUG - First 10 device names from '{col}':")
                    sample_devices = unique_vals[:10]
                    for i, device in enumerate(sample_devices, 1):
                        logger.debug(f"   {i:2d}. {device}")

                    logger.debug("🤖 DEBUG - Testing AI on sample devices:")
                    try:
                        from services.ai_device_generator import AIDeviceGenerator
                        ai_gen = AIDeviceGenerator()
                        for device in sample_devices[:5]:
                            try:
                                result = ai_gen.generate_device_attributes(str(device))
                                logger.info(
                                    f"   🚪 '{device}' → Name: '{result.device_name}', Floor: {result.floor_number}, Security: {result.security_level}, Confidence: {result.confidence:.1%}"
                                )
                                logger.info(
                                    f"      Access: Entry={result.is_entry}, Exit={result.is_exit}, Elevator={result.is_elevator}"
                                )
                                logger.info(f"      Reasoning: {result.ai_reasoning}")
                            except Exception as e:
                                logger.info(f"   ❌ AI error on '{device}': {e}")
                    except Exception as e:
                        logger.debug(f"🤖 DEBUG - AI import error: {e}")

        actual_devices = sorted(list(all_devices))
        logger.info(f"🎯 Total unique devices found: {len(actual_devices)}")

        if not actual_devices:
            return dbc.Alert(
                [
                    html.H6("No devices detected"),
                    html.P(
                        "No device/door columns found in uploaded data. Expected columns: door_id, device_name, location, etc."
                    ),
                ],
                color="warning",
            )

        table_rows = []
        for i, device_name in enumerate(actual_devices):
            ai_attributes = analyze_device_name_with_ai(device_name)

            table_rows.append(
                html.Tr(
                    [
                        html.Td(
                            [
                                html.Strong(device_name),
                                html.Br(),
                                html.Small(
                                    f"AI Confidence: {ai_attributes.get('confidence', 0.5):.0%}",
                                    className="text-success",
                                ),
                            ]
                        ),
                        html.Td(
                            [
                                dbc.Input(
                                    id={"type": "device-floor", "index": i},
                                    type="number",
                                    min=0,
                                    max=50,
                                    value=ai_attributes.get("floor_number", 1),
                                    placeholder="Floor",
                                    size="sm",
                                )
                            ]
                        ),
                        html.Td(
                            dbc.Checklist(
                                id={"type": "device-access", "index": i},
                                options=[
                                    {"label": "Entry", "value": "is_entry"},
                                    {"label": "Exit", "value": "is_exit"},
                                    {"label": "Elevator", "value": "is_elevator"},
                                    {"label": "Stairwell", "value": "is_stairwell"},
                                    {"label": "Fire Exit", "value": "is_fire_escape"},
                                    {"label": "Restricted", "value": "is_restricted"},
                                ],
                                value=[
                                    key
                                    for key in [
                                        "is_entry",
                                        "is_exit",
                                        "is_elevator",
                                        "is_stairwell",
                                        "is_fire_escape",
                                        "is_restricted",
                                    ]
                                    if ai_attributes.get(key, ai_attributes.get(key.replace("is_", "")))
                                ],
                                inline=False,
                            ),
                        ),
                        html.Td(
                            dbc.Input(
                                id={"type": "device-security", "index": i},
                                type="number",
                                min=0,
                                max=10,
                                value=ai_attributes.get("security_level", 5),
                                placeholder="0-10",
                                size="sm",
                            )
                        ),
                    ]
                )
            )

        return dbc.Container(
            [
                dbc.Alert(
                    [
                        html.Strong("🤖 AI Analysis: "),
                        f"Analyzed {len(actual_devices)} devices. Check console for detailed AI debug info.",
                    ],
                    color="info",
                    className="mb-3",
                ),
                dbc.Table(
                    [
                        html.Thead(
                            [
                                html.Tr(
                                    [
                                        html.Th("Device Name"),
                                        html.Th("Floor"),
                                        html.Th("Access Types"),
                                        html.Th("Security Level"),
                                    ]
                                )
                            ]
                        ),
                        html.Tbody(table_rows),
                    ],
                    striped=True,
                    hover=True,
                ),
            ]
        )

    except Exception as e:
        logger.info(f"❌ Error in device modal: {e}")
        return dbc.Alert(f"Error: {e}", color="danger")


def populate_modal_content(is_open, file_info):
    if not is_open or not file_info:
        return "Modal closed" if not is_open else dbc.Alert("No file information available", color="warning")

    filename = (
        str(file_info.get("filename", "Unknown"))
        .replace("⛑️", "")
        .replace("🔧", "")
        .replace("❌", "")
    )
    columns = file_info.get("column_names", []) or file_info.get("columns", [])
    ai_suggestions = file_info.get("ai_suggestions", {})

    if not columns:
        return dbc.Alert(f"No columns found in {filename}", color="warning")

    standard_fields = [
        {"field": "person_id", "label": "Person/User ID", "description": "Identifies who accessed"},
        {"field": "door_id", "label": "Door/Location ID", "description": "Identifies where access occurred"},
        {"field": "timestamp", "label": "Timestamp", "description": "When access occurred"},
        {"field": "access_result", "label": "Access Result", "description": "Success/failure of access"},
        {"field": "token_id", "label": "Token/Badge ID", "description": "Badge or card identifier"},
        {"field": "device_status", "label": "Device Status", "description": "Status of access device"},
        {"field": "entry_type", "label": "Entry/Exit Type", "description": "Direction of access"},
    ]

    csv_column_options = [{"label": f'"{col}"', "value": col} for col in columns]
    csv_column_options.append({"label": "Skip this field", "value": "skip"})

    table_rows = []
    for standard_field in standard_fields:
        field_name = standard_field["field"]

        suggested_csv_column = None
        ai_confidence = 0.0
        for csv_col, suggestion in ai_suggestions.items():
            if suggestion.get("field") == field_name:
                suggested_csv_column = csv_col
                ai_confidence = suggestion.get("confidence", 0.0)
                break

        table_rows.append(
            html.Tr(
                [
                    html.Td(
                        [
                            html.Strong(standard_field["label"]),
                            html.Br(),
                            html.Small(standard_field["description"], className="text-muted"),
                            html.Br(),
                            html.Code(field_name, className="bg-info text-white px-2 py-1 rounded small"),
                        ],
                        style={"width": "40%"},
                    ),
                    html.Td(
                        [
                            dcc.Dropdown(
                                id={"type": "standard-field-mapping", "field": field_name},
                                options=csv_column_options,
                                placeholder=f"Select CSV column for {field_name}",
                                value=suggested_csv_column,
                                style={"minWidth": "200px"},
                            )
                        ],
                        style={"width": "50%"},
                    ),
                    html.Td(
                        [
                            dbc.Badge(
                                f"AI: {ai_confidence:.0%}" if suggested_csv_column else "No AI suggestion",
                                color=("success" if ai_confidence > 0.7 else ("warning" if ai_confidence > 0.4 else "secondary")),
                                className="small",
                            )
                        ],
                        style={"width": "10%"},
                    ),
                ]
            )
        )

    return [
        dbc.Alert(
            [
                html.H6(
                    f"Map Analytics Fields to CSV Columns from {filename}",
                    className="mb-2",
                ),
                html.P(
                    [
                        "Your CSV has these columns: ",
                        ", ".join([col for col in columns[:5]]),
                        f"{'...' if len(columns) > 5 else ''}",
                    ],
                    className="mb-2",
                ),
                html.P(
                    [
                        html.Strong("Instructions: "),
                        "Each row below represents a field that our analytics system expects. ",
                        "Select which column from your CSV file should provide the data for each field.",
                    ],
                    className="mb-0",
                ),
            ],
            color="primary",
            className="mb-3",
        ),
        dbc.Table(
            [
                html.Thead(
                    [
                        html.Tr(
                            [
                                html.Th("Analytics Field (Fixed)", style={"width": "40%"}),
                                html.Th("Maps to CSV Column (Variable)", style={"width": "50%"}),
                                html.Th("AI Confidence", style={"width": "10%"}),
                            ]
                        )
                    ]
                ),
                html.Tbody(table_rows),
            ],
            striped=True,
            hover=True,
        ),
        dbc.Card(
            [
                dbc.CardHeader(html.H6("Your CSV Columns", className="mb-0")),
                dbc.CardBody(
                    [
                        html.P("Available columns from your uploaded file:"),
                        html.Div(
                            [
                                dbc.Badge(col, color="light", text_color="dark", className="me-1 mb-1")
                                for col in columns
                            ]
                        ),
                    ]
                ),
            ],
            className="mt-3",
        ),
    ]


def save_confirmed_device_mappings(confirm_clicks, floors, security, access, special, file_info):
    if not confirm_clicks or not file_info:
        return no_update, no_update, no_update

    try:
        devices = file_info.get("devices", [])
        filename = file_info.get("filename", "")

        user_mappings = {}
        for i, device in enumerate(devices):
            user_mappings[device] = {
                "floor_number": floors[i] if i < len(floors) else 1,
                "security_level": security[i] if i < len(security) else 5,
                "is_entry": "entry" in (access[i] if i < len(access) else []),
                "is_exit": "exit" in (access[i] if i < len(access) else []),
                "is_restricted": "is_restricted" in (special[i] if i < len(special) else []),
                "confidence": 1.0,
                "device_name": device,
                "source": "user_confirmed",
                "saved_at": datetime.now().isoformat(),
            }

        learning_service.save_user_device_mappings(filename, user_mappings)

        from services.ai_mapping_store import ai_mapping_store
        ai_mapping_store.update(user_mappings)

        logger.info(f"\u2705 Saved {len(user_mappings)} confirmed device mappings to database")

        success_alert = dbc.Toast(
            "✅ Device mappings saved to database!",
            header="Confirmed & Saved",
            is_open=True,
            dismissable=True,
            duration=3000,
        )

        return success_alert, False, False

    except Exception as e:
        logger.info(f"\u274c Error saving device mappings: {e}")
        error_alert = dbc.Toast(
            f"❌ Error saving mappings: {e}",
            header="Error",
            is_open=True,
            dismissable=True,
            duration=5000,
        )
        return error_alert, no_update, no_update


def register_callbacks(manager: UnifiedCallbackCoordinator) -> None:
    manager.register_callback(
        Output("upload-data", "style"),
        Input("upload-more-btn", "n_clicks"),
        prevent_initial_call=True,
        callback_id="highlight_upload_area",
        component_name="file_upload",
    )(highlight_upload_area)

    manager.register_callback(
        [
            Output("upload-results", "children", allow_duplicate=True),
            Output("file-preview", "children", allow_duplicate=True),
            Output("file-info-store", "data", allow_duplicate=True),
            Output("upload-nav", "children", allow_duplicate=True),
            Output("current-file-info-store", "data", allow_duplicate=True),
            Output("column-verification-modal", "is_open", allow_duplicate=True),
            Output("device-verification-modal", "is_open", allow_duplicate=True),
        ],
        Input("url", "pathname"),
        prevent_initial_call="initial_duplicate",
        allow_duplicate=True,
        callback_id="restore_upload_state",
        component_name="file_upload",
    )(restore_upload_state)

    manager.register_callback(
        [
            Output("upload-results", "children", allow_duplicate=True),
            Output("file-preview", "children", allow_duplicate=True),
            Output("file-info-store", "data", allow_duplicate=True),
            Output("upload-nav", "children", allow_duplicate=True),
            Output("current-file-info-store", "data", allow_duplicate=True),
            Output("column-verification-modal", "is_open", allow_duplicate=True),
            Output("device-verification-modal", "is_open", allow_duplicate=True),
        ],
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        prevent_initial_call=True,
        allow_duplicate=True,
        callback_id="process_uploaded_files",
        component_name="file_upload",
    )(process_uploaded_files)

    manager.register_callback(
        [
            Output("toast-container", "children", allow_duplicate=True),
            Output("column-verification-modal", "is_open", allow_duplicate=True),
            Output("device-verification-modal", "is_open", allow_duplicate=True),
        ],
        [
            Input("verify-columns-btn-simple", "n_clicks"),
            Input("classify-devices-btn", "n_clicks"),
            Input("column-verify-confirm", "n_clicks"),
            Input("column-verify-cancel", "n_clicks"),
            Input("device-verify-cancel", "n_clicks"),
        ],
        prevent_initial_call=True,
        allow_duplicate=True,
        callback_id="handle_modal_dialogs",
        component_name="file_upload",
    )(handle_modal_dialogs)

    manager.register_callback(
        [Output({"type": "column-mapping", "index": ALL}, "value")],
        [Input("column-verify-ai-auto", "n_clicks")],
        [State("current-file-info-store", "data")],
        prevent_initial_call=True,
        callback_id="apply_ai_suggestions",
        component_name="file_upload",
    )(apply_ai_suggestions)

    manager.register_callback(
        Output("device-modal-body", "children"),
        Input("device-verification-modal", "is_open"),
        State("current-file-info-store", "data"),
        prevent_initial_call=True,
        callback_id="populate_device_modal_with_learning",
        component_name="file_upload",
    )(populate_device_modal_with_learning)

    manager.register_callback(
        Output("modal-body", "children"),
        [Input("column-verification-modal", "is_open"), Input("current-file-info-store", "data")],
        prevent_initial_call=True,
        callback_id="populate_modal_content",
        component_name="file_upload",
    )(populate_modal_content)

    manager.register_callback(
        [
            Output("toast-container", "children", allow_duplicate=True),
            Output("column-verification-modal", "is_open", allow_duplicate=True),
            Output("device-verification-modal", "is_open", allow_duplicate=True),
        ],
        [Input("device-verify-confirm", "n_clicks")],
        [
            State({"type": "device-floor", "index": ALL}, "value"),
            State({"type": "device-security", "index": ALL}, "value"),
            State({"type": "device-access", "index": ALL}, "value"),
            State({"type": "device-special", "index": ALL}, "value"),
            State("current-file-info-store", "data"),
        ],
        prevent_initial_call=True,
        callback_id="save_confirmed_device_mappings",
        component_name="file_upload",
    )(save_confirmed_device_mappings)


__all__ = ["register_callbacks"]
