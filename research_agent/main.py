from scraper import scrape_professor_info
from storage import save_professor_data
from pre_process import pre_process_url

def main():
    with open("C:\\projects\\Summer_Siege\\research_agent\\sample_urls.txt") as f:
        urls = f.read().splitlines()
    i = 1
    for url in urls:
        bsElement = pre_process_url(url)
        data = scrape_professor_info(bsElement)
        if data:
            save_professor_data(data)
            print(f"[{i}] Saved: {data['Name']} ({data['Email']})")
        else:
            print(f"[{i}] Failed to extract from {url}")
        i += 1

if __name__ == "__main__":
    main()
