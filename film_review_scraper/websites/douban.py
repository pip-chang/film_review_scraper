from ctypes import Union
import re
import logging
from .base import Website
from dataclasses import dataclass, field
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


@dataclass
class DoubanShortReview(DoubanReview):
    pass


@dataclass
class DoubanLongReview(DoubanReview):
    total_votes: Optional[int]
    permalink: Optional[str]
    comments: List[str]
    like_ratio: Optional[float] = field(init=False)

    def __post_init__(self) -> None:
        if self.total_votes == 0:
            self.like_ratio = None
        else:
            self.like_ratio = self.upvotes / self.total_votes


class Douban(Website):
    def fetch_short_review_blocks(self, url: str) -> List[BeautifulSoup]:
        total_review_blocks = []
        with Chrome() as driver:
            driver.get(url)

            while True:
                try:
                    page_source = BeautifulSoup(driver.page_source, "html.parser")
                    if len(page_source.find_all("div", class_="comment-item")) != 1:
                        review_blocks = page_source.find_all(
                            "div", class_="comment-item"
                        )
                        total_review_blocks += review_blocks
                        self.load_next(driver, (By.CLASS_NAME, "next"))
                    else:
                        logging.info("No more reviews to load.")
                        break
                except (NoSuchElementException, TimeoutException):
                    break
        return total_review_blocks

    @staticmethod
    def fetch_long_review_links(page_source: BeautifulSoup) -> List[str]:
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
        driver.get(review_link)
        load_more_buttons = driver.find_elements(By.CLASS_NAME, "give-me-more")

        if load_more_buttons:
            for _ in load_more_buttons:
                try:
                    self.load_next(driver, (By.CLASS_NAME, "give-me-more"))
                except (NoSuchElementException, TimeoutException):
                    break

        page_source = BeautifulSoup(driver.page_source, "html.parser")
        review_block = page_source.find("div", class_="article")
        link_tag = page_source.new_tag("review_link", href=review_link)
        review_block.append(link_tag)
        return review_block

    def fetch_long_review_blocks(self, url: str) -> List[BeautifulSoup]:
        total_review_links = []
        total_review_blocks = []
        with Chrome() as driver:
            driver.get(url)
            while True:
                try:
                    page_source = BeautifulSoup(driver.page_source, "html.parser")
                    review_links = self.fetch_long_review_links(page_source)
                    if review_links:
                        total_review_links += review_links
                        self.load_next(driver, (By.CLASS_NAME, "next"))
                    else:
                        logging.info("No more reviews to load.")
                        break
                except (NoSuchElementException, TimeoutException):
                    break
            for review_link in total_review_links:
                review_block = self.fetch_long_review_block_from_link(
                    driver, review_link
                )
                total_review_blocks.append(review_block)
        return total_review_blocks

    def fetch_reviews(
        self, url: str, review_type: Literal["short", "long"]
    ) -> List[BeautifulSoup]:
        """
        BeautifulSoup should actually be bs4.element.Tag, but its common to refer to them all as BeautifulSoup objects cause they function kind of the same
        """
        review_blocks = []
        try:
            if review_type == "short":
                review_blocks = self.fetch_short_review_blocks(url)
            elif review_type == "long":
                review_blocks = self.fetch_long_review_blocks(url)
            else:
                raise ValueError("review_type must be either 'short' or 'long'.")
        except ValueError as ve:
            logging.error(ve)
        except Exception as e:
            logging.error(f"An error occurred during fetching reviews: {e}")
        return review_blocks

    @staticmethod
    def parse_short_review_block(review_block: BeautifulSoup) -> DoubanShortReview:
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

        return DoubanShortReview(date, location, rating, rating_ratio, review, upvotes)

    @staticmethod
    def parse_long_review_block(review_block: BeautifulSoup) -> DoubanLongReview:
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
            review_title_element.text.strip() if review_title_element else None
        )
        review_element = review_block.find("div", class_="review-content clearfix")
        review = review_element.text if review_element else None
        if review_title:
            review = f"{review_title} {review}"

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

    def parse_reviews(
        self,
        review_blocks: List[BeautifulSoup],
        parse_type: Literal["short", "long"],
    ) -> List[DoubanReview]:
        reviews = []
        try:
            if parse_type == "short":
                reviews = [
                    self.parse_short_review_block(review_block)
                    for review_block in review_blocks
                ]
            elif parse_type == "long":
                reviews = [
                    self.parse_long_review_block(review_block)
                    for review_block in review_blocks
                ]
            else:
                raise ValueError("review_type must be either 'short' or 'long'.")
        except ValueError as ve:
            logging.error(ve)
        except Exception as e:
            logging.error(f"An error occurred during fetching reviews: {e}")
        return reviews
