"""
Configuration Settings for the Library of Jörmungandr

Global constants and default settings used across all tools.
Modify these values to change behavior library-wide.
"""

from pathlib import Path

# ============================================================================
# FILE SIZE LIMITS
# ============================================================================

# Maximum file size to process (in bytes)
MAX_FILE_SIZE = 100 * 1024 * 1024 # 100 MB

# Maximum CSV file size (smaller because they load into memory)
MAX_CSV_SIZE = 50 * 1024 * 1024 # 50 MB

# Warn if File is larger than this
WARN_FILE_SIZE = 10 * 1024 * 1024 # 10 MB

# ============================================================================
# NETWORK SETTINGS
# ============================================================================

# Default timeout for HTTP requests (seconds)
DEFAULT_TIMEOUT = 30

# Maximum retries for failed requests
MAX_RETRIES = 3

# Delay between retries (seconds)
RETRY_DELAY = 1

# Default User-Agent for web scraping
DEFAULT_USER_AGENT = "LibraryOfJormungandr/1.0.0 (Python Tool)"

# ============================================================================
# RATE LIMITING
# ============================================================================

# Minimum delay between requests (seconds)
MIN_REQUEST_DELAY = 1.0

# Maximum requests per minute
MAX_REQUESTS_PER_MINUTE = 60


# ============================================================================
# DIRECTORY PATHS
# ============================================================================

# Base directory for all tool operations
BASE_DIR = Path.cwd()

# Output directory for processed files
OUTPUT_DIR = BASE_DIR / "output"

# Temporary files directory
TEMP_DIR = BASE_DIR / "temp"

# Log files directory
LOG_DIR = BASE_DIR / "logs"


# ============================================================================
# ENCODING SETTINGS
# ============================================================================

# Default file encoding
DEFAULT_ENCODING = "utf-8"

# Fallback encodings to try if UTF-8 fails
FALLBACK_ENCODINGS = ["latin-1", "cp1252", "iso-8859-1"]


# ============================================================================
# DATE/TIME FORMATS
# ============================================================================

# Default timestamp format for filenames
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# Human-readable timestamp format
READABLE_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

# Date-only format
DATE_FORMAT = "%Y-%m-%d"


# ============================================================================
# DATA PROCESSING DEFAULTS
# ============================================================================

# Default chunk size for processing large files (rows)
CHUNK_SIZE = 1000

# Maximum number of errors before stopping
MAX_ERRORS = 100

# Default value for missing data
DEFAULT_MISSING_VALUE = ""


# ============================================================================
# VALIDATION SETTINGS
# ============================================================================

# Maximum length for safe filenames
MAX_FILENAME_LENGTH = 255

# Maximum URL length
MAX_URL_LENGTH = 2048

# Valid email maximum length
MAX_EMAIL_LENGTH = 320


# ============================================================================
# LOGGING SETTINGS
# ============================================================================

# Default log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
DEFAULT_LOG_LEVEL = "INFO"

# Log message format
LOG_FORMAT = "[%(name)s] %(levelname)s: %(message)s"
