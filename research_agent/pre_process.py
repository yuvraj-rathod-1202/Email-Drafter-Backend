import requests
from bs4 import BeautifulSoup, Comment

def pre_process_url(url):
    res = requests.get(url=url, timeout=10)
    soup = BeautifulSoup(res.text, 'html.parser')

    tags_to_remove = ['nav', 'footer', 'script', 'style', 'head', 'a']
    for tag_name in tags_to_remove:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    return soup