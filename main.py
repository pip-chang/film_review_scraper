from film_review_scraper.websites import IMDB
from pathlib import Path

def main():
    config_file = Path(__file__).parent / "data" / "imdb_config.txt"
    page = IMDB(config_file)
    config = page.get_config()
    page_source = page.download_html(page.url)
    reviews = page.parse(page_source)
    output_path = f"/Users/pipchang/Documents/VSC/Projects/DH-S/{config.get('Film')}"
    print(reviews)

if __name__ == '__main__':
    main()