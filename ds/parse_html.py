import json
from bs4 import BeautifulSoup

def parse_html_to_json(html_file, json_file):
    """
    Reads an HTML file containing a table with id 'dataTable',
    extracts the data, and writes it to a JSON file.
    """
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Find the table by its id
    table = soup.find('table', id='dataTable')
    if not table:
        print("Table with id 'dataTable' not found.")
        return

    # Extract headers from thead
    headers = []
    thead = table.find('thead')
    if thead:
        th_elements = thead.find_all('th')
        headers = [th.get_text(strip=True) for th in th_elements]
    else:
        # Fallback: if no thead, use first row as header (unlikely here)
        first_row = table.find('tr')
        if first_row:
            headers = [td.get_text(strip=True) for td in first_row.find_all('td')]

    # Extract data rows from tbody
    data = []
    tbody = table.find('tbody')
    if tbody:
        rows = tbody.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            # Ensure we have the same number of cells as headers
            if len(cells) != len(headers):
                # Pad with empty strings if needed
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                cell_texts += [''] * (len(headers) - len(cells))
            else:
                cell_texts = [cell.get_text(strip=True) for cell in cells]

            row_dict = dict(zip(headers, cell_texts))
            data.append(row_dict)

    # Write to JSON file
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Successfully saved {len(data)} rows to {json_file}")

if __name__ == "__main__":
    # Adjust input/output file names as needed
    input_html = "devops_CreateClientAndSessionSummary.html"
    output_json = "output.json"
    parse_html_to_json(input_html, output_json)