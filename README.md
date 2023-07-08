# Film Review Scraper

The film_review_scraper is a Python library for scraping and storing film reviews from various websites.

Currently supported websites: [IMDB](https://www.imdb.com/), [RottenTomatoes](https://www.rottentomatoes.com/), [Douban](https://movie.douban.com/)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install film_review_scraper.

```bash
pip install film_review_scraper
```

## Quick Start

```python
from film_review_scraper import IMDB

website = IMDB()

reviews = website.parse_reviews(website.fetch_reviews("https://www.imdb.com/title/tt0780504/reviews?ref_=tt_urv"))
```

## Usage

Please refer to the [demonstration](https://nbviewer.org/github/pip-chang/film_review_scraper/blob/main/demonstration.ipynb) for detailed usage.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Upcoming Updates:
[ ] IMDB critic reviews with external links

[ ] Rotten Tomatoes critic reviews with external links

[ ] Douban discussion threads
