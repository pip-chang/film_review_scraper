import tempfile
import json
from pathlib import Path

from data_processing import FilmData, ReviewData, merge_film_and_review_data


def test_film_data_from_file():
    yaml_data = """
    film: Test Film
    data:
        genre: Action
        year: 2023
    """
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as temp_file:
        temp_file.write(yaml_data)
        temp_file.seek(0)

        film_data = FilmData.from_file(temp_file.name)

        assert film_data.name == "Test Film"
        assert film_data.data == {
            "film": "Test Film",
            "data": {"genre": "Action", "year": 2023},
        }


def test_review_data_from_folder():
    review_data = [
        {"a": 1, "b": 2},
        {"a": 1, "c": 3},
    ]
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = Path(temp_dir) / "temp_file.jsonl"
        with open(temp_file_path, "w") as temp_file:
            for data in review_data:
                jsonline = json.dumps(data, ensure_ascii=False)
                temp_file.write(jsonline + "\n")

        review_data = ReviewData.from_folder(temp_dir, "Test Film")

        assert review_data.name == "Test Film"
        assert review_data.data == [
            {"a": 1, "b": 2, "c": None},
            {"a": 1, "b": None, "c": 3},
        ]


def test_merge_film_and_review_data():
    film_data = FilmData(name="Test Film", data={"genre": "Action", "year": 2023})
    review_data = ReviewData(
        name="Test Film",
        data=[{"review": "Great movie!", "date": "2021-10-08", "rating_ratio": 0.8}],
    )

    merged_data = merge_film_and_review_data(film_data, review_data)

    assert merged_data == [
        {
            "genre": "Action",
            "year": 2023,
            "review": "Great movie!",
            "date": "2021-10-08",
            "rating_ratio": 0.8,
        }
    ]
