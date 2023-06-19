# Collect Reviews from Multiple Websites

# TODO

write config_template.yaml

write instructions on how to use library 'pip install -e .'

# Description

a package for crawling multiple movie websites for reviews
supported websites: IMDB, Rotten Tomatoes, Letterboxd, Metacritic

1. download html as .html files

2. parse .html files to extract needed information

3. store information in jsonl

# Needed columns:

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

