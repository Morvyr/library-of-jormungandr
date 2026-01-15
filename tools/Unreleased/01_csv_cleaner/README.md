# CSV Data Cleaner

**The Library of Jörmungandr Tool #1**

Clean messy CSV files automatically by removing duplicates, handling missing values, cleaning whitespace, and ensuring data consistency.

## Features

- ✅ Remove duplicate rows
- ✅ Remove completely empty rows  
- ✅ Fill missing values with configurable defaults
- ✅ Clean whitespace in text fields
- ✅ Professional logging and error handling
- ✅ Detailed cleaning statistics

## Usage

### Command Line
```bash
python csv_cleaner.py path/to/your/file.csv
```

### As a Module
```python
from csv_cleaner import CSVCleaner

cleaner = CSVCleaner()
result = cleaner.run("data.csv")

if result:
    print(f"Cleaned file: {result['output_file']}")
    print(f"Stats: {result['statistics']}")
```

## Output

Cleaned files are saved to the `output/` directory with a timestamp:
- Original: `sales_data.csv`
- Cleaned: `sales_data_cleaned_20260110_143022.csv`

## Requirements
```bash
pip install -r requirements.txt
```

## Configuration

Edit `core/config.py` to customize:
- `MAX_CSV_SIZE` - Maximum file size to process
- `DEFAULT_MISSING_VALUE` - What to fill missing values with
- `OUTPUT_DIR` - Where to save cleaned files

## Statistics Reported

- Original row count
- Duplicates removed
- Empty rows removed
- Missing values filled
- Final row count

## License

MIT License - Part of the Library of Jörmungandr