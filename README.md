# Film Review Scraper

The film_review_scraper is a Python library for scraping and storing film reviews from various websites.

Currently working websites: [IMDB](https://www.imdb.com/), [RottenTomatoes](https://www.rottentomatoes.com/), [Douban](https://movie.douban.com/)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install film_review_scraper.

```bash
pip install foobar
```

## Usage

```python
import foobar

# returns 'words'
foobar.pluralize('word')

# returns 'geese'
foobar.pluralize('goose')

# returns 'phenomenon'
foobar.singularize('phenomena')
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)

# TODO

write instructions on how to use library 'pip install -e .'

# Description

a package for crawling multiple movie websites for *audience* reviews
supported websites: IMDB, Rotten Tomatoes, Letterboxd, Metacritic

- film_review_scraper

    - websites

        fetch review containers: url -> list of review blocks (to be saved or parsed)
                                        check for missing data

        parse review blocks: review blocks -> dict-like review data (to be saved or organized with other dict-ike objects)

    - data handling

        read html: path html -> html (to be parsed with website parser)

        read_jsonl: path jsonl -> dict-like review data (to be organized with other dict-ike objects)

        save html: dict-like data -> None (save as html)

        save jsonl: dict-like data -> None (save as jsonl)

        read config: path yaml -> dict (to be organized with other dict-ike objects)

    - data processing

        organize data: dict-like objects -> jsonl? csv?

    scrape: pipeline for scraping, prganizing and storing

# Data need saving (tbc):

Source Type: public review website
Source: IMDB, RottenTomatoes, Reddit...
Reviewer Type: critic, audience...
Language: en, cn

Reviewer: names
Gender: male, female...
Rating: 4/10, 3/5... (maybe a float)
Review: review_text
Review Date: 00-00-0000
Dislike Ratio: 0.6
URL: link of review

Film Type: [genres]
Film: film_name in English
Theater Release Date: 00-00-0000
Streaming Release Date: 00-00-0000
Director: name
Production Companies:
Country: China, US
International Collaboration: True, False
Language: en, cn
Budget: (in dollar)
Box Office: (in dollar)


For other sources:
SourceType: journalism, social media, review websites, magazines...
