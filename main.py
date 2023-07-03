from ast import parse
from film_review_scraper.websites import IMDB, RottenTomatoes, Douban
from film_review_scraper.data_handling import get_output_path, save_dataclass_to_jsonl


def imdb_download():
    page = IMDB()
    review_blocks = page.fetch_reviews(
        url="https://www.imdb.com/title/tt3540136/reviews?sort=submissionDate&dir=desc&ratingFilter=0"
    )
    reviews = page.parse_reviews(review_blocks)
    output_path = get_output_path(
        folder_path="/Users/pipchang/Documents/VSC/Projects/DH-S/download",
        file_name="imdb_Wolf_Warrior",
        file_type="jsonl",
    )
    save_dataclass_to_jsonl(objects=reviews, output_path=output_path)


def rt_download():
    page = RottenTomatoes()
    review_blocks = page.fetch_reviews(
        url="https://www.rottentomatoes.com/m/last_tycoon/reviews?type=user"
    )
    reviews = page.parse_reviews(review_blocks)
    output_path = get_output_path(
        folder_path="/Users/pipchang/Documents/VSC/Projects/DH-S/download",
        file_name="rt_Last_Tycoon",
        file_type="jsonl",
    )
    save_dataclass_to_jsonl(objects=reviews, output_path=output_path)


def db_download_short():
    page = Douban()
    review_blocks = page.fetch_reviews(
        url="https://movie.douban.com/subject/1298293/comments?limit=20&status=P&sort=time",
        review_type="short",
    )
    reviews = page.parse_reviews(review_blocks=review_blocks, parse_type="short")
    output_path = get_output_path(
        folder_path="/Users/pipchang/Documents/VSC/Projects/DH-S/download",
        file_name="The_Last_Tycoon",
        file_type="jsonl",
    )
    save_dataclass_to_jsonl(objects=reviews, output_path=output_path)


def db_download_long():
    page = Douban()
    review_blocks = page.fetch_reviews(
        url="https://movie.douban.com/subject/3218852/reviews?sort=time",
        review_type="long",
    )
    reviews = page.parse_reviews(review_blocks=review_blocks, parse_type="long")
    output_path = get_output_path(
        folder_path="/Users/pipchang/Documents/VSC/Projects/DH-S/download",
        file_name="Last_Days",
        file_type="jsonl",
    )
    save_dataclass_to_jsonl(objects=reviews, output_path=output_path)


if __name__ == "__main__":
    rt_download()
