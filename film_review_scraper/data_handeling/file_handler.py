from pathlib import Path
from bs4 import BeautifulSoup
from typing import Literal, Union, Optional, Type, Dict, List
from dataclasses import asdict, is_dataclass, dataclass, field
import json

def get_output_path(folder_path: str, file_name: str, file_type: Literal['html', 'jsonl']) -> Path:
    folder_path = Path(folder_path)
    folder_path.mkdir(parents=True, exist_ok=True)
    output_path = folder_path / f"{file_name}.{file_type}"
    return output_path


def read_from_html(html_file: Union[str, Path]) -> str:
    html_file = Path(html_file)
    if not html_file.exists():
        raise FileNotFoundError(f"HTML file not found: {html_file}")
    with open(html_file, mode = "r") as file:
        html_source = file.read()
    return html_source

def save_to_html(html_source: Optional[BeautifulSoup], output_path: Path) -> None:
    """
    Save HTML source to a file.

    Args:
        html_source (Union[str, BeautifulSoup]): HTML content to be saved. Can be a string or a BeautifulSoup object.
        output_path (str): Directory path where the file will be saved.
        file_name (str): Name of the file (without extension).

    Returns:
        None
    """
    with output_path.open(mode='w', encoding='utf-8') as file:
        file.write(html_source)

def save_to_jsonl(objects: List[Type], output_path: Path) -> None:
    with output_path.open(mode="a+", encoding="utf-8") as f:
        for object in objects:
            if not is_dataclass(object):
                raise TypeError(f"Object {object} is not a dataclass.")
            jsonline = json.dumps(asdict(object), ensure_ascii=False)
            f.write(jsonline + "\n")


@dataclass
class FilmConfig:
    config: Dict = field(default_factory=dict)

    @staticmethod
    def get_config(config_file: Union[str, Path]) -> Dict:
        config_file = Path(config_file)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")
        with open(config_file, mode = "r") as file:
            config = yaml.safe_load(config_file.read_text())
        return config

    def load_config(self, config_file: Union[str, Path]) -> None:
        self.config = self.get_config(config_file)