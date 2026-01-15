"""
CSV Structure Repair Tool for the Library of Jörmungandr

Detects and repairs structural issues in CSV files before processing.
This tool identifes field count mismatches and provides interactive 
repair through user input.

This is a CORE tool - other tools can use it to ensure CSV files
are structurally valid before attempting to process them.
"""

from pathlib import Path
from typing import Optional, List, Tuple

# Import from other core modules
from base_tool import BaseTool
from config import DEFAULT_ENCODING, MAX_CSV_SIZE
from utils import check_file_exists, get_file_size, bytes_to_human_readable
from user_input import edit_line_interactive, confirm_action

class CSVRepairTool(BaseTool):
    """
    Repairs structural issues in CSV files.

    Detects field count mismatches and provides interactive
    repair through user guidance.

    Method Flow:
    1. __init__() - Initialize tool and stats tracking
    2. validate_input() - Verify file exists and is valid CSV
    3. process() - Main repair workflow (read → detect → repair → return)
    4. _has_unbalanced_quotes() - Check if line has paired quotes
    5. _count_fields_respecting_quotes() - Count fields respecting CSV quoting rules
    6. _detect_field_mismatches() - Find all lines with structural issues
    7. _interactive_repair() - User-guided line-by-line repair
    """
    
    def __init__(self):
        """ Initialize the CSV Repair Tool."""
        super().__init__(name="CSV Repair Tool", version="1.0.0")
        self.repairs_made = 0

    def validate_input(self, filepath):
        """   
        Validate the input CSV file.

        Checks:
        - File exists
        -File has .csv extension
        -File size is within limits
        
        Args:
            filepath: Path to the Csv file

        Returns:
            bool: True if valid, False otherwise
        """

        # Check if filepath provided
        if not filepath:
            self.logger.error("No filepath provided")
            return False
        
        # Convert to Path object
        filepath = Path(filepath)

        # Check if file exists
        if not check_file_exists(filepath):
            self.logger.error(f"File not found: {filepath}")
            return False
        
        # Check if CSV file
        if filepath.suffix.lower() != '.csv':
            self.logger.error(f"File must be a CSV file, got: {filepath.suffix}")
            return False
        
        # Check file size
        size = get_file_size(filepath)
        if size is None:
            self.logger.error("Could not determine file size")
            return False
        
        if size > MAX_CSV_SIZE:
            self.logger.error(f"File too large: {bytes_to_human_readable(size)} (max: {bytes_to_human_readable(MAX_CSV_SIZE)})")
            return False
        
        self.logger.info(f"Input file validated: {filepath} ({bytes_to_human_readable(size)})")
        return True

    def process(self, filepath):
        """   
        Repair CSV structure issues before pandas parsing.

        Two-layer detection approach:
        1. Detect field count mismatches using quote aware counting
        2. Interactive user repair for issues found

        Args:
            filepath: Path to the CSV file

        Returns:
            str: Repaired CSV content as string, ready for pandas
                 Returns None if file is empty or user cancels
        """

        filepath = Path(filepath)

        self.logger.info("Starting CSV structure repair...")

        # Read the raw CSV content
        with open(filepath, 'r', encoding=DEFAULT_ENCODING) as f:
            lines = f.readlines()

        if not lines:
            self.logger.error("CSV file is empty")
            return None
        
        # Detect issues using two-layer detection
        self.logger.info("Detecting field mismatches...")
        issues = self._detect_field_mismatches(lines)

        # Interactive repair if issues found
        if issues:
            self.logger.info(f"Found {len(issues)} lines needing repair")
            lines = self._interactive_repair(lines, issues)

            if lines is None:
                self.logger.error("User cancelled repair process")
                return None
            
            self.repairs_made = len(issues)
        
        else:
            self.logger.info("No field mismatches detected! CSV structure looks good. Lucky you!")

        # Join lines back into single string
        repaired_content = ''.join(lines)

        self.logger.info("CSV structure repair complete")
        return repaired_content



    def _has_unbalanced_quotes(self, line):
        """   
        Check if a line has unbalanced quotes (odd number).

        Args:
            line: CSV line to check

        Returns:
            bool: True if unbalanced (odd count), False if balanced (even count)
        """

        quote_count = line.count('"')
        return quote_count % 2 != 0 # Odd = unbalanced
    
    def _count_fields_respecting_quotes(self, line):
        """
        Count fields in a CSV line, respecting quoted sections.

        Commas inside quotes don't count as delimiters.

        Args:
            line: CSV line to analyze

        Returns:
            int: Number of fields in the line
        """
        inside_quotes = False
        field_count = 1 # Start with 1 field

        for char in line:
            if char == '"':
                inside_quotes = not inside_quotes # Toggle state
            
            elif char == ',' and not inside_quotes:
                field_count += 1 # Count comma only outside quotes

        return field_count
    
    
    def _detect_field_mismatches(self, lines):
        """
        Detect lines with structural issues using two-layer detection.

        Layer 1: Check for unbalanced quotes
        Layer 2: Check for field count mismatches (quote-aware)

        Args:
            lines: List of CSV lines (including header)

        Returns:
            List of tuples: (line_number, line_content, issue_type)
        """
        if len(lines) < 2:
            return []

        # Get expected field count from header
        header = lines[0]
        expected_fields = self._count_fields_respecting_quotes(header)
        
        self.logger.info(f"Header has {expected_fields} fields")

        issues = []

        # Check each data line
        for i, line in enumerate(lines[1:], start=2): #Start at line 2
            # Skip empty lines
            if not line.strip():
                continue

            # Layer 1: Check quote balance
            if self._has_unbalanced_quotes(line):
                issues.append((i, line.strip(), "Unbalanced quotes"))
                continue # Skip field count check if quotes are broken

            # Layer 2: Check field count
            field_count = self._count_fields_respecting_quotes(line)
            if field_count != expected_fields:
                issues.append((i, line.strip(), f"Has {field_count} fields, expected {expected_fields}"))

        return issues

    def _interactive_repair(self, lines, issues):
        """
        Guide user through fixing problematic lines interactively.

        Args:
            lines: List of all CSV lines
            issues: List of tuples(line_number, line_content, issue_description)

        Returns:
            Modified lines list, or None if user cancels
        """
        print("\n" + "=" * 60)
        print(f"INTERACTIVE REPAIR MODE")
        print(f"Found {len(issues)} lines with structural issues")
        print("=" * 60)

        for line_num, line_content, issue_desc in issues:
            print(f"\nLine {line_num}: {issue_desc}")
            print(f"Content: {line_content}")

            # Ask user if they want to fix this line
            should_fix = confirm_action(
                f"Do you want to fix line {line_num}?",
                default=True
            )

            if not should_fix:
                self.logger.info(f"Skipping line {line_num}")
                continue

            # Let user edit the line
            fixed_line = edit_line_interactive(line_content, line_num)

            if fixed_line is None:
                # User cancelled - ask if they want to abort entire repair
                abort = confirm_action(
                    "Cancel entire repair process?",
                    default=False
                )
                if abort:
                    return None
                else:
                    continue

            # Update the line (add newline back)
            lines[line_num - 1] = fixed_line + '\n'
            self.logger.info(f"Repaired line {line_num}")

        return lines

    """def _repair_csv_structure(self, filepath):
        
        Repair CSV structure issues before pandas parsing.

        Two-layer approach:
        1. Detect field count mismatches.
        2. Interactive user repair for issues found.

        Args:
            filepath: Path to the CSV file

        Returns:
            str: Repaired CSV content as string, ready for pandas
        
        filepath = Path(filepath)

        self.logger.info("Starting CSV structure repair...")

        #Read the raw CSV content
        with open(filepath, 'r', encoding=DEFAULT_ENCODING) as f:
            lines=f.readlines()

        if not lines:
            self.logger.error("CSV file is empty")
            return None

        # Layer 1: Detect issues
        self.logger.info("Detecting field mismatches...")
        issues = self._detect_field_mismatches(lines)

        # Layer 2: Interactive repair if issues found
        if issues:
            self.logger.info(f"Found {len(issues)} lines needing repair")
            lines = self._interactive_repair(lines,issues)

            if lines is None:
                self.logger.error("User cancelled repair process")
                return None

        else:
            self.logger.info("No field mismatches detected! CSV structure looks good. Lucky you!")

        # Join lines back into single string
        repaired_content = ''.join(lines)

        self.logger.info("CSV structure repair complete")
        return repaired_content
    """



    