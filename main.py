from film_review_scraper.websites import IMDB, RottenTomatoes, export
from pathlib import Path

def imdb_parse():
    page = IMDB()
    html = page.read_html_file('/Users/pipchang/Documents/VSC/Projects/DH-S/download/imdb_page.html')
    reviews = page.parse(html)
    print(reviews[67])

def rt_parse():
    page = RottenTomatoes()
    html = page.read_html_file('/Users/pipchang/Documents/VSC/Projects/DH-S/download/rt_page.html')
    reviews = page.parse(html)
    print(reviews[55])

def imdb_download():
    page = IMDB()
    source = page.download_html('https://www.imdb.com/title/tt7946836/reviews?sort=submissionDate&dir=asc&ratingFilter=0')
    export.save_html(html_source=source, output_path='/Users/pipchang/Documents/VSC/Projects/DH-S/download', file_name='test')

if __name__ == '__main__':
    imdb_parse()

