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
    table = soup.find('table', {'name': 'finging_report'})
    
    if not table:
        raise ValueError("Table 'finging_report' not found")
    
    findings = []
    for row in table.find_all('tr')[1:]:  # Skip header row
        cols = row.find_all('td')
        if len(cols) >= 2:
            finding_name = cols[0].get_text(strip=True)
            try:
                occurrences = int(cols[1].get_text(strip=True))
                findings.append((finding_name, occurrences))
            except ValueError:
                continue
    
    return findings 