from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Union
import re

from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from .base import Website


@dataclass
class IMDBReview:
    date: Optional[str]
    rating: Optional[str]
    rating_ratio: Optional[float]
    review: Optional[str]
    upvotes: Optional[int]
    total_votes: Optional[int]
    permalink: Optional[str]
    like_ratio: Union[float, int] = field(init=False)
    website: str = "IMDB"

    def __post_init__(self) -> None:
        if self.total_votes == 0:
            self.like_ratio = None
        else:
            self.like_ratio = self.upvotes / self.total_votes


class IMDB(Website):
    def fetch_reviews(self, url: str) -> List[BeautifulSoup]:
        total_review_blocks = []
        with Chrome() as driver:
            driver.get(url)
            while True:
                try:
                    self.load_next(driver, (By.CLASS_NAME, "ipl-load-more__button"))
                except TimeoutException:
                    break
            self.load_element(driver, (By.CLASS_NAME, "imdb-user-review"))
            page_source = BeautifulSoup(driver.page_source, "html.parser")
            total_review_blocks = page_source.find_all(
                "div", class_=re.compile("imdb-user-review")
            )

        return total_review_blocks

    @staticmethod
    def parse_review_block(review_block: BeautifulSoup) -> IMDBReview:
        date_element = review_block.find("span", class_="review-date")
        if date_element:
            date_string = date_element.text
            dt_object = datetime.strptime(date_string, "%d %B %Y")
            date = dt_object.strftime("%Y-%m-%d")
        else:
            date = None

        score = review_block.find(string=re.compile(r"^\d{1,2}$"))
        if score:
            rating = f"{score}/10"
            rating_ratio = int(score) / 10
        else:
            rating = None
            rating_ratio = None

        review_title_element = review_block.find("a", class_="title")
        review_title = review_title_element.text.strip() if review_title_element else ""
        review_body_element = review_block.find(
            "div", class_=re.compile(r"text show-more")
        )
        review_body = review_body_element.text.strip() if review_body_element else ""
        review = f"{review_title}: {review_body}"

        vote_element = review_block.find(string=re.compile(r"found this helpful"))
        votes = vote_element.text.strip()
        upvotes, total_votes = map(int, re.findall(r"\d+", votes))

        permalink_element = review_block.find("a", string=re.compile("Permalink"))
        permalink = permalink_element.get("href") if permalink_element else None

        return IMDBReview(
            date, rating, rating_ratio, review, upvotes, total_votes, permalink
        )

    def parse_reviews(self, review_blocks: List[BeautifulSoup]) -> List[IMDBReview]:
        reviews = []
        reviews = [
            self.parse_review_block(review_block) for review_block in review_blocks
        ]
        return reviews
