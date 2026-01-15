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
            df = pd.read_csv(filepath, encoding=DEFAULT_ENCODING, dtype=str, keep_default_na=False)

            # Convert empty strings to NaN for proper handling
            df = df.replace('', pd.NA)

            self.stats["original_rows"] = len(df)
            self.logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")

            # Clean the data
            df = self._remove_duplicates(df)
            df = self._remove_empty_rows(df)
            df = self._clean_prices(df)
            df = self._standardize_dates(df)
            df = self._handle_missing_values(df)
            df = self._standardize_text(df)
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
    
    def _standardize_text(self, df):
        """
        Standardize text formatting across common column types.
        - Names: Title Case
        - Emails: lowercase
        - Status fields: Title Case
        """ 

        changes_made = 0

        # Find columns that look like names (contain 'name' in column name)
        name_columns = [col for col in df.columns if 'name' in col.lower()]
        for col in name_columns:
            if df[col].dtype == 'object': 
                # Apply title case, leaving NaN unchanged
                df[col] = df[col].apply(lambda x: x.title() if pd.notna(x) else x)
                changes_made += 1
        
        # Find columns that look like emails
        email_columns = [col for col in df.columns if 'email' in col.lower()]
        for col in email_columns:
            if df[col].dtype == 'object':
               # Apply title case, leaving NaN unchanged
                df[col] = df[col].apply(lambda x: x.lower() if pd.notna(x) else x)
                changes_made += 1

        # Find columns that look like status fields
        status_columns = [col for col in df.columns if 'status' in col.lower()]
        for col in status_columns:
            if df[col].dtype == 'object':
                # Apply title case, leaving NaN unchanged
                df[col] = df[col].apply(lambda x: x.title() if pd.notna(x) else x)
                changes_made += 1

        if changes_made > 0:
            column_word = "column" if changes_made == 1 else "columns"
            self.logger.info(f"Standardized text in {changes_made} {column_word}")

        return df

    def _standardize_dates(self, df):
        """
        Standardize date formats to YYYY-MM-DD.
        Handles multiple input formats automatically.
        """

        # Find columns that look like dates
        date_columns = [col for col in df.columns if any(
            keyword in col.lower() for keyword in ['date', 'time', 'day']
        )]

        changes_made = 0

        for col in date_columns:
            try:
                # Convert to datetime (handles both text and datetime input)
                df[col] = pd.to_datetime(df[col], errors='coerce')
                # Format as string
                df[col] = df[col].dt.strftime('%Y-%m-%d')
                # Replace NaT with empty string
                df[col] = df[col].fillna('')
                changes_made += 1
            except Exception:
                continue
        
        if changes_made > 0:
            column_word = "column" if changes_made == 1 else "columns"
            self.logger.info(f"Standardized dates in {changes_made} {column_word}")

        return df
    
    def _clean_prices(self, df):
        """
        Clean price/currency columns by removing symbols and converting to numbers.
        Handles: $, €, £, ¥, and commas
        """

        # Find columns that look like prices
        price_columns = [col for col in df.columns if any(
            keyword in col.lower() for keyword in ['price', 'cost', 'amount', 'total', 'fee']
        )]

        changes_made = 0

        for col in price_columns:
            # Convert to string
            df[col] = df[col].astype(str)

            # Remove currency symbols and commas
            df[col] = df[col].str.replace('$', '', regex=False)
            df[col] = df[col].str.replace('€', '', regex=False)
            df[col] = df[col].str.replace('£', '', regex=False)
            df[col] = df[col].str.replace('¥', '', regex=False)
            df[col] = df[col].str.replace(',', '', regex=False)

            # Convert to numeric
            df[col] = pd.to_numeric(df[col], errors='coerce')
            changes_made += 1

        if changes_made > 0:
            column_word = "column" if changes_made == 1 else "columns"
            self.logger.info(f"Cleaned prices in {changes_made} {column_word}")

        return df
    
    def _handle_missing_values(self, df):
        """Fill missing values with intelligent defaults based on column type and name."""
        
        missing_count = df.isna().sum().sum()

        if missing_count == 0:
            return df
        
        filled = 0

        # Smart defaults for common column types
        for col in df.columns:
            if df[col].isna().sum() == 0:
                continue # Skip columns with no missing values

            col_lower = col.lower()

            # Products get 'Unknown Product'
            if 'product' in col_lower:
                missing_in_col = df[col].isna().sum()
                df[col] = df[col].fillna('Unknown Product')
                filled += missing_in_col

            # Names get 'Unknown'
            elif 'name' in col_lower:
                missing_in_col = df[col].isna().sum()
                df[col] = df[col].fillna('Unknown')
                filled += missing_in_col

            # Emails get placeholder
            elif 'email' in col_lower:
                missing_in_col = df[col].isna().sum()
                df[col] = df[col].fillna('no-email@provided.com')
                filled += missing_in_col

            # Status gets 'Pending'
            elif 'status' in col_lower:
                missing_in_col = df[col].isna().sum()
                df[col] = df[col].fillna('Pending')
                filled += missing_in_col

            # Quantities/counts get 1
            elif 'quantity' in col_lower or 'count' in col_lower:
                missing_in_col = df[col].isna().sum()
                df[col] = df[col].fillna(1)
                filled += missing_in_col

            # Prices/amounts get 0.00
            elif any(word in col_lower for word in ['price', 'cost', 'amount', 'total', 'fee']):
                missing_in_col = df[col].isna().sum()
                df[col] = df[col].fillna(0.00)
                filled += missing_in_col

            # Everything else gets empty string
            else:
                missing_in_col = df[col].isna().sum()
                df[col] = df[col].fillna(DEFAULT_MISSING_VALUE)
                filled += missing_in_col
                    
        self.stats["missing_values_filled"] = missing_count

        if filled > 0:
            value_word = "value" if filled == 1 else "values"
            self.logger.info(f"Filled {filled} missing {value_word} with intelligent defaults.")

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


    
    
    


        




