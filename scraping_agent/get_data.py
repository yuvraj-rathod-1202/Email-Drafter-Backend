from get_links import get_links
from scrape_links import scrape_links

def get_data(prof_data):

    links = get_links(prof_data['name'], prof_data['curent_institute'])
    print(f"Links found: {len(links)}")

    data = scrape_links(links)  # Limit to first 5 links for performance
    

    return data