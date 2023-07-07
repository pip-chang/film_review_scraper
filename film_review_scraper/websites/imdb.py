from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple, Optional, Union
import re

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
)

from .base import Website


@dataclass
class IMDBReview:
    """
    Data class for storing short review information from IMDB.

    Attributes:
        date (Optional[str]): The date when the review was posted in the format of "YYYY-MM-DD" (e.g. "2022-05-01").
        rating (Optional[str]): The rating given by the user in the format of "rating/full_rating" (e.g. "7/10").
        rating_ratio (Optional[float]): The rating given by the user, normalized to a scale of 0 to 1.
        review (Optional[str]): The review text.
        upvotes (Optional[int]): The number of upvotes the review received.
        total_votes (Optional[int]): The total number of votes (upvotes and downvotes) the review received.
        permalink (Optional[str]): The permalink of the review.
        like_ratio (Union[float, int]): The ratio of upvotes to total votes, set in the post-initialization stage.
        website (str): The website from which the review was scraped.
    """

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
    """
    A subclass of Website that handles scraping and parsing of IMDB reviews.
    """

    def fetch_reviews(
        self, url: str, headless_mode: bool = False
    ) -> List[BeautifulSoup]:
        """
        Fetches reviews from the given IMDB URL.

        Note:
            It is possible to scrape all reviews without logging in an IMDB account.

        Args:
            url (str): The URL to scrape reviews from.
            headless_mode (bool): A flag indicating whether to run the browser in headless mode. Defaults to False.

        Returns:
            List[BeautifulSoup]: A list of BeautifulSoup objects, each representing a block of review data.
        """
        total_review_blocks = []
        driver = self.initiate_chrome(headless_mode=headless_mode)
        driver.get(url)

        while True:
            try:
                self.load_element(driver, (By.CLASS_NAME, "imdb-user-review"))
                page_source = BeautifulSoup(driver.page_source, "html.parser")
            except:
                break
            try:
                self.load_next(driver, (By.CLASS_NAME, "ipl-load-more__button"))
            except (
                TimeoutException,
                NoSuchElementException,
                ElementNotInteractableException,
            ):
                break
        total_review_blocks = page_source.find_all(
            "div", class_=re.compile("imdb-user-review")
        )

        driver.quit()

        return total_review_blocks

    @staticmethod
    def parse_date(review_block: BeautifulSoup) -> Optional[str]:
        """
        Parses the review date from the review block.

        Args:
            review_block (BeautifulSoup): A BeautifulSoup object representing a review block.

        Returns:
            Optional[str]: The review date if available, otherwise None.
        """
        date_element = review_block.find("span", class_="review-date")
        if date_element:
            date_string = date_element.text
            dt_object = datetime.strptime(date_string, "%d %B %Y")
            return dt_object.strftime("%Y-%m-%d")
        else:
            return None

    @staticmethod
    def parse_rating(
        review_block: BeautifulSoup,
    ) -> Tuple[Optional[str], Optional[float]]:
        """
        Parses the rating from the review block.

        Args:
            review_block (BeautifulSoup): A BeautifulSoup object representing a review block.

        Returns:
            Tuple[Optional[str], Optional[float]]: The rating and the rating ratio if available, otherwise (None, None).
        """
        score = review_block.find(string=re.compile(r"^\d{1,2}$"))
        if score:
            rating = f"{score}/10"
            rating_ratio = int(score) / 10
            return rating, rating_ratio
        else:
            return None, None

    @staticmethod
    def parse_review(review_block: BeautifulSoup) -> str:
        """
        Parses the review text from the review block.

        Args:
            review_block (BeautifulSoup): A BeautifulSoup object representing a review block.

        Returns:
            str: The review title and review text if available, otherwise ": "
        """
        review_title_element = review_block.find("a", class_="title")
        review_title = review_title_element.text.strip() if review_title_element else ""
        review_body_element = review_block.find(
            "div", class_=re.compile(r"text show-more")
        )
        review_body = review_body_element.text.strip() if review_body_element else ""
        return f"{review_title}: {review_body}"

    @staticmethod
    def parse_upvotes(review_block: BeautifulSoup) -> Tuple[int, int]:
        """
        Parses the upvotes and total votes from the review block.

        Args:
            review_block (BeautifulSoup): A BeautifulSoup object representing a review block.

        Returns:
            Tuple[int, int]: The number of upvotes and the total number of votes.
        """
        vote_element = review_block.find("div", class_="actions text-muted")
        if vote_element:
            votes = re.findall(r"\b\d+\b", vote_element.text.replace(",", ""))
            return tuple(map(int, votes))
        else:
            return (0, 0)

    @staticmethod
    def parse_permalink(review_block: BeautifulSoup) -> Optional[str]:
        """
        Parses the permalink from the review block.

        Args:
            review_block (BeautifulSoup): A BeautifulSoup object representing a review block.

        Returns:
            Optional[str]: The permalink if available, otherwise None.
        """
        permalink_element = review_block.find("a", string=re.compile("Permalink"))
        return permalink_element.get("href") if permalink_element else None

    def parse_review_block(self, review_block: BeautifulSoup) -> IMDBReview:
        """
        Parses a review block from the IMDB website and returns an IMDBReview instance.

        This method extracts various details from the review block such as date, rating, review,
        upvotes, total votes, and permalink. If an exception occurs during parsing, the method
        prints the failed review block, an error message and returns None.

        Args:
            review_block (BeautifulSoup): The review block to be parsed.

        Returns:
            IMDBReview: An instance of the IMDBReview class representing the parsed review.
            None: If an error occurs during parsing.

        """
        try:
            date = self.parse_date(review_block)
            rating, rating_ratio = self.parse_rating(review_block)
            review = self.parse_review(review_block)
            upvotes, total_votes = self.parse_upvotes(review_block)
            permalink = self.parse_permalink(review_block)
            return IMDBReview(
                date, rating, rating_ratio, review, upvotes, total_votes, permalink
            )
        except Exception as e:
            print(f"Failed to parse:\n{review_block}\nError: {e}")
            return None

    def parse_reviews(self, review_blocks: List[BeautifulSoup]) -> List[IMDBReview]:
        """
        Parses a list of review blocks into a list of IMDBReview objects, discarding any that fail to parse.

        Args:
            review_blocks (List[BeautifulSoup]): The list of BeautifulSoup objects representing the review blocks to parse.

        Returns:
            List[IMDBReview]: The list of successfully parsed reviews. If a review block fails to parse, it is excluded from this list.
        """
        reviews = []
        reviews = [
            self.parse_review_block(review_block)
            for review_block in review_blocks
            if self.parse_review_block(review_block) is not None
        ]
        return reviews
