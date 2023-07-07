from ast import parse
from film_review_scraper.websites import IMDB, RottenTomatoes, Douban
from film_review_scraper.data_handling import get_output_path, save_dataclass_to_jsonl
from film_review_scraper.data_processing import FilmData, ReviewData

def imdb_download():
    page = IMDB()
    review_blocks = page.fetch_reviews(
        url="https://www.imdb.com/title/tt22058628/reviews?sort=curated&dir=desc&ratingFilter=0"
    )
    reviews = page.parse_reviews(review_blocks)
    output_path = get_output_path(
        folder_path="/Users/pipchang/Documents/VSC/Projects/DH-S/download",
        file_name="imdb_Born_To_Fly_popular",
        file_type="jsonl",
    )
    save_dataclass_to_jsonl(objects=reviews, output_path=output_path)


def rt_download():
    page = RottenTomatoes()
    review_blocks = page.fetch_reviews(
        url="https://www.rottentomatoes.com/m/born_to_fly_2023/reviews?type=user"
    )
    reviews = page.parse_reviews(review_blocks)
    output_path = get_output_path(
        folder_path="/Users/pipchang/Documents/VSC/Projects/DH-S/download",
        file_name="rt_Born_To_Fly_audience",
        file_type="jsonl",
    )
    save_dataclass_to_jsonl(objects=reviews, output_path=output_path)


def db_download_short():
    page = Douban()
    review_blocks = page.fetch_reviews(
        url="https://movie.douban.com/subject/35209731/comments?sort=time&status=P",
        review_type="short",
    )
    reviews = page.parse_reviews(review_blocks=review_blocks, parse_type="short")
    output_path = get_output_path(
        folder_path="/Users/pipchang/Documents/VSC/Projects/DH-S/download",
        file_name="db_Born_To_Fly_short_timed",
        file_type="jsonl",
    )
    save_dataclass_to_jsonl(objects=reviews, output_path=output_path)


def db_download_long():
    page = Douban()
    review_blocks = page.fetch_reviews(
        url="https://movie.douban.com/subject/35209731/reviews",
        review_type="long",
    )
    reviews = page.parse_reviews(review_blocks=review_blocks, parse_type="long")
    output_path = get_output_path(
        folder_path="/Users/pipchang/Documents/VSC/Projects/DH-S/download",
        file_name="db_Born_To_Fly_long_popular",
        file_type="jsonl",
    )
    save_dataclass_to_jsonl(objects=reviews, output_path=output_path)


if __name__ == "__main__":
    imdb_download()
    # db_download_short()
    # db_download_long()
    # rt_download()
