import requests
from bs4 import BeautifulSoup
from parse_text import parse_text

def scrape_links(urls):
    data = []
    for link, title in urls:
        try:
            html = requests.get(link)
            soup = BeautifulSoup(html.text, 'html.parser')
            body = str(soup.body)
            soup = BeautifulSoup(body, 'html.parser')
            for script in soup(["script", "style"]):
                script.extract()

            cleaned_text = soup.get_text(separator='\n')
            cleaned_text = "\n".join(line.strip() for line in cleaned_text.splitlines() if line.strip())
            data.append({"title": title, "data": parse_text(cleaned_text)})
        except Exception as e:
            print(f"Error scraping {link}: {e}")
            data.append({"title": title, "data": ""})

    return data
            