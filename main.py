from film_review_scraper.websites import IMDB, RottenTomatoes, Douban
from film_review_scraper.data_handeling import save_to_html, save_to_jsonl, get_output_path
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
    save_to_html(html_source=source, output_path='/Users/pipchang/Documents/VSC/Projects/DH-S/download', file_name='test')

def db_download():
    page = Douban()
    review_blocks = page.fetch_reviews(url='https://movie.douban.com/subject/1306476/comments?sort=time&status=P', review_type='short')
    reviews = page.parse_reviews(review_blocks=review_blocks)
    output_path = get_output_path(folder_path='/Users/pipchang/Documents/VSC/Projects/DH-S/download', file_name='db', file_type='jsonl')
    save_to_jsonl(objects=reviews, output_path=output_path)


if __name__ == '__main__':
    db_download()

