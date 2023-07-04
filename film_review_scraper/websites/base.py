import logging
import random
from abc import ABC, abstractmethod
from time import sleep
from typing import List, Tuple, TypeVar, Generic

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    SessionNotCreatedException,
)


logging.basicConfig(level=logging.INFO)

ScrapedReviewType = TypeVar("ScrapedReviewType")
ParsedReviewType = TypeVar("ParsedReviewType")

WAIT_TIME_LOAD = 30
WAIT_TIME_CLICK = 10
MIN_SLEEP = 1
MAX_SLEEP = 10


class Website(ABC, Generic[ScrapedReviewType, ParsedReviewType]):
    @staticmethod
    def remove_duplicates(
        parsed_reviews: List[ParsedReviewType],
    ) -> List[ParsedReviewType]:
        pass

    @staticmethod
    def initiate_chrome(headless_mode: bool) -> Chrome:
        chrome_options = Options()
        if headless_mode:
            chrome_options.add_argument("--headless=new")
        try:
            driver = Chrome(options=chrome_options)
        except SessionNotCreatedException:
            print("Could not init Chrome driver - trying to fetch required version...")
            driver = Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=chrome_options,
            )
        return driver

    @staticmethod
    def load_element(driver: Chrome, locator: Tuple[By, str]):
        try:
            WebDriverWait(driver, WAIT_TIME_LOAD).until(
                EC.presence_of_element_located(locator)
            )
        except TimeoutException as e:
            logging.info("Timeout occured: no element found in time limit.")
            raise
        except NoSuchElementException as e:
            logging.info("No content found.")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise

    @staticmethod
    def load_next(driver: Chrome, locator: Tuple[By, str]):
        try:
            current_page_source = driver.page_source
            WebDriverWait(driver, WAIT_TIME_CLICK).until(
                EC.element_to_be_clickable(locator)
            )
            load_more_button = driver.find_element(*locator)
            sleep_time = random.uniform(MIN_SLEEP, MAX_SLEEP)
            sleep(sleep_time)
            load_more_button.click()
            new_page_source = driver.page_source
            if new_page_source == current_page_source:
                raise TimeoutException
        except TimeoutException as e:
            logging.info("Timeout occured: no next button found in time limit.")
            raise
        except (NoSuchElementException, ElementNotInteractableException) as e:
            logging.info("No next button found.")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise

    @abstractmethod
    def fetch_reviews(self, url: str) -> List[ScrapedReviewType]:
        pass

    @abstractmethod
    def parse_reviews(
        self, review_blocks: List[ScrapedReviewType]
    ) -> List[ParsedReviewType]:
        pass
