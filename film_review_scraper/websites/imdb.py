from dataclasses import dataclass
from typing import List, Dict, Optional
from time import sleep
from bs4 import BeautifulSoup, element
from selenium import webdriver   
from selenium.webdriver.common.by import By
from .base import Website
import re

@dataclass
class IMDBReview:
    date: str
    review: str
    upvotes: int
    total_votes: int
    permalink: str

    @property
    def like_ratio(self) -> Optional[float]:
        if self.total_votes == 0:
            return None
        else:
            return self.upvotes/self.total_votes

class IMDB(Website):
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.url = None
    
    def get_config(self) -> Dict[str, str]:
        config = Website.get_config(self.config_file)
        self.url = config.get('Url')
        return config

    def download_html(self, url: str) -> str:
        with webdriver.Chrome() as driver:
            driver.get(url)
            loading = True
            while loading:
                try:
                    load_more_button = driver.find_element(By.CSS_SELECTOR, "button[id='load-more-trigger']")
                    load_more_button.click()
                    sleep(2)
                except Exception as e:
                    loading = False
                    print(e)
        return driver.page_source

    @staticmethod
    def parse_review_block(review_block: element.Tag) -> IMDBReview:
        date = review_block.find("span", class_="review-date").text
        review = review_block.find("div", class_=re.compile(r"text show-more")).text
        vote_text = review_block.find(string=re.compile(r"found this helpful")).text.strip()
        upvotes, total_votes = map(int, re.findall(r'\d+', vote_text))
        permalink = review_block.find("a", string=re.compile("Permalink"))['href']
        return IMDBReview(date, review, upvotes, total_votes, permalink)

    def parse(self, html_source: str) -> List[IMDBReview]:
        soup = BeautifulSoup(html_source, 'html.parser')
        review_blocks = soup.find_all("div", class_=re.compile("imdb-user-review"))
        reviews = [self.parse_review_block(review_block) for review_block in review_blocks]
        return reviews
