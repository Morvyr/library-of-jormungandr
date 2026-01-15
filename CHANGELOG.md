# Changelog

All notable changes to The Library of Jörmungandr will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### In Progress
- **Tool 1: CSV Data Cleaner** After days of debugging, the first production tool is still not ready for deployment. Once work can resume, The core tool csv_repair_tool will be intergrated and further imporvements can commence, until production is acheived.

## [0.005] - 2026-01-15
- **Training Docs and Thread Summaries** - In the /docs folder, added two new folders. in /Thread_Summaries, we added summaries for our Claude training threads to show transparent growth of this porject. In Training_Docs, we have begun the process of creating training documentation for each function in each tool written, for future teaching and reference.
- **New Core tools**
  -`csv_repair_tool.py` - Detects and repairs structural issues in CSV files before processing. This tool identifes field count mismatches and provides interactive repair through user input.
  -`User_input.py` - Functions for human-in-the-loop workflows when automated repair fails or user guidance is needed.
- **CSV Data Cleaner issues** - after testing CSVCleaner.py, found issues with pandas not able to decipher the difference between standard commas and sperator commas. Spent multiple days duebugging first in VS Code, then a Jupyter notebook until deciding to write two new core tools.

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