# URL Matcher

A Python script for matching Live URLs with Staging URLs for website migration audits.

## Overview

This tool analyzes a CSV file containing Live and Staging URLs, performs matching operations using various strategies, and generates comprehensive reports. It implements a multi-step approach:

1. **Data Preparation**: Cleans and standardizes URLs
2. **Exact Matching**: Identifies identical URLs between Live and Staging
3. **Partial Matching**: Uses multiple algorithms to find similar URLs
4. **Unmatched URL Handling**: Identifies URLs with no matches
5. **Reporting**: Generates detailed reports and statistics

## Features

- Modular, well-documented code structure
- Multiple matching strategies (exact, path-based, sequence, substring)
- Configurable similarity threshold
- Comprehensive logging
- Detailed reporting with CSV and text summary outputs

## Requirements

- Python 3.6+
- Dependencies listed in `requirements.txt`

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/url-matcher.git
cd url-matcher

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python matcher.py path/to/your/csv_file.csv
```

### Advanced Options

```bash
python matcher.py path/to/your/csv_file.csv --output-dir ./custom_output --threshold 0.8 --verbose
```

### Command Line Arguments

- `csv_file`: Path to the CSV file containing URLs (required)
- `--output-dir`, `-o`: Directory to save output files (default: ./output)
- `--threshold`, `-t`: Similarity threshold for partial matching, 0.0 to 1.0 (default: 0.7)
- `--verbose`, `-v`: Enable verbose logging

## Output

The script generates several output files in the specified output directory:

1. `url_matching_results_[timestamp].csv`: Complete results with match types
2. `url_matching_summary_[timestamp].txt`: Text summary with statistics
3. `exact_matches_[timestamp].csv`: List of exact URL matches
4. `partial_matches_[timestamp].csv`: List of partial URL matches with similarity scores
5. `unmatched_live_[timestamp].csv`: Live URLs with no matches
6. `unmatched_staging_[timestamp].csv`: Staging URLs with no matches

## Example

```bash
python matcher.py Holiday_Inn_Migration_Audit_Apr_2025_Compare_Live_Staging_URLs.csv
```

This will process the Holiday Inn Migration Audit CSV file and generate reports in the ./output directory.
