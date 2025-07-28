from bs4 import BeautifulSoup

def parse_api_endpoints(html_content):
    """Parse the HTML content to extract API endpoint information."""
    soup = BeautifulSoup(html_content, 'html.parser')
    endpoints = []
    
    # Find all list items containing endpoints
    items = soup.find_all('li', class_='Sidebar-item23D-2Kd61_k3')
    
    for item in items:
        link = item.find('a')
        if link:
            endpoint = {
                'title': link.find('span', class_='Sidebar-link-text_label1gCT_uPnx7Gu').get_text(strip=True),
                'method': link.find('span', class_='rm-APIMethod').get_text(strip=True),
                'href': link.get('href', ''),
                'target': link.get('target', ''),
                'active': 'active' in link.get('class', [])
            }
            endpoints.append(endpoint)
    
    return endpoints

# Example usage
html_content = """
<li class="Sidebar-item23D-2Kd61_k3 subnav-expanded"><a class="Sidebar-link2Dsha-r-GKh2 Sidebar-link_parent text-wrap rm-Sidebar-link" target="_self" href="/reference/visits-desktop"><span class="Sidebar-link-textLuTE1ySm4Kqn"><span class="Sidebar-link-text_label1gCT_uPnx7Gu">Traffic &amp; Engagement - Desktop</span></span><button aria-expanded="true" aria-label="Hide subpages for Traffic &amp; Engagement - Desktop" class="Sidebar-link-buttonWrapper3hnFHNku8_BJ" type="button"><i aria-hidden="true" class="Sidebar-link-iconnjiqEiZlPn0W Sidebar-link-expandIcon2yVH6SarI6NW icon-chevron-rightward"></i></button></a><ul class="subpages Sidebar-list3cZWQLaBf9k8 rm-Sidebar-list"><li class="Sidebar-item23D-2Kd61_k3"><a class="Sidebar-link2Dsha-r-GKh2 childless subpage text-wrap rm-Sidebar-link" target="_self" href="/reference/visits-desktop"><span class="Sidebar-link-textLuTE1ySm4Kqn"><span class="Sidebar-link-text_label1gCT_uPnx7Gu">Visits - Desktop</span></span><span class="Sidebar-method-container2yBYD-KB_IfC"><span class="rm-APIMethod APIMethod APIMethod_fixedWidth APIMethod_get Sidebar-methodfUM3m6FEWm6w" data-testid="http-method">get</span></span><div class="Sidebar-link-buttonWrapper3hnFHNku8_BJ"></div></a></li><li class="Sidebar-item23D-2Kd61_k3"><a class="Sidebar-link2Dsha-r-GKh2 childless subpage text-wrap rm-Sidebar-link" target="_self" href="/reference/pages-per-visit-desktop"><span class="Sidebar-link-textLuTE1ySm4Kqn"><span class="Sidebar-link-text_label1gCT_uPnx7Gu">Pages Per Visit - Desktop</span></span><span class="Sidebar-method-container2yBYD-KB_IfC"><span class="rm-APIMethod APIMethod APIMethod_fixedWidth APIMethod_get Sidebar-methodfUM3m6FEWm6w" data-testid="http-method">get</span></span><div class="Sidebar-link-buttonWrapper3hnFHNku8_BJ"></div></a></li><li class="Sidebar-item23D-2Kd61_k3"><a class="Sidebar-link2Dsha-r-GKh2 childless subpage text-wrap rm-Sidebar-link" target="_self" href="/reference/average-visit-duration"><span class="Sidebar-link-textLuTE1ySm4Kqn"><span class="Sidebar-link-text_label1gCT_uPnx7Gu">Average Visit Duration - Desktop</span></span><span class="Sidebar-method-container2yBYD-KB_IfC"><span class="rm-APIMethod APIMethod APIMethod_fixedWidth APIMethod_get Sidebar-methodfUM3m6FEWm6w" data-testid="http-method">get</span></span><div class="Sidebar-link-buttonWrapper3hnFHNku8_BJ"></div></a></li><li class="Sidebar-item23D-2Kd61_k3"><a class="Sidebar-link2Dsha-r-GKh2 childless subpage text-wrap rm-Sidebar-link" target="_self" href="/reference/bounce-rate-desktop"><span class="Sidebar-link-textLuTE1ySm4Kqn"><span class="Sidebar-link-text_label1gCT_uPnx7Gu">Bounce Rate - Desktop</span></span><span class="Sidebar-method-container2yBYD-KB_IfC"><span class="rm-APIMethod APIMethod APIMethod_fixedWidth APIMethod_get Sidebar-methodfUM3m6FEWm6w" data-testid="http-method">get</span></span><div class="Sidebar-link-buttonWrapper3hnFHNku8_BJ"></div></a></li><li class="Sidebar-item23D-2Kd61_k3"><a class="Sidebar-link2Dsha-r-GKh2 childless subpage text-wrap rm-Sidebar-link" target="_self" href="/reference/pageviews"><span class="Sidebar-link-textLuTE1ySm4Kqn"><span class="Sidebar-link-text_label1gCT_uPnx7Gu">Pageviews - Desktop</span></span><span class="Sidebar-method-container2yBYD-KB_IfC"><span class="rm-APIMethod APIMethod APIMethod_fixedWidth APIMethod_get Sidebar-methodfUM3m6FEWm6w" data-testid="http-method">get</span></span><div class="Sidebar-link-buttonWrapper3hnFHNku8_BJ"></div></a></li><li class="Sidebar-item23D-2Kd61_k3"><a class="Sidebar-link2Dsha-r-GKh2 childless subpage text-wrap rm-Sidebar-link" target="_self" href="/reference/unique-visitors"><span class="Sidebar-link-textLuTE1ySm4Kqn"><span class="Sidebar-link-text_label1gCT_uPnx7Gu">Unique Visitors - Desktop</span></span><span class="Sidebar-method-container2yBYD-KB_IfC"><span class="rm-APIMethod APIMethod APIMethod_fixedWidth APIMethod_get Sidebar-methodfUM3m6FEWm6w" data-testid="http-method">get</span></span><div class="Sidebar-link-buttonWrapper3hnFHNku8_BJ"></div></a></li><li class="Sidebar-item23D-2Kd61_k3"><a class="Sidebar-link2Dsha-r-GKh2 childless subpage text-wrap rm-Sidebar-link" target="_self" href="/reference/geography"><span class="Sidebar-link-textLuTE1ySm4Kqn"><span class="Sidebar-link-text_label1gCT_uPnx7Gu">Geography - Desktop</span></span><span class="Sidebar-method-container2yBYD-KB_IfC"><span class="rm-APIMethod APIMethod APIMethod_fixedWidth APIMethod_get Sidebar-methodfUM3m6FEWm6w" data-testid="http-method">get</span></span><div class="Sidebar-link-buttonWrapper3hnFHNku8_BJ"></div></a></li></ul></li>
"""

endpoints = parse_api_endpoints(html_content)

# Print the results
for endpoint in endpoints:
    print(f"{endpoint['method']:5} {endpoint['title']:60} {endpoint['href']}")
