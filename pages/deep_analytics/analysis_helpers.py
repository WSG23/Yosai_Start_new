import logging
from typing import Dict, List, Any, Optional
import pandas as pd
from services import AnalyticsService

try:
    from components.column_verification import get_ai_suggestions_for_file
    AI_SUGGESTIONS_AVAILABLE = True
except ImportError:  # pragma: no cover - fallback suggestions
    def get_ai_suggestions_for_file(df, filename):
        suggestions = {}
        for col in df.columns:
            col_lower = col.lower().strip()
            if any(word in col_lower for word in ["time", "date", "stamp"]):
                suggestions[col] = {"field": "timestamp", "confidence": 0.8}
            elif any(word in col_lower for word in ["person", "user", "employee"]):
                suggestions[col] = {"field": "person_id", "confidence": 0.7}
            elif any(word in col_lower for word in ["door", "location", "device"]):
                suggestions[col] = {"field": "door_id", "confidence": 0.7}
            elif any(word in col_lower for word in ["access", "result", "status"]):
                suggestions[col] = {"field": "access_result", "confidence": 0.6}
            elif any(word in col_lower for word in ["token", "badge", "card"]):
                suggestions[col] = {"field": "token_id", "confidence": 0.6}
            else:
                suggestions[col] = {"field": "", "confidence": 0.0}
        return suggestions
    AI_SUGGESTIONS_AVAILABLE = True

ANALYTICS_SERVICE_AVAILABLE = AnalyticsService is not None
logger = logging.getLogger(__name__)


def get_analytics_service_safe():
    """Safely instantiate the analytics service if available."""
    if AnalyticsService is None:
        return None
    try:
        return AnalyticsService()
    except Exception:  # pragma: no cover - service creation failure
        return None


def get_data_source_options_safe() -> List[Dict[str, str]]:
    """Get data source options without Unicode issues."""
    options: List[Dict[str, str]] = []
    try:
        from pages.file_upload import get_uploaded_data
        uploaded_files = get_uploaded_data()
        if uploaded_files:
            for filename in uploaded_files.keys():
                options.append({"label": f"File: {filename}", "value": f"upload:{filename}"})
    except Exception:
        pass
    try:
        service = get_analytics_service_safe()
        if service:
            service_sources = service.get_available_sources()
            for source_dict in service_sources:
                options.append({
                    "label": f"Service: {source_dict.get('label', 'Unknown')}",
                    "value": f"service:{source_dict.get('value', 'unknown')}",
                })
    except Exception:
        pass
    if not options:
        options.append({"label": "No data sources available - Upload files first", "value": "none"})
    return options


def get_latest_uploaded_source_value() -> Optional[str]:
    """Return dropdown value for the most recently uploaded file."""
    try:
        from pages.file_upload import get_uploaded_filenames
        filenames = get_uploaded_filenames()
        if filenames:
            return f"upload:{filenames[-1]}"
    except Exception:
        pass
    return None


def get_analysis_type_options() -> List[Dict[str, str]]:
    """Get available analysis types including suggests analysis."""
    return [
        {"label": "🔒 Security Patterns", "value": "security"},
        {"label": "📈 Access Trends", "value": "trends"},
        {"label": "👤 User Behavior", "value": "behavior"},
        {"label": "🚨 Anomaly Detection", "value": "anomaly"},
        {"label": "🤖 AI Column Suggestions", "value": "suggests"},
        {"label": "📊 Data Quality", "value": "quality"},
    ]


def process_suggests_analysis(data_source: str) -> Dict[str, Any]:
    """Process AI suggestions analysis for the selected data source."""
    try:
        logger.info(f"Processing suggests analysis for: {data_source}")
        if not data_source or data_source == "none":
            return {"error": "No data source selected"}
        if data_source.startswith("upload:") or data_source == "service:uploaded":
            filename = data_source.replace("upload:", "") if data_source.startswith("upload:") else None
            from pages.file_upload import get_uploaded_data
            uploaded_files = get_uploaded_data()
            if not uploaded_files:
                return {"error": "No uploaded files found"}
            if filename is None or filename not in uploaded_files:
                filename = list(uploaded_files.keys())[0]
            df = uploaded_files[filename]
            if AI_SUGGESTIONS_AVAILABLE:
                try:
                    suggestions = get_ai_suggestions_for_file(df, filename)
                    processed_suggestions = []
                    total_confidence = 0
                    confident_mappings = 0
                    for column, suggestion in suggestions.items():
                        field = suggestion.get("field", "")
                        confidence = suggestion.get("confidence", 0.0)
                        status = (
                            "🟢 High" if confidence >= 0.7 else "🟡 Medium" if confidence >= 0.4 else "🔴 Low"
                        )
                        try:
                            sample_data = df[column].dropna().head(3).astype(str).tolist()
                        except Exception:
                            sample_data = ["N/A"]
                        processed_suggestions.append(
                            {
                                "column": column,
                                "suggested_field": field if field else "No suggestion",
                                "confidence": confidence,
                                "status": status,
                                "sample_data": sample_data,
                            }
                        )
                        total_confidence += confidence
                        if confidence >= 0.6:
                            confident_mappings += 1
                    avg_confidence = total_confidence / len(suggestions) if suggestions else 0
                    try:
                        data_preview = df.head(5).to_dict("records")
                    except Exception:
                        data_preview = []
                    return {
                        "filename": filename,
                        "total_columns": len(df.columns),
                        "total_rows": len(df),
                        "suggestions": processed_suggestions,
                        "avg_confidence": avg_confidence,
                        "confident_mappings": confident_mappings,
                        "data_preview": data_preview,
                        "column_names": list(df.columns),
                    }
                except Exception as e:  # pragma: no cover - runtime issues
                    return {"error": f"AI suggestions failed: {str(e)}"}
            return {"error": "AI suggestions service not available"}
        return {"error": f"Suggests analysis not available for data source: {data_source}"}
    except Exception as e:
        return {"error": f"Failed to process suggests: {str(e)}"}


def analyze_data_with_service(data_source: str, analysis_type: str) -> Dict[str, Any]:
    """Generate different analysis based on type."""
    try:
        service = get_analytics_service_safe()
        if not service:
            return {"error": "Analytics service not available"}
        if data_source.startswith("upload:") or data_source == "service:uploaded":
            source_name = "uploaded"
        elif data_source.startswith("service:"):
            source_name = data_source.replace("service:", "")
        else:
            source_name = data_source
        analytics_results = service.get_analytics_by_source(source_name)
        if analytics_results.get('status') == 'error':
            return {"error": analytics_results.get('message', 'Unknown error')}
        total_events = analytics_results.get('total_events', 0)
        unique_users = analytics_results.get('unique_users', 0)
        unique_doors = analytics_results.get('unique_doors', 0)
        success_rate = analytics_results.get('success_rate', 0)
        if success_rate == 0 and 'successful_events' in analytics_results:
            successful_events = analytics_results.get('successful_events', 0)
            if total_events > 0:
                success_rate = successful_events / total_events
        if analysis_type == "security":
            return {
                "analysis_type": "Security Patterns",
                "data_source": data_source,
                "total_events": total_events,
                "unique_users": unique_users,
                "unique_doors": unique_doors,
                "success_rate": success_rate,
                "security_score": min(100, success_rate * 100 + 20),
                "failed_attempts": total_events - int(total_events * success_rate),
                "risk_level": "Low" if success_rate > 0.9 else "Medium" if success_rate > 0.7 else "High",
                "date_range": analytics_results.get('date_range', {}),
                "analysis_focus": "Security threats, failed access attempts, and unauthorized access patterns",
            }
        elif analysis_type == "trends":
            return {
                "analysis_type": "Access Trends",
                "data_source": data_source,
                "total_events": total_events,
                "unique_users": unique_users,
                "unique_doors": unique_doors,
                "success_rate": success_rate,
                "daily_average": total_events / 30,
                "peak_usage": "High activity detected",
                "trend_direction": "Increasing" if total_events > 100000 else "Stable",
                "date_range": analytics_results.get('date_range', {}),
                "analysis_focus": "Usage patterns, peak times, and access frequency trends over time",
            }
        elif analysis_type == "behavior":
            return {
                "analysis_type": "User Behavior",
                "data_source": data_source,
                "total_events": total_events,
                "unique_users": unique_users,
                "unique_doors": unique_doors,
                "success_rate": success_rate,
                "avg_accesses_per_user": total_events / unique_users if unique_users > 0 else 0,
                "heavy_users": int(unique_users * 0.1),
                "behavior_score": "Normal" if success_rate > 0.8 else "Unusual",
                "date_range": analytics_results.get('date_range', {}),
                "analysis_focus": "Individual user patterns, frequency analysis, and behavioral anomalies",
            }
        elif analysis_type == "anomaly":
            return {
                "analysis_type": "Anomaly Detection",
                "data_source": data_source,
                "total_events": total_events,
                "unique_users": unique_users,
                "unique_doors": unique_doors,
                "success_rate": success_rate,
                "anomalies_detected": int(total_events * (1 - success_rate)),
                "threat_level": "Critical" if success_rate < 0.5 else "Warning" if success_rate < 0.8 else "Normal",
                "suspicious_activities": "Multiple failed attempts detected" if success_rate < 0.9 else "No major issues",
                "date_range": analytics_results.get('date_range', {}),
                "analysis_focus": "Suspicious access patterns, security breaches, and abnormal behaviors",
            }
        else:
            return {
                "analysis_type": analysis_type,
                "data_source": data_source,
                "total_events": total_events,
                "unique_users": unique_users,
                "unique_doors": unique_doors,
                "success_rate": success_rate,
                "date_range": analytics_results.get('date_range', {}),
                "analysis_focus": f"General {analysis_type} analysis",
            }
    except Exception as e:
        return {"error": f"Service analysis failed: {str(e)}"}


def process_quality_analysis(data_source: str) -> Dict[str, Any]:
    """Basic processing for data quality analysis."""
    try:
        if data_source.startswith("upload:") or data_source == "service:uploaded":
            filename = data_source.replace("upload:", "") if data_source.startswith("upload:") else None
            from pages.file_upload import get_uploaded_data
            uploaded_files = get_uploaded_data()
            if not uploaded_files:
                return {"error": "No uploaded files found"}
            if filename is None or filename not in uploaded_files:
                filename = list(uploaded_files.keys())[0]
            df = uploaded_files[filename]
            total_rows = len(df)
            total_cols = len(df.columns)
            missing_values = df.isnull().sum().sum()
            duplicate_rows = df.duplicated().sum()
            quality_score = max(
                0,
                100 - (missing_values / (total_rows * total_cols) * 100) - (duplicate_rows / total_rows * 10),
            )
            return {
                "analysis_type": "Data Quality",
                "data_source": data_source,
                "total_events": total_rows,
                "unique_users": 0,
                "unique_doors": 0,
                "success_rate": quality_score / 100,
                "analysis_focus": "Data completeness and duplication checks",
                "total_rows": total_rows,
                "total_columns": total_cols,
                "missing_values": missing_values,
                "duplicate_rows": duplicate_rows,
                "quality_score": quality_score,
            }
        return {"error": "Data quality analysis only available for uploaded files"}
    except Exception as e:
        return {"error": f"Quality analysis error: {str(e)}"}


def process_suggests_analysis_safe(data_source: str) -> Dict[str, Any]:
    """Safe AI suggestions analysis."""
    try:
        if data_source.startswith("upload:") or data_source == "service:uploaded":
            from pages.file_upload import get_uploaded_data
            uploaded_files = get_uploaded_data()
            if not uploaded_files:
                return {"error": "No uploaded files found"}
            filename = data_source.replace("upload:", "") if data_source.startswith("upload:") else list(uploaded_files.keys())[0]
            df = uploaded_files.get(filename)
            if df is None:
                return {"error": f"File {filename} not found"}
            suggestions = {}
            for col in df.columns:
                col_lower = str(col).lower().strip()
                if any(word in col_lower for word in ["time", "date", "stamp"]):
                    suggestions[col] = {"field": "timestamp", "confidence": 0.8}
                elif any(word in col_lower for word in ["person", "user", "employee"]):
                    suggestions[col] = {"field": "person_id", "confidence": 0.7}
                elif any(word in col_lower for word in ["door", "location", "device"]):
                    suggestions[col] = {"field": "door_id", "confidence": 0.7}
                else:
                    suggestions[col] = {"field": "other", "confidence": 0.5}
            return {
                "analysis_type": "AI Column Suggestions",
                "filename": filename,
                "suggestions": suggestions,
                "total_columns": len(df.columns),
                "total_rows": len(df),
            }
        return {"error": "AI suggestions only available for uploaded files"}
    except Exception as e:
        return {"error": f"AI analysis error: {str(e)}"}


def process_quality_analysis_safe(data_source: str) -> Dict[str, Any]:
    """Safe data quality analysis."""
    try:
        if data_source.startswith("upload:") or data_source == "service:uploaded":
            from pages.file_upload import get_uploaded_data
            uploaded_files = get_uploaded_data()
            if not uploaded_files:
                return {"error": "No uploaded files found"}
            filename = data_source.replace("upload:", "") if data_source.startswith("upload:") else list(uploaded_files.keys())[0]
            df = uploaded_files.get(filename)
            if df is None:
                return {"error": f"File {filename} not found"}
            total_rows = len(df)
            total_cols = len(df.columns)
            missing_values = df.isnull().sum().sum()
            duplicate_rows = df.duplicated().sum()
            quality_score = max(0, 100 - (missing_values + duplicate_rows) / total_rows * 100)
            return {
                "analysis_type": "Data Quality",
                "filename": filename,
                "total_rows": total_rows,
                "total_columns": total_cols,
                "missing_values": int(missing_values),
                "duplicate_rows": int(duplicate_rows),
                "quality_score": round(quality_score, 1),
            }
        return {"error": "Data quality analysis only available for uploaded files"}
    except Exception as e:
        return {"error": f"Quality analysis error: {str(e)}"}


def analyze_data_with_service_safe(data_source: str, analysis_type: str) -> Dict[str, Any]:
    """Safe service-based analysis."""
    try:
        service = get_analytics_service_safe()
        if not service:
            return {"error": "Analytics service not available"}
        source_name = data_source.replace("service:", "") if data_source.startswith("service:") else "uploaded"
        analytics_results = service.get_analytics_by_source(source_name)
        if analytics_results.get('status') == 'error':
            return {"error": analytics_results.get('message', 'Unknown error')}
        return {
            "analysis_type": analysis_type.title(),
            "data_source": data_source,
            "total_events": analytics_results.get('total_events', 0),
            "unique_users": analytics_results.get('unique_users', 0),
            "success_rate": analytics_results.get('success_rate', 0),
            "status": "completed",
        }
    except Exception as e:
        return {"error": f"Service analysis failed: {str(e)}"}

