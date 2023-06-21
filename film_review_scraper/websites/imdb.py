from dataclasses import dataclass, field
from typing import List, Optional, Union
from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup, element
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base import Website
import re

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

    def __post_init__(self) -> None:
        if self.total_votes == 0:
            self.like_ratio = None
        else:
            self.like_ratio = self.upvotes/self.total_votes


class IMDB(Website):
    def fetch_reviews(self, url: str) -> str:
        with Chrome() as driver:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[id='load-more-trigger']")))
            
            loading = True
            while loading:
                try:
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[id='load-more-trigger']")))
                    load_more_button = driver.find_element(By.CSS_SELECTOR, "button[id='load-more-trigger']")
                    sleep(2)
                    load_more_button.click()
                except Exception as e:
                    loading = False
                    print(f"Loading completed or an error occurred: {e}")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            return str(soup)

    @staticmethod
    def parse_review_block(review_block: element.Tag) -> IMDBReview:
        try:
            date_string = review_block.find("span", class_="review-date").text
            dt_object = datetime.strptime(date_string, "%d %B %Y")
            date = dt_object.strftime("%Y-%m-%d")
            score = review_block.find(string=re.compile(r'^\d{1,2}$'))
            if score:
                rating = f"{score}/10"
                rating_ratio = float(score)/10
            else:
                rating = None
                rating_ratio = None
            review_title = review_block.find("a", class_="title").text.strip()
            review_body = review_block.find("div", class_=re.compile(r"text show-more")).text.strip()
            review = f"{review_title} {review_body}"
            vote_text = review_block.find(string=re.compile(r"found this helpful")).text.strip()
            upvotes, total_votes = map(int, re.findall(r'\d+', vote_text))
            permalink = review_block.find("a", string=re.compile("Permalink"))['href']
        except Exception as e:
            print(review_block)
            print(f"An error occurred: {e}")
        return IMDBReview(date, rating, rating_ratio, review, upvotes, total_votes, permalink)

    def parse_html(self, html_source: str) -> List[IMDBReview]:
        soup = BeautifulSoup(html_source, 'html.parser')
        review_blocks = soup.find_all("div", class_=re.compile("imdb-user-review"))
        reviews = [self.parse_review_block(review_block) for review_block in review_blocks]
        return reviews
