from film_review_scraper.websites import IMDB
from pathlib import Path

def main():
    config_file = Path(__file__).parent / "data" / "imdb_config.txt"
    page = IMDB(config_file)
    config = page.get_config()
    page_source = page.download_html(page.url)
    # html = page.read_html_file('/Users/pipchang/Documents/VSC/Projects/DH-S/download/imdb_page.html')
    reviews = page.parse(page_source)
    print(reviews[0])

if __name__ == '__main__':
    if False:
        main()