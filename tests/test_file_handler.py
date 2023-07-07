import json
import tempfile
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import TypedDict

from data_handling import save_dataclass_to_jsonl, save_dicts_to_jsonl


@dataclass
class TestDataClass:
    a: int
    b: str


TEST_LIST = [
    {
        "date": "2023-06-20",
        "location": "重庆",
        "rating": "5/5",
        "rating_ratio": 1.0,
        "review": "只想大声说，祖国强大真好",
        "upvotes": 0,
        "website": "Douban",
    },
    {
        "date": "2023-05-03",
        "rating": "9/10",
        "rating_ratio": 0.9,
        "review": "burning, touching, funny: Born To Fly should be considered a successful commercial film.",
        "upvotes": 0,
        "total_votes": 7,
        "permalink": "/review/rw9030254/?ref_=tt_urv",
        "like_ratio": 0.0,
        "website": "IMDB",
    },
]


def test_save_dicts_to_jsonl():
    with tempfile.NamedTemporaryFile() as temp_file:
        temp_path = Path(temp_file.name)

        data = TEST_LIST

        save_dicts_to_jsonl(data, temp_path)

        with temp_path.open() as f:
            lines = f.readlines()
            assert len(lines) == len(data)
            for line, original_dict in zip(lines, data):
                assert json.loads(line) == original_dict


def test_save_dataclass_to_jsonl():
    with tempfile.NamedTemporaryFile() as temp_file:
        temp_path = Path(temp_file.name)

        data = [TestDataClass(a=1, b="test"), TestDataClass(a=2, b="test2")]

        save_dataclass_to_jsonl(data, temp_path)

        with temp_path.open() as f:
            lines = f.readlines()
            assert len(lines) == len(data)
            for line, original_object in zip(lines, data):
                assert json.loads(line) == asdict(original_object)
