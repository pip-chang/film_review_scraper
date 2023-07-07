import tempfile
from pathlib import Path
import yaml

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
        assert film_data.data == {"film": "Test Film", "data": {"genre": "Action", "year": 2023}}

def test_review_data_from_folder(mocker):
    mocker.patch('data_handling.get_files_in_folder', return_value=['path1', 'path2'])
    mocker.patch('data_handling.read_jsonl_to_dict', side_effect=[ 
        [{"review1": "Awesome movie!"}], [{"review2": "Must watch!"}]
    ])

    review_data = ReviewData.from_folder("fake_folder_path", "Test Film")

    assert review_data.name == "Test Film"
    assert review_data.data == [{"review1": "Awesome movie!", "review2": None}, {"review1": None, "review2": "Must watch!"}]

def test_merge_film_and_review_data():
    film_data = FilmData(name="Test Film", data={"genre": "Action", "year": 2023})
    review_data = ReviewData(name="Test Film", data=[{"review": "Awesome movie!"}])

    merged_data = merge_film_and_review_data(film_data, review_data)

    assert merged_data == [{"genre": "Action", "year": 2023, "review": "Awesome movie!"}]
