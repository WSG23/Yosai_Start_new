import io
import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

class FileProcessorService:
    """Simplified, reliable file processor"""

    ALLOWED_EXTENSIONS = {'.csv', '.json', '.xlsx', '.xls'}
    MAX_FILE_SIZE_MB = 50

    def validate_file(self, filename: str, file_size: int) -> dict:
        """Simplified validation"""
        issues = []
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            issues.append(f"Unsupported file type: {file_ext}")
        size_mb = file_size / (1024 * 1024)
        if size_mb > self.MAX_FILE_SIZE_MB:
            issues.append(f"File too large: {size_mb:.1f}MB")
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'size_mb': size_mb,
            'extension': file_ext
        }

    def process_file(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """Simplified file processing"""
        file_ext = Path(filename).suffix.lower()
        try:
            if file_ext == '.csv':
                return self._process_csv_simple(file_content)
            elif file_ext == '.json':
                return self._process_json_simple(file_content)
            elif file_ext in ['.xlsx', '.xls']:
                return self._process_excel_simple(file_content)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            raise ValueError(f"File processing failed: {str(e)}")

    def _process_csv_simple(self, content: bytes) -> pd.DataFrame:
        """Simple CSV processing"""
        try:
            text = content.decode('utf-8-sig')
            return pd.read_csv(io.StringIO(text))
        except UnicodeDecodeError:
            text = content.decode('latin-1')
            return pd.read_csv(io.StringIO(text))

    def _process_json_simple(self, content: bytes) -> pd.DataFrame:
        """Simple JSON processing"""
        text = content.decode('utf-8-sig')
        return pd.read_json(io.StringIO(text))

    def _process_excel_simple(self, content: bytes) -> pd.DataFrame:
        """Simple Excel processing"""
        return pd.read_excel(io.BytesIO(content))
