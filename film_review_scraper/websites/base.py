from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Union
from pathlib import Path
import yaml

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

class Website(ABC):
    @staticmethod
    def read_html_file(html_file: Union[str, Path]) -> str:
        html_file = Path(html_file)
        if not html_file.exists():
            raise FileNotFoundError(f"HTML file not found: {html_file}")
        with open(html_file, mode = "r") as file:
            html_source = file.read()
        return html_source

    @abstractmethod
    def download_html(self) -> str:
        pass

    @abstractmethod
    def parse(self) -> List:
        pass
