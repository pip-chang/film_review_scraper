from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, Union, Optional, Type, List, is_typeddict
from dataclasses import asdict, is_dataclass
import json
import yaml


def get_output_path(folder_path: str, file_name: str, file_type: str) -> Path:
    folder_path = Path(folder_path)
    folder_path.mkdir(parents=True, exist_ok=True)
    output_path = folder_path / f"{file_name}.{file_type}"
    return output_path


def get_files_in_folder(folder_path: str, file_type: str) -> List[Path]:
    folder_path = Path(folder_path)
    return list(folder_path.glob(f"*.{file_type}"))


def read_html_to_soup(html_file: Union[str, Path]) -> BeautifulSoup:
    html_file = Path(html_file)
    if not html_file.exists():
        raise FileNotFoundError(f"HTML file not found: {html_file}")
    with open(html_file, mode="r") as file:
        html_source = file.read()
    page_source = BeautifulSoup(html_source, "html.parser")
    return page_source


def read_jsonl_to_dict(jsonl_path: Union[str, Path]) -> List[Dict]:
    data = []
    with open(jsonl_path, "r") as f:
        for line in f:
            data.append(json.loads(line))
    return data


def save_soup_to_html(html_source: Optional[BeautifulSoup], output_path: Path) -> None:
    with output_path.open(mode="w", encoding="utf-8") as file:
        file.write(html_source)


def save_dicts_to_jsonl(list_of_dicts: List[Dict], output_path: Path) -> None:
    with output_path.open(mode="a+", encoding="utf-8") as file:
        for dict in list_of_dicts:
            if not is_typeddict(dict):
                raise TypeError(f"Object {dict} is not a dict.")
            jsonline = json.dumps(dict, ensure_ascii=False)
            file.write(jsonline + "\n")


def save_dataclass_to_jsonl(objects: List[Type], output_path: Path) -> None:
    with output_path.open(mode="a+", encoding="utf-8") as file:
        for object in objects:
            if not is_dataclass(object):
                raise TypeError(f"Object {object} is not a dataclass.")
            jsonline = json.dumps(asdict(object), ensure_ascii=False)
            file.write(jsonline + "\n")
