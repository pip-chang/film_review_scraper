from dataclasses import dataclass, field
from pathlib import Path
from typing import Union, Dict, List
import yaml

from data_handling import read_jsonl_to_dict, get_files_in_folder


@dataclass
class FilmData:
    """
    A data class for holding film data.

    Attributes:
        name (str): The name of the film.
        data (Dict): The dictionary containing the film's data.
    """

    name: str
    data: Dict

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "FilmData":
        """
        Creates a FilmData object from a file.

        Args:
            file_path (Union[str, Path]): Path to the YAML file containing the film data.

        Raises:
            FileNotFoundError: If the specified file path does not exist.

        Returns:
            FilmData: A new FilmData object.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Film data file not found: {file_path}")
        with open(file_path, mode="r") as file:
            data = yaml.safe_load(file)
        return cls(name=data.get("film"), data=data)


@dataclass
class ReviewData:
    """
    A data class for holding review data.

    Attributes:
        name (str): The name of the film being reviewed.
        data (List[Dict]): A list of dictionaries, each containing a review.
    """

    name: str
    data: List[Dict]

    @staticmethod
    def get_total_data_from_folder(folder_path: str) -> List[Dict]:
        """
        Static method to retrieve data from all JSONL files within a specified folder.

        Args:
            folder_path (str): The path to the folder containing the JSONL files.

        Returns:
            List[Dict]: A list of dictionaries, each representing data from one JSONL file.
        """
        paths = get_files_in_folder(folder_path=folder_path, file_type="jsonl")
        total_data = []
        for path in paths:
            data = read_jsonl_to_dict(path)
            total_data += data
        return total_data

    @classmethod
    def from_folder(cls, folder_path: Union[str, Path], film_name: str) -> "ReviewData":
        """
        Class method to create a ReviewData instance from all JSONL files within a specified folder.

        Args:
            folder_path (Union[str, Path]): The path to the folder containing the JSONL files.
            film_name (str): The name of the film being reviewed.

        Returns:
            ReviewData: A ReviewData instance with the film's name and all the review data.
        """
        total_data = cls.get_total_data_from_folder(folder_path)
        keys = set().union(*total_data)
        concatenated_data = [
            {key: data.get(key) for key in keys} for data in total_data
        ]
        return cls(name=film_name, data=concatenated_data)


def merge_film_and_review_data(
    film_data: FilmData, review_data: ReviewData
) -> List[Dict]:
    """
    Merges film and review data.

    Args:
        film_data (FilmData): A FilmData instance containing the film's data.
        review_data (ReviewData): A ReviewData instance containing the review data.

    Returns:
        List[Dict]: A list of dictionaries, each containing merged film and review data.
    """
    merged_data = []
    film = film_data.data
    for review in review_data.data:
        merged = film | review
        merged_data.append(merged)
    return merged_data
