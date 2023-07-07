from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, Union, Optional, Type, List
from dataclasses import asdict, is_dataclass
import json


def get_output_path(folder_path: str, file_name: str, file_type: str) -> Path:
    """
    Constructs the path where the output file will be stored.

    Args:
        folder_path (str): The path to the directory where the file will be stored.
        file_name (str): The name of the file.
        file_type (str): The extension of the file (e.g., 'html', 'jsonl').

    Returns:
        Path: The path object where the file will be stored.
    """
    folder_path = Path(folder_path)
    folder_path.mkdir(parents=True, exist_ok=True)
    output_path = folder_path / f"{file_name}.{file_type}"
    return output_path


def get_files_in_folder(folder_path: str, file_type: str) -> List[Path]:
    """
    Retrieves all the files of a specified type in the given folder.

    Args:
        folder_path (str): The path to the folder where files will be searched.
        file_type (str): The type of the files to retrieve.

    Returns:
        List[Path]: A list of paths to the files found in the folder.
    """
    folder_path = Path(folder_path)
    return list(folder_path.glob(f"*.{file_type}"))


def read_html_to_soup(html_file: Union[str, Path]) -> BeautifulSoup:
    """
    Parses an HTML file into a BeautifulSoup object.

    Args:
        html_file (Union[str, Path]): The path to the HTML file to be parsed.

    Raises:
        FileNotFoundError: If the specified HTML file does not exist.

    Returns:
        BeautifulSoup: The parsed HTML document.
    """
    html_file = Path(html_file)
    if not html_file.exists():
        raise FileNotFoundError(f"HTML file not found: {html_file}")
    with open(html_file, mode="r") as file:
        html_source = file.read()
    page_source = BeautifulSoup(html_source, "html.parser")
    return page_source


def read_jsonl_to_dict(jsonl_path: Union[str, Path]) -> List[Dict]:
    """
    Reads a JSONL file and returns its content as a list of dictionaries.

    Args:
        jsonl_path (Union[str, Path]): The path to the JSONL file.

    Returns:
        List[Dict]: A list of dictionaries representing the JSONL data.
    """
    data = []
    with open(jsonl_path, "r") as file:
        for line in file:
            data.append(json.loads(line))
    return data


def save_soup_to_html(html_source: Optional[BeautifulSoup], output_path: Path) -> None:
    """
    Writes a BeautifulSoup object to an HTML file.

    Args:
        html_source (Optional[BeautifulSoup]): The BeautifulSoup object to be written to file.
        output_path (Path): The path where the HTML file will be saved.
    """
    with output_path.open(mode="w", encoding="utf-8") as file:
        file.write(html_source)


def save_dicts_to_jsonl(list_of_dicts: List[Dict], output_path: Path) -> None:
    """
    Writes a list of dictionaries to a JSONL file.

    Args:
        list_of_dicts (List[Dict]): The list of dictionaries to be written to file.
        output_path (Path): The path where the JSONL file will be saved.

    Raises:
        TypeError: If any element in the list_of_dicts is not a dictionary.
    """
    with output_path.open(mode="a+", encoding="utf-8") as file:
        for dictionary in list_of_dicts:
            if not isinstance(dictionary, dict):
                raise TypeError(f"Object {dictionary} is not a dict.")
            jsonline = json.dumps(dictionary, ensure_ascii=False)
            file.write(jsonline + "\n")


def save_dataclass_to_jsonl(objects: List[Type], output_path: Path) -> None:
    """
    Writes a list of dataclass objects to a JSONL file.

    Args:
        objects (List[Type]): The list of dataclass objects to be written to file.
        output_path (Path): The path where the JSONL file will be saved.

    Raises:
        TypeError: If any element in the objects list is not a dataclass.
    """
    with output_path.open(mode="a+", encoding="utf-8") as file:
        for object in objects:
            if not is_dataclass(object):
                raise TypeError(f"Object {object} is not a dataclass.")
            jsonline = json.dumps(asdict(object), ensure_ascii=False)
            file.write(jsonline + "\n")
