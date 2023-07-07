import logging
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
    """
    A subclass of Website that handles scraping and parsing of Rotten Tomatoes reviews.
    """

    @staticmethod
    def click_privacy_option(driver: Chrome):
        """
        Attempts to find and click the privacy agreement button on a Rotten Tomatoes page.

        Args:
            driver (Chrome): The WebDriver instance to use.

        Raises:
            TimeoutException: If the privacy button could not be found within the set wait time.
            NoSuchElementException, ElementNotInteractableException: If there are issues interacting with the privacy button.
            Exception: If an unexpected error occurs.
        """
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
        """
        Fetches all audience reviews from a Rotten Tomatoes movie page.

        Args:
            url (str): The URL of the Rotten Tomatoes movie page to fetch reviews from.
            headless_mode (bool, optional): If True, Chrome will run in headless mode. Defaults to False.

        Returns:
            List[BeautifulSoup]: A list of BeautifulSoup objects, each representing a single review block.
        """
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
        """
        Parses a single review block from a Rotten Tomatoes movie page into a RottenTomatoesReview object.

        This method extracts various details from the review block. If an exception occurs
        during parsing, the method prints the failed review block, an error message and returns None.

        Args:
            review_block (BeautifulSoup): The review block to be parsed.

        Returns:
            RottenTomatoesReview: An RottenTomatoesReview object containing all parsed data from the review block.
            None: If an error occurs during parsing.
        """
        try:
            date_element = review_block.find(
                "span", class_="audience-reviews__duration"
            )
            if date_element:
                date_string = date_element.text.replace(",", "")
                dt_object = datetime.strptime(date_string, "%b %d %Y")
                date = dt_object.strftime("%Y-%m-%d")
            else:
                date = None

            full_stars = len(
                review_block.find_all("span", class_="star-display__filled")
            )
            half_stars = len(review_block.find_all("span", class_="star-display__half"))
            score = full_stars + half_stars * 0.5
            rating = f"{score}/5"
            rating_ratio = score / 5

            review_element = review_block.find(
                "p", class_="audience-reviews__review js-review-text"
            )
            review = review_element.text.strip() if review_element else None

            return RottenTomatoesReview(date, rating, rating_ratio, review)
        except Exception as e:
            print(f"Failed to parse:\n{review_block}\nError: {e}")
            return None

    def parse_reviews(
        self, review_blocks: List[BeautifulSoup]
    ) -> List[RottenTomatoesReview]:
        """
        Parses a list of review blocks into a list of RottenTomatoesReview objects, discarding any that fail to parse.

        Args:
            review_blocks (List[BeautifulSoup]): The list of BeautifulSoup objects representing the review blocks to parse.

        Returns:
            List[RottenTomatoesReview]: The list of successfully parsed reviews. If a review block fails to parse, it is excluded from this list.
        """
        reviews = []
        reviews = [
            self.parse_review_block(review_block)
            for review_block in review_blocks
            if self.parse_review_block(review_block) is not None
        ]
        return reviews
