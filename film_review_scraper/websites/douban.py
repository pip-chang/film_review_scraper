import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional, Literal

from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
)

from .base import Website


logging.basicConfig(level=logging.INFO)


@dataclass
class DoubanReview:
    """
    Data class for storing review information from Douban.

    Attributes:
        date (Optional[str]): The date the review was made in the format of "YYYY-MM-DD" (e.g. "2022-05-01").
        location (Optional[str]): The location of the reviewer.
        rating (Optional[str]): The rating given by the reviewer in the format of "rating/full_rating" (e.g. "4/5").
        rating_ratio (Optional[float]): The rating given by the user, normalized to a scale of 0 to 1.
        review (Optional[str]): The review text.
        upvotes (Optional[int]): The number of upvotes for the review.
    """

    date: Optional[str]
    location: Optional[str]
    rating: Optional[str]
    rating_ratio: Optional[float]
    review: Optional[str]
    upvotes: Optional[int]


@dataclass
class DoubanShortReview(DoubanReview):
    """
    Data class for storing short review information from Douban.

    Attributes:
        website (str): The website where the review was made.
    """

    website: str = "Douban"


@dataclass
class DoubanLongReview(DoubanReview):
    """
    Data class for storing long review information from Douban.

    Attributes:
        total_votes (Optional[int]): The total number of votes for the review.
        permalink (Optional[str]): The permanent link to the review.
        comments (List[str]): The list of comments for the review.
        like_ratio (Optional[float]): The ratio of likes for the review.
        website (str): The website where the review was made.
    """

    total_votes: Optional[int]
    permalink: Optional[str]
    comments: List[str]
    like_ratio: Optional[float] = field(init=False)
    website: str = "Douban"

    def __post_init__(self) -> None:
        """
        Initializes the like ratio for long reviews.
        """
        if self.total_votes == 0:
            self.like_ratio = None
        else:
            self.like_ratio = self.upvotes / self.total_votes


class Douban(Website):
    """
    A subclass of Website that handles scraping and parsing of Douban reviews.
    """

    def fetch_short_review_blocks(
        self, url: str, headless_mode: bool = False
    ) -> List[BeautifulSoup]:
        """
        Fetches short review blocks from the specified URL.

        Note:
            Logged-in client can scrape at most 600 short reviews from the popular section and 200 from the newest section.
            All long reviews can be scraped without logging in.

        Args:
            url (str): The URL to fetch reviews from.
            headless_mode (bool, optional): If set to True, the function will run Chrome in headless mode. Defaults to False.

        Returns:
            List[BeautifulSoup]: A list of BeautifulSoup objects, each representing a short review block.
        """
        total_review_blocks = []
        driver = self.initiate_chrome(headless_mode=headless_mode)
        driver.get(url)

        while True:
            try:
                self.load_element(driver, (By.CLASS_NAME, "comment-item"))
                page_source = BeautifulSoup(driver.page_source, "html.parser")
                if len(page_source.find_all("div", class_="comment-item")) != 1:
                    review_blocks = page_source.find_all("div", class_="comment-item")
                    total_review_blocks += review_blocks
                    self.load_next(driver, (By.CLASS_NAME, "next"))
                else:
                    logging.info("No more reviews to load.")
                    break
            except (
                TimeoutException,
                NoSuchElementException,
                ElementNotInteractableException,
            ):
                break
        driver.quit()

        return total_review_blocks

    @staticmethod
    def fetch_long_review_links(page_source: BeautifulSoup) -> List[str]:
        """
        Extract the URLs of the long reviews from the page source.

        Args:
            page_source (BeautifulSoup): A parsed page source.

        Returns:
            List[str]: A list of URLs of the long reviews. If no links are found, returns None.
        """
        review_links = None
        link_sections = page_source.find_all("h2")
        if link_sections:
            review_links = [
                link_section.a.get("href")
                for link_section in link_sections
                if link_section.a and link_section.a.get("href")
            ]
        return review_links

    def fetch_long_review_block_from_link(
        self, driver: Chrome, review_link: str
    ) -> BeautifulSoup:
        """
        Fetches the review block from the provided review link.

        Args:
            driver (Chrome): An instance of Chrome driver.
            review_link (str): A URL of the review.

        Returns:
            BeautifulSoup: A parsed long review block.
        """
        driver.get(review_link)
        load_more_buttons = []
        try:
            self.load_element(driver, (By.CLASS_NAME, "give-me-more"))
            load_more_buttons = driver.find_elements(By.CLASS_NAME, "give-me-more")
        except (TimeoutException, NoSuchElementException) as e:
            logging.info(f"No folded comments.")

        if load_more_buttons:
            for _ in load_more_buttons:
                try:
                    self.load_next(driver, (By.CLASS_NAME, "give-me-more"))
                except (
                    TimeoutException,
                    NoSuchElementException,
                    ElementNotInteractableException,
                ):
                    break

        page_source = BeautifulSoup(driver.page_source, "html.parser")
        review_block = page_source.find("div", class_="article")
        link_tag = page_source.new_tag("review_link", href=review_link)
        review_block.append(link_tag)
        return review_block

    def fetch_long_review_blocks(
        self, url: str, headless_mode: bool = False
    ) -> List[BeautifulSoup]:
        """
        Fetches all long review blocks from the provided URL.

        Args:
            url (str): The URL from where to fetch the long review blocks.
            headless_mode (bool, optional): Whether to run Chrome in headless mode. Defaults to False.

        Returns:
            List[BeautifulSoup]: A list of parsed long review blocks.
        """
        total_review_links = []
        total_review_blocks = []
        driver = self.initiate_chrome(headless_mode=headless_mode)
        driver.get(url)

        while True:
            try:
                self.load_element(driver, (By.TAG_NAME, "h2"))
                page_source = BeautifulSoup(driver.page_source, "html.parser")
                review_links = self.fetch_long_review_links(page_source)
                if review_links:
                    total_review_links += review_links
                    self.load_next(driver, (By.CLASS_NAME, "next"))
                else:
                    logging.info("No more reviews to load.")
                    break
            except (
                TimeoutException,
                NoSuchElementException,
                ElementNotInteractableException,
            ):
                break

        for review_link in total_review_links:
            review_block = self.fetch_long_review_block_from_link(driver, review_link)
            total_review_blocks.append(review_block)

        driver.quit()
        return total_review_blocks

    def fetch_reviews(
        self,
        url: str,
        review_type: Literal["short", "long"],
        headless_mode: str = False,
    ) -> List[BeautifulSoup]:
        """
        Fetches review blocks based on the specified type ('short' or 'long').

        Args:
            url (str): The URL to fetch reviews from.
            review_type (Literal["short", "long"]): The type of review to fetch ('short' or 'long').
            headless_mode (bool, optional): If set to True, the function will run Chrome in headless mode. Defaults to False.

        Returns:
            List[BeautifulSoup]: A list of BeautifulSoup objects, each representing a review block.
        """
        review_blocks = []
        try:
            if review_type == "short":
                review_blocks = self.fetch_short_review_blocks(
                    url, headless_mode=headless_mode
                )
            elif review_type == "long":
                review_blocks = self.fetch_long_review_blocks(
                    url, headless_mode=headless_mode
                )
            else:
                raise ValueError("review_type must be either 'short' or 'long'.")
        except ValueError as ve:
            logging.error(ve)
        except Exception as e:
            logging.error(f"An error occurred during fetching reviews: {e}")
        return review_blocks

    @staticmethod
    def parse_short_review_block(review_block: BeautifulSoup) -> DoubanShortReview:
        """
        Parses a short review block.

        This method extracts various details from the review block. If an exception occurs
        during parsing, the method prints  the failed review block, an error message and returns None.

        Args:
            review_block (BeautifulSoup): The short review block to be parsed.

        Returns:
            DoubanShortReview: An DoubanShortReview object containing all parsed data from the review block.
            None: If an error occurs during parsing.
        """
        try:
            date_element = review_block.find("span", class_="comment-time")
            date = date_element.text.strip().split(" ")[0] if date_element else None

            location_element = review_block.find("span", class_="comment-location")
            location = location_element.text.strip() if location_element else None

            rating_element = review_block.find(
                "span", class_=re.compile(r"allstar\d+ rating")
            )
            if rating_element:
                score = int(rating_element.get("class")[0].replace("allstar", "")[0])
                rating = f"{score}/5"
                rating_ratio = score / 5
            else:
                rating = None
                rating_ratio = None

            review_element = review_block.find("span", class_="short")
            review = review_element.text.strip() if review_element else None

            upvotes_element = review_block.find("span", class_="votes vote-count")
            upvotes = int(upvotes_element.text.strip()) if upvotes_element else None

            return DoubanShortReview(
                date, location, rating, rating_ratio, review, upvotes
            )

        except Exception as e:
            print(f"Failed to parse:\n{review_block}\nError: {e}")
            return None

    @staticmethod
    def parse_long_review_block(review_block: BeautifulSoup) -> DoubanLongReview:
        """
        Parses a long review block.

        This method extracts various details from the review block. If an exception occurs
        during parsing, the method prints the failed review block, an error message and returns None.

        Args:
            review_block (BeautifulSoup): The review block to be parsed.

        Returns:
            DoubanLongReview: An DoubanLongReview object containing all parsed data from the review block.
            None: If an error occurs during parsing.
        """
        try:
            date_element = review_block.find("span", class_="main-meta")
            date = date_element.text.split(" ")[0] if date_element else None

            location_element = review_block.find("header", class_="main-hd")
            if location_element:
                location_string = location_element.text.strip().split(" ")[-1]
                location = (
                    location_string if not re.search(r"\d", location_string) else None
                )

            rating_element = review_block.find(
                "span", class_=re.compile(r"main-title-rating")
            )
            if rating_element:
                score = int(rating_element.get("class")[0].replace("allstar", "")[0])
                rating = f"{score}/5"
                rating_ratio = score / 5
            else:
                rating = None
                rating_ratio = None

            review_title_element = review_block.find("span", property="v:summary")
            review_title = (
                review_title_element.text.strip() if review_title_element else ""
            )
            review_body_element = review_block.find(
                "div", class_="review-content clearfix"
            )
            review_body = review_body_element.text if review_body_element else ""
            review = f"{review_title}: {review_body}"

            votes_element = review_block.find("div", class_="main-bd")
            if votes_element and votes_element.get("data-ad-ext"):
                upvotes, downvotes = map(
                    int, re.findall(r"\d+", votes_element.get("data-ad-ext"))
                )
                total_votes = upvotes + downvotes
            else:
                upvotes = 0
                total_votes = 0

            permalink = review_block.find("review_link").get("href")

            comment_blocks = review_block.find_all("div", class_="item comment-item")
            comments = [
                comment_block.find("div", class_="comment-content").text
                if comment_block.find("div", class_="comment-content")
                else None
                for comment_block in comment_blocks
            ]

            return DoubanLongReview(
                date,
                location,
                rating,
                rating_ratio,
                review,
                upvotes,
                total_votes,
                permalink,
                comments,
            )
        except Exception as e:
            print(f"Failed to parse:\n{review_block}\nError: {e}")
            return None

    def parse_reviews(
        self,
        review_blocks: List[BeautifulSoup],
        parse_type: Literal["short", "long"],
    ) -> List[DoubanReview]:
        """
        Parse a list of review blocks into a list of DoubanReview objects, discarding any that fail to parse.

        This method iterates over the given review blocks and uses either the
        `parse_short_review_block` or `parse_long_review_block` method to parse the review
        depending on the given parse type. If the parse type is not 'short' or 'long', a ValueError
        is raised. If an exception occurs during parsing, the error is logged and the method
        continues with the next review block.

        Args:
            review_blocks (List[BeautifulSoup]): List of review blocks to parse.
            parse_type (Literal["short", "long"]): The type of reviews to parse.

        Returns:
            List[DoubanReview]: List of parsed reviews.

        Raises:
            ValueError: If `parse_type` is not 'short' or 'long'.
        """
        reviews = []
        try:
            if parse_type == "short":
                reviews = [
                    self.parse_short_review_block(review_block)
                    for review_block in review_blocks
                    if self.parse_short_review_block(review_block) is not None
                ]
            elif parse_type == "long":
                reviews = [
                    self.parse_long_review_block(review_block)
                    for review_block in review_blocks
                    if self.parse_long_review_block(review_block) is not None
                ]
            else:
                raise ValueError("review_type must be either 'short' or 'long'.")
        except ValueError as ve:
            logging.error(ve)
        except Exception as e:
            logging.error(f"An error occurred during fetching reviews: {e}")
        return reviews
