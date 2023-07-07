from .websites import IMDB, RottenTomatoes, Douban
from .data_handling import save_dataclass_to_jsonl, save_dicts_to_jsonl
from .data_processing import FilmData, ReviewData, merge_film_and_review_data
from .data_handling import (
    get_output_path,
    save_dataclass_to_jsonl,
    save_soup_to_html,
    read_html_to_soup,
    read_jsonl_to_dict,
    get_files_in_folder,
    save_dicts_to_jsonl,
)
