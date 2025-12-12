#!/usr/bin/env python3
"""
Script for downloading files from URLs found in XLS, XLSX, or CSV files.
Reads all cells in a file and downloads any external file links to a specified folder.
"""

import argparse
import csv
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple
from urllib.parse import urlparse, unquote
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

try:
    import xlrd
    XLRD_AVAILABLE = True
except ImportError:
    XLRD_AVAILABLE = False


# URL pattern to detect external links
URL_PATTERN = re.compile(
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
)


def extract_urls_from_text(text: str) -> List[str]:
    """
    Extract all URLs from a text string.

    Args:
        text: Text to search for URLs

    Returns:
        List of URLs found in the text
    """
    if not isinstance(text, str):
        text = str(text)

    urls = URL_PATTERN.findall(text)
    return urls


def get_filename_from_url(url: str) -> str:
    """
    Extract filename from URL. If no filename found, generate one.

    Args:
        url: The URL to extract filename from

    Returns:
        Filename string
    """
    parsed_url = urlparse(url)
    path = unquote(parsed_url.path)

    # Get the last part of the path
    filename = os.path.basename(path)

    # If no filename or it's a directory, generate from URL
    if not filename or '.' not in filename:
        # Use a hash of the URL to generate a unique filename
        url_hash = str(hash(url))[-8:]
        filename = f"downloaded_file_{url_hash}"

    return filename


def download_file(url: str, output_path: Path) -> bool:
    """
    Download a file from URL to the specified path.

    Args:
        url: URL to download from
        output_path: Path where to save the file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create a request with a user agent to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        request = Request(url, headers=headers)

        # Download the file
        with urlopen(request, timeout=30) as response:
            # Read the file content
            content = response.read()

            # Save to file
            with open(output_path, 'wb') as f:
                f.write(content)

        return True

    except (URLError, HTTPError, TimeoutError) as e:
        print(f"Error downloading {url}: {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error downloading {url}: {str(e)}")
        return False


def read_csv_file(file_path: Path) -> List[str]:
    """
    Read CSV file and extract all URLs from cells.

    Args:
        file_path: Path to CSV file

    Returns:
        List of URLs found in the file
    """
    urls = []

    try:
        with open(file_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                for cell in row:
                    if cell:
                        urls.extend(extract_urls_from_text(cell))
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, 'r', encoding='cp1251', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    for cell in row:
                        if cell:
                            urls.extend(extract_urls_from_text(cell))
        except Exception as e:
            print(f"Error reading CSV file {file_path}: {str(e)}")
    except Exception as e:
        print(f"Error reading CSV file {file_path}: {str(e)}")

    return urls


def read_xlsx_file(file_path: Path) -> List[str]:
    """
    Read XLSX file and extract all URLs from cells.

    Args:
        file_path: Path to XLSX file

    Returns:
        List of URLs found in the file
    """
    if not OPENPYXL_AVAILABLE:
        print("Error: openpyxl library is not installed. Install it with: pip install openpyxl")
        return []

    urls = []

    try:
        workbook = openpyxl.load_workbook(file_path, data_only=True)

        # Iterate through all sheets
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]

            # Iterate through all cells
            for row in sheet.iter_rows():
                for cell in row:
                    if cell.value:
                        # Check if cell has a hyperlink
                        if cell.hyperlink and cell.hyperlink.target:
                            urls.append(cell.hyperlink.target)

                        # Also check cell value for URLs
                        urls.extend(extract_urls_from_text(str(cell.value)))

        workbook.close()
    except Exception as e:
        print(f"Error reading XLSX file {file_path}: {str(e)}")

    return urls


def read_xls_file(file_path: Path) -> List[str]:
    """
    Read XLS file and extract all URLs from cells.

    Args:
        file_path: Path to XLS file

    Returns:
        List of URLs found in the file
    """
    if not XLRD_AVAILABLE:
        print("Error: xlrd library is not installed. Install it with: pip install xlrd")
        return []

    urls = []

    try:
        workbook = xlrd.open_workbook(file_path)

        # Iterate through all sheets
        for sheet_index in range(workbook.nsheets):
            sheet = workbook.sheet_by_index(sheet_index)

            # Iterate through all cells
            for row_index in range(sheet.nrows):
                for col_index in range(sheet.ncols):
                    cell = sheet.cell(row_index, col_index)
                    if cell.value:
                        urls.extend(extract_urls_from_text(str(cell.value)))

        # Also check for hyperlinks
        try:
            for sheet_index in range(workbook.nsheets):
                sheet = workbook.sheet_by_index(sheet_index)
                if hasattr(sheet, 'hyperlink_map'):
                    for link in sheet.hyperlink_map.values():
                        if link.url_or_path:
                            urls.append(link.url_or_path)
        except:
            pass  # Hyperlinks not available in this version

    except Exception as e:
        print(f"Error reading XLS file {file_path}: {str(e)}")

    return urls


def read_file(file_path: Path) -> List[str]:
    """
    Read file and extract URLs based on file extension.

    Args:
        file_path: Path to the file

    Returns:
        List of URLs found in the file
    """
    suffix = file_path.suffix.lower()

    if suffix == '.csv':
        return read_csv_file(file_path)
    elif suffix == '.xlsx':
        return read_xlsx_file(file_path)
    elif suffix == '.xls':
        return read_xls_file(file_path)
    else:
        print(f"Error: Unsupported file format '{suffix}'. Supported formats: .xls, .xlsx, .csv")
        return []


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Download files from URLs found in XLS, XLSX, or CSV files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python download.py data.xlsx /path/to/output
  python download.py data.csv ~/Downloads
  python download.py data.xls ./files
        """
    )

    parser.add_argument(
        "file",
        type=str,
        help="Path to XLS, XLSX, or CSV file containing URLs"
    )

    parser.add_argument(
        "folder",
        type=str,
        help="Path to folder where to download files"
    )

    args = parser.parse_args()

    # Convert paths to Path objects
    file_path = Path(args.file).resolve()
    folder_path = Path(args.folder).resolve()

    # Check if input file exists
    if not file_path.exists():
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)

    if not file_path.is_file():
        print(f"Error: '{file_path}' is not a file.")
        sys.exit(1)

    # Create output folder if it doesn't exist
    folder_path.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {folder_path}")

    # Read file and extract URLs
    print(f"Reading file: {file_path}")
    urls = read_file(file_path)

    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)

    if not unique_urls:
        print("No URLs found in the file.")
        sys.exit(0)

    print(f"Found {len(unique_urls)} unique URL(s) in the file")

    # Download each file
    successful = 0
    failed = 0
    skipped = 0

    for i, url in enumerate(unique_urls, 1):
        print(f"\n[{i}/{len(unique_urls)}] Processing: {url}")

        # Get filename from URL
        filename = get_filename_from_url(url)
        output_path = folder_path / filename

        # Check if file already exists
        if output_path.exists():
            print(f"Skipped (already exists): {filename}")
            skipped += 1
            continue

        # Download the file
        if download_file(url, output_path):
            print(f"Downloaded: {filename}")
            successful += 1
        else:
            failed += 1

    # Print summary
    print("\n" + "=" * 50)
    print("Download complete!")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print(f"Total URLs: {len(unique_urls)}")
    print("=" * 50)


if __name__ == "__main__":
    main()
