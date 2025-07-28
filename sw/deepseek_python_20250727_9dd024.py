from bs4 import BeautifulSoup
import json

def parse_similarweb_api_sidebar(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    api_sections = []
    
    # Find all section elements
    sections = soup.find_all('section', class_='rm-Sidebar-section')
    
    for section in sections:
        section_title = section.find('h2', class_='rm-Sidebar-heading')
        if not section_title:
            continue
            
        section_data = {
            'section_title': section_title.get_text(strip=True),
            'endpoints': []
        }
        
        # Find the main list container
        main_list = section.find('ul', class_='rm-Sidebar-list')
        if not main_list:
            api_sections.append(section_data)
            continue
        
        # Find all items in the section
        items = main_list.find_all('li', class_='Sidebar-item23D-2Kd61_k3', recursive=False)
        
        for item in items:
            # Check if it's a parent item (has subpages)
            parent_link = item.find('a', class_='Sidebar-link_parent')
            if parent_link:
                parent_data = {
                    'title': parent_link.find('span', class_='Sidebar-link-text_label1gCT_uPnx7Gu').get_text(strip=True),
                    'method': parent_link.find('span', class_='rm-APIMethod').get_text(strip=True) if parent_link.find('span', class_='rm-APIMethod') else None,
                    'href': parent_link.get('href', ''),
                    'subpages': []
                }
                
                # Find subpages container
                subpages_container = item.find('ul', class_='subpages')
                if subpages_container:
                    subpages = subpages_container.find_all('li', class_='Sidebar-item23D-2Kd61_k3')
                    for subpage in subpages:
                        subpage_link = subpage.find('a')
                        if subpage_link:
                            subpage_data = {
                                'title': subpage_link.find('span', class_='Sidebar-link-text_label1gCT_uPnx7Gu').get_text(strip=True),
                                'method': subpage_link.find('span', class_='rm-APIMethod').get_text(strip=True) if subpage_link.find('span', class_='rm-APIMethod') else None,
                                'href': subpage_link.get('href', '')
                            }
                            parent_data['subpages'].append(subpage_data)
                
                section_data['endpoints'].append(parent_data)
            else:
                # It's a single endpoint without subpages
                link = item.find('a')
                if link:
                    endpoint_data = {
                        'title': link.find('span', class_='Sidebar-link-text_label1gCT_uPnx7Gu').get_text(strip=True),
                        'method': link.find('span', class_='rm-APIMethod').get_text(strip=True) if link.find('span', class_='rm-APIMethod') else None,
                        'href': link.get('href', '')
                    }
                    section_data['endpoints'].append(endpoint_data)
        
        api_sections.append(section_data)
    
    return api_sections

# Load HTML from file
with open('section.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML
parsed_data = parse_similarweb_api_sidebar(html_content)

# Save the parsed data to a JSON file
with open('similarweb_api_endpoints.json', 'w', encoding='utf-8') as outfile:
    json.dump(parsed_data, outfile, indent=2, ensure_ascii=False)

print("Parsing complete. Results saved to similarweb_api_endpoints.json")