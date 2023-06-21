import re
import logging
from .base import Website
from dataclasses import dataclass
from typing import List, Optional, Literal
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException


logging.basicConfig(level=logging.INFO)

@dataclass
class DoubanReview:
    date: Optional[str]
    location: Optional[str]
    rating: Optional[str]
    rating_ratio: Optional[float]
    review: Optional[str]
    upvotes: Optional[int]

class Douban(Website):

    def fetch_short_reviews(self, url: str) -> List[BeautifulSoup]:
        with Chrome() as driver:
            driver.get(url)
            total_review_blocks = []
            while True:
                try:
                    page_source = BeautifulSoup(driver.page_source, 'html.parser')
                    if len(page_source.find_all("div", class_='comment-item')) != 1:
                        review_blocks = page_source.find_all("div", class_="comment-item")
                        total_review_blocks += review_blocks
                        self.load_next(driver, (By.CLASS_NAME, 'next'))
                    else:
                        logging.info("No more reviews to load.")
                        break
                except (NoSuchElementException, TimeoutException):
                    break
        return total_review_blocks

    def fetch_long_reviews(self, url: str) -> List[BeautifulSoup]:
        pass

    def fetch_reviews(self, url: str, review_type: Literal['short', 'long']) -> List[BeautifulSoup]:
        """
        BeautifulSoup should actually be bs4.element.Tag, but its common to refer to them all as BeautifulSoup objects cause they function kind of the same
        """
        try:
            if review_type == 'short':
                review_blocks = self.fetch_short_reviews(url)
            elif review_type == 'long':
                review_blocks = self.fetch_long_reviews(url)
            else:
                raise ValueError("review_type must be either 'short' or 'long'.")
        except ValueError as ve:
            logging.error(ve)
        except Exception as e:
            logging.error(f"An error occurred during fetching reviews: {e}")
        return review_blocks

    @staticmethod
    def parse_review_block(review_block: BeautifulSoup) -> DoubanReview:
        date_element = review_block.find("span", class_='comment-time')
        date = date_element.text.strip().split(" ")[0] if date_element else None

        location_element = review_block.find("span", class_='comment-location')
        location = location_element.text.strip() if location_element else None

        text = review_block.find("span", class_=re.compile(r'allstar\d+ rating'))
        if text:
            score = int(text.get('class')[0].replace('allstar', '')[0])
            rating = f'{score}/5'
            rating_ratio = score/5
        else:
            rating = None
            rating_ratio = None
        review_element = review_block.find("span", class_='short')
        review = review_element.text.strip() if review_element else None

        upvotes_element = review_block.find("span", class_='votes vote-count')
        upvotes = int(upvotes_element.text.strip()) if upvotes_element else None

        return DoubanReview(date, location, rating, rating_ratio, review, upvotes)

    def parse_reviews(self, review_blocks: List[BeautifulSoup]) -> List[DoubanReview]:
        reviews = [self.parse_review_block(review_block) for review_block in review_blocks]
        return reviews
