#!/usr/bin/env python3
"""
Extract specific divs with IDs #2 and #3 from PyCon India 2025 schedule HTML file.
"""

from bs4 import BeautifulSoup
import sys
from pathlib import Path


def extract_divs_by_ids(html_file_path: str, target_ids: list[str]) -> dict[str, str]:
    """
    Extract divs with specific IDs from an HTML file.
    
    Args:
        html_file_path: Path to the HTML file
        target_ids: List of div IDs to extract (without the # symbol)
    
    Returns:
        Dictionary mapping ID to the HTML content of the div
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'lxml')
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        with open(html_file_path, 'r', encoding='iso-8859-1') as file:
            soup = BeautifulSoup(file, 'lxml')
    
    extracted_divs = {}
    
    for div_id in target_ids:
        div_element = soup.find('div', id=div_id)
        if div_element:
            extracted_divs[div_id] = str(div_element)
            print(f"[+] Found div with ID '{div_id}'")
        else:
            print(f"[-] Could not find div with ID '{div_id}'")
            extracted_divs[div_id] = None
    
    return extracted_divs


def save_extracted_divs(extracted_divs: dict[str, str], output_dir: str = "extracted_divs"):
    """
    Save extracted divs to separate HTML files.
    
    Args:
        extracted_divs: Dictionary of extracted div content
        output_dir: Directory to save the files
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for div_id, content in extracted_divs.items():
        if content:
            file_path = output_path / f"div_{div_id}.html"
            with open(file_path, 'w', encoding='utf-8') as file:
                # Create a complete HTML document
                html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Extracted Div ID: {div_id}</title>
</head>
<body>
{content}
</body>
</html>"""
                file.write(html_doc)
            print(f"[+] Saved div #{div_id} to {file_path}")


def main():
    # HTML file path
    html_file = "Schedule _ 12th - 15th September.htm"
    
    # Check if file exists
    if not Path(html_file).exists():
        print(f"Error: HTML file '{html_file}' not found!")
        sys.exit(1)
    
    # Target div IDs to extract
    target_ids = ["2", "3"]
    
    print(f"Extracting divs with IDs: {target_ids}")
    print(f"From file: {html_file}")
    print("-" * 50)
    
    # Extract the divs
    extracted_divs = extract_divs_by_ids(html_file, target_ids)
    
    # Save to files
    save_extracted_divs(extracted_divs)
    
    print("-" * 50)
    print("Extraction complete!")
    
    # Print summary
    found_count = sum(1 for content in extracted_divs.values() if content is not None)
    print(f"Found {found_count} out of {len(target_ids)} requested divs")


if __name__ == "__main__":
    main()