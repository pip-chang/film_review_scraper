from abc import ABC, abstractmethod
from typing import List, Dict
from pathlib import Path

class Website(ABC):
    @staticmethod
    def get_config(config_file: Path) -> Dict[str, str]:
        #TODO
        with open(config_file, mode = "r") as file:
            config = {line.strip().split('\t')[0] : line.strip().split('\t')[1] for line in file.readlines()}
        return config

    @staticmethod
    def read_html_file(html_file: Path) -> str:
        with open(html_file, mode = "r") as file:
            html_source = file.read()
        return html_source

    @abstractmethod
    def download_html(self, link: str) -> str:
        pass

    @abstractmethod
    def parse(self) -> List:
        pass
