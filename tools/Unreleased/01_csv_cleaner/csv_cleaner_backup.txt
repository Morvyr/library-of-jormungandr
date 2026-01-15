"""
The Library of Jörmungandr Tool #1

CSV Data Cleaner

Clean messy CSV files by removing duplicates, handling missing values,
cleaning whitespace, and ensuring data consistency.
"""

import sys
from pathlib import Path
from datetime import datetime

#Add parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))

from base_tool import BaseTool
from utils import check_file_exists, get_file_size, create_directory, clean_string, bytes_to_human_readable
from config import MAX_CSV_SIZE, DEFAULT_ENCODING, OUTPUT_DIR, DEFAULT_MISSING_VALUE

import pandas as pd

class CSVCleaner(BaseTool):
    """
    Tool for cleaning messy CSV files.

    Removes duplicates, handles missing values, cleans whitespace,
    and ensures data consistency.
    """

    def __init__(self):
        super().__init__(name="CSV Cleaner", version="1.0.0")
        self.stats = {
            "original_rows": 0,
            "duplicates_removed": 0,
            "empty_rows_removed": 0,
            "missing_values_filled": 0,
            "final_rows": 0
        }

    def validate_input(self, filepath):
        """
        Validate the input CSV file.

        Checks:
        -File exists
        -File has .csv extension
        -File size is within limits
        
        Args:
            filepath: Path to the CSV file
        
        Returns:
            bool: True if valid, False otherwise
        """

        # Check if filepath provided
        if not filepath:
            self.logger.error("NO filepath provided")
            return False
        
        # Convert to Path Object
        filepath = Path(filepath)

        # Check if file exists (using utils.py)
        if not check_file_exists(filepath):
            self.logger.error(f"File not found: {filepath}")
            return False
        
        # Check if CSV file
        if filepath.suffix.lower() != '.csv':
            self.logger.error(f"File must be a CSV file, got: {filepath.suffix}")
            return False
        
        # Check file size (usuing utils.py and config.py)
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
        Clean the CSV file. 

        Args:
            filepath: Path to the CSV file

        Returns:
            dict: Results including output path and cleaning statistics
        """
        filepath = Path(filepath)

        try:
            # Read CSV file
            self.logger.info(f"Reading CSV file with encoding: {DEFAULT_ENCODING}")
            df = pd.read_csv(filepath, encoding=DEFAULT_ENCODING)

            self.stats["original_rows"] = len(df)
            self.logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")

            # Clean the data
            df = self._remove_duplicates(df)
            df = self._remove_empty_rows(df)
            df = self._handle_missing_values(df)
            df = self._clean_text_fields(df)

            self.stats["final_rows"] = len(df)

            # Save cleaned file
            output_path = self._save_cleaned_file(df, filepath)

            # Log summary
            self._log_summary()

            return {
                "success": True,
                "input_file": str(filepath),
                "output_file": str(output_path),
                "statistics": self.stats.copy()
            }
        
        except pd.errors.EmptyDataError:
            self.logger.error("CSV file is empty")
            return None
        except pd.errors.ParserError as e:
            self.logger.error(f"Error parsing CSV: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return None
        
    def _remove_duplicates(self, df):
        """Remove duplicate rows from the Dataframe."""
        before = len(df)
        df = df.drop_duplicates()
        after = len(df)

        removed = before - after
        self.stats["duplicates_removed"] = removed

        if removed > 0:
            row_word = "row" if removed == 1 else "rows"
            self.logger.info(f"Removed {removed} duplicate {row_word}")
            
        return df
        
    def _remove_empty_rows(self, df):
        """Remove completely empty rows."""
        before = len(df)
        df = df.dropna(how='all')
        after = len(df)

        removed = before - after
        self.stats["empty_rows_removed"] = removed

        if removed > 0:
            row_word = "row" if removed == 1 else "rows"
            self.logger.info(f"Removed {removed} empty {row_word}")

        return df
    
    def _handle_missing_values(self, df):
        """Fill missing values with default value from config."""
        missing_count = df.isna().sum().sum()

        if missing_count > 0:
            df = df.fillna(DEFAULT_MISSING_VALUE)
            self.stats["missing_values_filled"] = missing_count
            value_word = "value" if missing_count == 1 else "values"
            self.logger.info(f"Filled {missing_count} missing {value_word} with '{DEFAULT_MISSING_VALUE}'")

        return df
    
    def _clean_text_fields(self, df):
        """Clean whitespace in text fields using utils.clean_string()."""
        cleaned_count = 0

        # Find text columns
        text_columns = df.select_dtypes(include=['object']).columns

        # Clean each text column
        for column in text_columns:
            # Apply clean_string to each value in the column
            df[column] = df[column].apply(
                lambda x: clean_string(str(x)) if pd.notna(x) else x
            )
            cleaned_count += 1
        
        if cleaned_count > 0:
            column_word = "column" if cleaned_count == 1 else "columns"
            self.logger.info(f"Cleaned whitespace in {cleaned_count} text {column_word}")

        return df
    
    def _save_cleaned_file(self, df, original_filepath):
        """Save the cleaned dataframe to a new CSV file."""
        
        # Ensure output directory exists (using utils.py and config.py)
        create_directory(OUTPUT_DIR)

        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{original_filepath.stem}_cleaned_{timestamp}.csv"
        output_path = OUTPUT_DIR / output_filename

        # Save to CSV
        df.to_csv(output_path, index=False, encoding=DEFAULT_ENCODING)

        self.logger.info(f"Saved cleaned file to: {output_path}")

        return output_path

    def _log_summary(self):
        """Log a summary of cleaning operations."""
        self.logger.info("=" * 50)
        self.logger.info("CLEANING SUMMARY")
        self.logger.info(f"Original rows: {self.stats['original_rows']}")
        self.logger.info(f"Duplicates removed: {self.stats['duplicates_removed']}")
        self.logger.info(f"Empty rows removed: {self.stats['empty_rows_removed']}")
        self.logger.info(f"Missing values filled: {self.stats['missing_values_filled']}") 
        self.logger.info(f"Final rows: {self.stats['final_rows']}")
        self.logger.info(f"Rows removed: {self.stats['original_rows'] - self.stats['final_rows']}")
        self.logger.info("=" * 50)

# Command-line interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python csv_cleaner.py <path_to_csv_file>")
        sys.exit(1)

    # Get filepath from command line
    filepath = sys.argv[1]

    # Create and run the tool
    cleaner = CSVCleaner()
    result = cleaner.run(filepath)

    if result:
        print(f"\n✓ Success! Cleaned file saved to: {result['output_file']}")
    else:
        print("\n✗ Cleaning failed. Check logs above for details.")
        sys.exit(1)


    
    
    


        




