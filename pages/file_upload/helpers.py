import logging
import json
from datetime import datetime
from typing import Dict, Any, List

import pandas as pd

from services.device_learning_service import DeviceLearningService
from utils.upload_store import uploaded_data_store as _uploaded_data_store

logger = logging.getLogger(__name__)

# Initialize device learning service
learning_service = DeviceLearningService()


def analyze_device_name_with_ai(device_name):
    """User mappings ALWAYS override AI - FIXED"""
    try:
        from services.ai_mapping_store import ai_mapping_store

        mapping = ai_mapping_store.get(device_name)
        if mapping and mapping.get("source") == "user_confirmed":
            logger.info(
                f"\U0001f512 Using USER CONFIRMED mapping for '{device_name}'"
            )
            return mapping

        logger.info(
            f"\U0001f916 No user mapping found, generating AI analysis for '{device_name}'"
        )

        from services.ai_device_generator import AIDeviceGenerator

        ai_generator = AIDeviceGenerator()
        result = ai_generator.generate_device_attributes(device_name)

        ai_mapping = {
            "floor_number": result.floor_number,
            "security_level": result.security_level,
            "confidence": result.confidence,
            "is_entry": result.is_entry,
            "is_exit": result.is_exit,
            "device_name": result.device_name,
            "ai_reasoning": result.ai_reasoning,
            "source": "ai_generated",
        }

        return ai_mapping

    except Exception as e:
        logger.info(f"\u274c Error in device analysis: {e}")
        return {
            "floor_number": 1,
            "security_level": 5,
            "confidence": 0.1,
            "source": "fallback",
        }


def get_uploaded_data() -> Dict[str, pd.DataFrame]:
    """Get all uploaded data (for use by analytics)."""
    return _uploaded_data_store.get_all_data()


def get_uploaded_filenames() -> List[str]:
    """Get list of uploaded filenames."""
    return _uploaded_data_store.get_filenames()


def clear_uploaded_data():
    """Clear all uploaded data."""
    _uploaded_data_store.clear_all()
    logger.info("Uploaded data cleared")


def get_file_info() -> Dict[str, Dict[str, Any]]:
    """Get information about uploaded files."""
    return _uploaded_data_store.get_file_info()


def save_ai_training_data(filename: str, mappings: Dict[str, str], file_info: Dict):
    """Save confirmed mappings for AI training"""
    try:
        logger.info(f"🤖 Saving AI training data for {filename}")

        training_data = {
            "filename": filename,
            "timestamp": datetime.now().isoformat(),
            "mappings": mappings,
            "reverse_mappings": {v: k for k, v in mappings.items()},
            "column_count": len(file_info.get("columns", [])),
            "ai_suggestions": file_info.get("ai_suggestions", {}),
            "user_verified": True,
        }

        try:
            from plugins.ai_classification.plugin import AIClassificationPlugin
            from plugins.ai_classification.config import get_ai_config

            ai_plugin = AIClassificationPlugin(get_ai_config())
            if ai_plugin.start():
                session_id = (
                    f"verified_{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                ai_mappings = {v: k for k, v in mappings.items()}
                ai_plugin.confirm_column_mapping(ai_mappings, session_id)
                logger.info(f"✅ AI training data saved: {ai_mappings}")
        except Exception as ai_e:
            logger.info(f"⚠️ AI training save failed: {ai_e}")

        import os

        os.makedirs("data/training", exist_ok=True)
        with open(
            f"data/training/mappings_{datetime.now().strftime('%Y%m%d')}.jsonl", "a"
        ) as f:
            f.write(json.dumps(training_data) + "\n")

        logger.info(f"✅ Training data saved locally")

    except Exception as e:
        logger.info(f"❌ Error saving training data: {e}")


__all__ = [
    "analyze_device_name_with_ai",
    "get_uploaded_data",
    "get_uploaded_filenames",
    "clear_uploaded_data",
    "get_file_info",
    "save_ai_training_data",
]
