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

WAIT_TIME_LOAD = 10
WAIT_TIME_CLICK = 20
MIN_SLEEP = 1
MAX_SLEEP = 10


class Website(ABC, Generic[ScrapedReviewType, ParsedReviewType]):
    """
    A base class for specific website scrapers. This class is expected to be
    subclassed with methods implemented for each specific website's HTML structure.
    """

    @staticmethod
    def initiate_chrome(headless_mode: bool) -> Chrome:
        """
        Initializes the Chrome driver with the given mode.

        Args:
            headless_mode (bool): A flag indicating whether to initiate the Chrome
                                  driver in headless mode.

        Returns:
            driver (Chrome): The initialized Chrome driver.
        """
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
        """
        Loads a web element in the provided driver using the locator.

        Args:
            driver (Chrome): The Chrome driver to use for loading the element.
            locator (Tuple[By, str]): The locator for the element to be loaded.

        Raises:
            TimeoutException: If the element was not loaded within the defined wait time.
            NoSuchElementException: If the element could not be found.
        """
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

    @staticmethod
    def load_next(driver: Chrome, locator: Tuple[By, str]):
        """
        Loads the next page of a multi-page website.

        Args:
            driver (Chrome): The Chrome driver to use for loading the next page.
            locator (Tuple[By, str]): The locator for the 'next' button.

        Raises:
            TimeoutException: If the next page was not loaded within the defined wait time.
            NoSuchElementException, ElementNotInteractableException: If the 'next' button could not be found or interacted with.
        """
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

    @abstractmethod
    def fetch_reviews(self, url: str) -> List[ScrapedReviewType]:
        """
        Fetches review data from the given URL. This is an abstract method that must
        be implemented in each subclass.

        Args:
            url (str): The URL to scrape reviews from.

        Returns:
            List[ScrapedReviewType]: A list of scraped review data.
        """
        pass

    @abstractmethod
    def parse_reviews(
        self, review_blocks: List[ScrapedReviewType]
    ) -> List[ParsedReviewType]:
        """
        Parses a list of scraped review data blocks. This is an abstract method that
        must be implemented in each subclass.

        Args:
            review_blocks (List[ScrapedReviewType]): The list of scraped review data blocks to parse.

        Returns:
            List[ParsedReviewType]: A list of parsed review data.
        """
        pass
