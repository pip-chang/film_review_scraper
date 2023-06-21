from dataclasses import dataclass
from typing import Optional, List
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
class RottenTomatoesReview:
    date: Optional[str]
    rating: Optional[str]
    rating_ratio: Optional[float]
    review: Optional[str]

class RottenTomatoes(Website):
    @staticmethod
    def click_privacy_option(driver: Chrome):
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "onetrust-button-group")))
        privacy_button = driver.find_element(By.ID, "onetrust-button-group")
        privacy_button.click()        

    @staticmethod
    def concatenate_htmls(page_sources: List[str]) -> str:
        soup = BeautifulSoup("<html></html>", "html.parser")
        for i, page_source in enumerate(page_sources):
            page_soup = BeautifulSoup(page_source, "html.parser")
            reviews_container = page_soup.find('div', class_='review_table')
            if reviews_container:
                page_wrapper = soup.new_tag("div", id=f"page{i+1}")
                page_wrapper.append(reviews_container)
                soup.html.append(page_wrapper)
        return str(soup)

    def fetch_reviews(self, url: str) -> str:
        page_sources = []
        with Chrome() as driver:
            driver.get(url)
            self.click_privacy_option(driver)
            loading = True
            while loading:
                try:
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'next')))
                    page_sources.append(driver.page_source)
                    load_more_button = driver.find_element(By.CLASS_NAME, 'next')
                    sleep(2)
                    load_more_button.click()
                except Exception as e:
                    loading = False
                    print(f"Loading completed or an error occurred: {e}")
            return self.concatenate_htmls(page_sources)

    @staticmethod
    def parse_review_block(review_block: element.Tag) -> RottenTomatoesReview:
        date_string = review_block.find("span", class_='audience-reviews__duration').text.replace(',', '')
        dt_object = datetime.strptime(date_string, "%b %d %Y")
        date = dt_object.strftime("%Y-%m-%d")
        full_stars = len(review_block.find_all("span", class_='star-display__filled'))
        half_stars = len(review_block.find_all("span", class_='star-display__half'))
        score = float(full_stars) + float(half_stars) * 0.5
        rating = f'{score}/5'
        rating_ratio = score/5
        review = review_block.find("p", class_='audience-reviews__review js-review-text').text.strip()
        return RottenTomatoesReview(date, rating, rating_ratio, review)

    def parse_html(self, html_source: str) -> List[RottenTomatoesReview]:
        soup = BeautifulSoup(html_source, 'html.parser')
        review_blocks = soup.find_all("div", class_=re.compile("audience-review-row"))
        reviews = [self.parse_review_block(review_block) for review_block in review_blocks]
        return reviews
    
        


                

