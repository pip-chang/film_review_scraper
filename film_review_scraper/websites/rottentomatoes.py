import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
)

from .base import Website

logging.basicConfig(level=logging.INFO)


@dataclass
class RottenTomatoesReview:
    date: Optional[str]
    rating: Optional[str]
    rating_ratio: Optional[float]
    review: Optional[str]
    website: str = "Rotten Tomatoes"


class RottenTomatoes(Website):
    @staticmethod
    def click_privacy_option(driver: Chrome):
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "onetrust-button-group"))
            )
            privacy_button = driver.find_element(By.ID, "onetrust-button-group")
            privacy_button.click()
        except TimeoutException as e:
            logging.info("Timeout occured: privacy button not found in time limit.")
            raise
        except (NoSuchElementException, ElementNotInteractableException) as e:
            logging.info("No privacy button to click.")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise

    def fetch_reviews(
        self, url: str, headless_mode: bool = False
    ) -> List[BeautifulSoup]:
        total_review_blocks = []
        driver = self.initiate_chrome(headless_mode=headless_mode)
        driver.get(url)
        self.click_privacy_option(driver)

        while True:
            try:
                self.load_element(driver, (By.CLASS_NAME, "audience-review-row"))
                page_source = BeautifulSoup(driver.page_source, "html.parser")
                review_blocks = page_source.find_all(
                    "div", class_="audience-review-row"
                )
                total_review_blocks += review_blocks
                self.load_next(driver, (By.CLASS_NAME, "next"))
            except (
                TimeoutException,
                NoSuchElementException,
                ElementNotInteractableException,
            ):
                break

        driver.quit()

        return total_review_blocks

    @staticmethod
    def parse_review_block(review_block: BeautifulSoup) -> RottenTomatoesReview:
        date_element = review_block.find("span", class_="audience-reviews__duration")
        if date_element:
            date_string = date_element.text.replace(",", "")
            dt_object = datetime.strptime(date_string, "%b %d %Y")
            date = dt_object.strftime("%Y-%m-%d")
        else:
            date = None

        full_stars = len(review_block.find_all("span", class_="star-display__filled"))
        half_stars = len(review_block.find_all("span", class_="star-display__half"))
        score = full_stars + half_stars * 0.5
        rating = f"{score}/5"
        rating_ratio = score / 5

        review_element = review_block.find(
            "p", class_="audience-reviews__review js-review-text"
        )
        review = review_element.text.strip() if review_element else None

        return RottenTomatoesReview(date, rating, rating_ratio, review)

    def parse_reviews(
        self, review_blocks: List[BeautifulSoup]
    ) -> List[RottenTomatoesReview]:
        reviews = []
        reviews = [
            self.parse_review_block(review_block) for review_block in review_blocks
        ]
        return reviews
