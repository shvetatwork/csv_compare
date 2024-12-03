from bs4 import BeautifulSoup
import re
from datetime import datetime

def extract_date_from_filename(filename):
    # Extract date from filename (findings_report_YYYY-MM-DD.html)
    match = re.search(r'findings_report_(\d{4}-\d{2}-\d{2})\.html', filename)
    if match:
        return datetime.strptime(match.group(1), '%Y-%m-%d').date()
    raise ValueError("Invalid filename format")

def parse_html_report(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all tables
    tables = soup.find_all('table')
    target_table = None
    
    # Look for the table that has both "finding_name" and "num_of_occurences" in its headers
    for table in tables:
        headers = [header.get_text(strip=True).lower() for header in table.find_all('th')]
        if 'finding_name' in headers and 'num_of_occurences' in headers:
            target_table = table
            finding_name_idx = headers.index('finding_name')
            occurences_idx = headers.index('num_of_occurences')
            break
    
    if not target_table:
        raise ValueError("Could not find table with required columns 'finding_name' and 'num_of_occurences'")
    
    findings = []
    # Skip header row and process data rows
    for row in target_table.find_all('tr')[1:]:
        cols = row.find_all(['td', 'th'])  # Some tables might use th for all cells
        if len(cols) > max(finding_name_idx, occurences_idx):
            finding_name = cols[finding_name_idx].get_text(strip=True)
            try:
                # Remove any non-numeric characters (like commas) and convert to int
                occurences_text = cols[occurences_idx].get_text(strip=True)
                occurences = int(''.join(filter(str.isdigit, occurences_text)))
                findings.append((finding_name, occurences))
            except ValueError:
                continue
    
    return findings 