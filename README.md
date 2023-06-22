# Collect Reviews from Multiple Websites

# TODO

modify IMDB and RottenTomatoes

write instructions on how to use library 'pip install -e .'

data storing

tests

docs

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

