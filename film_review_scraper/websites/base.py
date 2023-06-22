import random
import logging
from time import sleep
from abc import ABC, abstractmethod
from typing import List, Tuple, TypeVar, Generic
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import element_to_be_clickable
from selenium.common.exceptions import NoSuchElementException, TimeoutException

logging.basicConfig(level=logging.INFO)

ScrapedReviewType = TypeVar('ScrapedReviewType')
ParsedReviewType = TypeVar('ParsedReviewType')

MIN_SLEEP = 1
MAX_SLEEP = 10

class Website(ABC, Generic[ScrapedReviewType, ParsedReviewType]):

    @staticmethod
    def remove_duplicates(parsed_reviews: List[ParsedReviewType]) -> List[ParsedReviewType]:
        pass
    
    @staticmethod
    def load_next(driver: Chrome, locator: Tuple[By, str]):
        try:
            WebDriverWait(driver, 10).until(element_to_be_clickable(locator))
            load_more_button = driver.find_element(*locator)
            sleep_time = random.uniform(MIN_SLEEP, MAX_SLEEP)
            sleep(sleep_time)
            load_more_button.click()
        except NoSuchElementException as e:
            logging.info("No more reviews to load.")
            raise
        except TimeoutException as e:
            logging.info("Timeout occurred.")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise

    @abstractmethod
    def fetch_reviews(self, url: str) -> List[ScrapedReviewType]:
        pass

    @abstractmethod
    def parse_reviews(self, review_blocks: List[ScrapedReviewType]) -> List[ParsedReviewType]:
        pass
