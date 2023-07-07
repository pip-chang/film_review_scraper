from typing import Literal
from data_handling.file_handler import save_dicts_to_jsonl

from data_processing.data_processor import (
    FilmData,
    ReviewData,
    merge_film_and_review_data,
)
from websites import IMDB, RottenTomatoes, Douban
from data_handling import (
    get_files_in_folder,
    get_output_path,
    save_dataclass_to_jsonl,
)
from data_processing import FilmData, ReviewData, merge_film_and_review_data

FILM_NAME = "The Last Tycoon"

IMDB_URL = "https://www.imdb.com/title/tt0074777/reviews?sort=submissionDate&dir=desc&ratingFilter=0"
RT_URL = "https://www.rottentomatoes.com/m/last_tycoon/reviews?type=user"
DB_SHORT_URL = "https://movie.douban.com/subject/1298293/comments?sort=time&status=P"
DB_LONG_URL = "https://movie.douban.com/subject/1298293/reviews?sort=time"

REVIEW_OUTPUT_FOLDER = "/Users/pipchang/Documents/VSC/Projects/DH-S/the_last_tycoon"
FILM_DATA_FILE = (
    "/Users/pipchang/Documents/VSC/Projects/DH-S/the_last_tycoon/the_last_tycoon.yaml"
)


def imdb_download(film_name: str, url: str, output_folder: str):
    page = IMDB()
    review_blocks = page.fetch_reviews(url=url)
    reviews = page.parse_reviews(review_blocks)
    output_path = get_output_path(
        folder_path=output_folder,
        file_name=f"imdb_{film_name}",
        file_type="jsonl",
    )
    save_dataclass_to_jsonl(objects=reviews, output_path=output_path)


def rt_download(film_name: str, url: str, output_folder: str):
    page = RottenTomatoes()
    review_blocks = page.fetch_reviews(url=url)
    reviews = page.parse_reviews(review_blocks)
    output_path = get_output_path(
        folder_path=output_folder,
        file_name=f"rt_{film_name}",
        file_type="jsonl",
    )
    save_dataclass_to_jsonl(objects=reviews, output_path=output_path)


def db_download(
    review_type: Literal["short", "long"], film_name: str, url: str, output_folder: str
):
    page = Douban()
    review_blocks = page.fetch_reviews(
        url=url,
        review_type=review_type,
    )
    reviews = page.parse_reviews(review_blocks=review_blocks, parse_type=review_type)
    output_path = get_output_path(
        folder_path=output_folder,
        file_name=f"db_{review_type}_{film_name}",
        file_type="jsonl",
    )
    save_dataclass_to_jsonl(objects=reviews, output_path=output_path)


def export_all_data_to_jsonl(input_folder: str, output_folder: str, file_name: str):
    film_config = get_files_in_folder(folder_path=input_folder, file_type="yaml")[0]
    film_data = FilmData.from_file(film_config)
    review_data = ReviewData.from_folder(
        folder_path=input_folder, film_name=film_data.name
    )
    all_data = merge_film_and_review_data(film_data=film_data, review_data=review_data)
    output_path = get_output_path(
        folder_path=output_folder, file_name=file_name, file_type="jsonl"
    )
    save_dicts_to_jsonl(list_of_dicts=all_data, output_path=output_path)


if __name__ == "__main__":
    if False:
        # download
        imdb_download(
            film_name=FILM_NAME, url=IMDB_URL, output_folder=REVIEW_OUTPUT_FOLDER
        )
        rt_download(
            film_name=FILM_NAME, url=IMDB_URL, output_folder=REVIEW_OUTPUT_FOLDER
        )
        db_download(
            review_type="short",
            film_name=FILM_NAME,
            url=IMDB_URL,
            output_folder=REVIEW_OUTPUT_FOLDER,
        )
        db_download(
            review_type="long",
            film_name=FILM_NAME,
            url=IMDB_URL,
            output_folder=REVIEW_OUTPUT_FOLDER,
        )

        # merge
        export_all_data_to_jsonl(
            input_folder=REVIEW_OUTPUT_FOLDER,
            output_folder=REVIEW_OUTPUT_FOLDER,
            file_name="the_last_tycoon",
        )
