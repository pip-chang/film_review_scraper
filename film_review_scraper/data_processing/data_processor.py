from dataclasses import dataclass, field
from pathlib import Path
from typing import Union, Dict, List
import yaml

from data_handling import read_jsonl_to_dict, get_files_in_folder


@dataclass
class FilmData:
    name: str
    data: Dict

    @staticmethod
    def from_file(file_path: Union[str, Path]) -> "FilmData":
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Film data file not found: {file_path}")
        with open(file_path, mode="r") as file:
            data = yaml.safe_load(file)
        return FilmData(name=data.get("film"), data=data)


@dataclass
class ReviewData:
    name: str
    data: List[Dict]

    @staticmethod
    def get_total_data_from_folder(folder_path: str) -> List[Dict]:
        paths = get_files_in_folder(folder_path=folder_path, file_type="jsonl")
        total_data = []
        for path in paths:
            data = read_jsonl_to_dict(path)
            total_data += data
        return total_data

    def from_folder(cls, folder_path: Union[str, Path], film_name: str) -> "ReviewData":
        total_data = cls.get_total_data_from_folder(folder_path)
        keys = set().union(*total_data)
        concatenated_data = [
            {key: data.get(key) for key in keys} for data in total_data
        ]
        return ReviewData(name=film_name, data=concatenated_data)


def merge_film_and_review_data(
    film_data: FilmData, review_data: ReviewData
) -> List[Dict]:
    merged_data = []
    film = film_data.data
    for review in review_data.data:
        merged = film | review
        merged_data.append(merged)
    return merged_data
