# Changelog

All notable changes to The Library of Jörmungandr will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### In Progress
- Tool #3: REST API Client

---

## [0.004] - 2026-01-10

### Added
- **Tool #1: CSV Data Cleaner** - Complete CSV cleaning tool with duplicate removal, missing value handling, whitespace cleaning, and data consistency checks
- **Core Architecture Complete:**
  - `base_tool.py` - Abstract base class for all tools with validation, processing, and logging
  - `utils.py` - Utility functions including file operations, path validation, data validation, string utilities, and bytes_to_human_readable conversion
  - `config.py` - Global configuration settings for file size limits, network settings, rate limiting, directory paths, encoding, date/time formats, data processing defaults, and validation settings
- **Library Structure:** Established tools/##_toolname/ directory pattern for organized tool storage

### Validated
- BaseTool inheritance pattern works correctly
- Utils functions integrate seamlessly with tools
- Config constants provide consistent behavior across tools
- Logging provides professional output
- Error handling prevents crashes and provides useful feedback

### Technical Details
- CSV Cleaner processes test files successfully
- Architecture supports modular, reusable code
- Foundation ready for 99 additional tools

## [0.003] - 2026-01-10

### Infrastructure
- Created master repository: `library-of-jormungandr`
- Established project vision and philosophy
- Defined 100-tool roadmap
- Created base directory structure
- Wrote master README
- Initialized Git repository

---

## [0.002] - 2026-01-09

### Added
- Tool #2: CSV Data Cleaner
  - Removes duplicate rows
  - Standardizes text formatting (Title Case, lowercase)
  - Standardizes date formats (YYYY-MM-DD)
  - Handles missing values intelligently
  - Removes currency symbols from prices
  - Command-line and interactive modes

### Infrastructure
- Created individual repository: `csv-data-cleaner`
- Added to Upwork portfolio
- Published to GitHub
- Announced on X/Twitter

---

## [0.001] - 2026-01-08

### Added
- Tool #1: E-commerce Price Tracker
  - Web scraper using BeautifulSoup
  - Handles pagination automatically
  - Exports to CSV with timestamps
  - Rate limiting and error handling

### Infrastructure
- Created individual repository: `ecommerce-price-tracker`
- Added to Upwork portfolio
- Published to GitHub
- Announced on X/Twitter

---

*The serpent's coils grow with each tool added.*