from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
from pathlib import Path
from time import sleep
from bs4 import BeautifulSoup, element
from selenium import webdriver   
from selenium.webdriver.common.by import By
import re

class Website(ABC):
    @staticmethod
    def get_config(config_file: str) -> Dict[str, str]:
        config_file = Path(config_file)
        with config_file.open(mode='r') as file:
            config = {line.strip().split('\t')[0] : line.strip().split('\t')[1] for line in file.readlines()}
        return config

    @staticmethod
    def read_html_file(html_file: str) -> str:
        html_file = Path(html_file)
        with open(html_file, mode="r") as file:
            html_source = file.read()
        return html_source

    @abstractmethod
    def download(self, link: str) -> str:
        pass

    @abstractmethod
    def parse(self) -> List[Tuple]:
        pass


class IMDB(Website):
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.url = None
    
    def get_config(self) -> Dict[str, str]:
        config = super().get_config(self.config_file)
        self.url = config.get('Url')
        return config

    def download(self, url: str) -> str:
        driver = webdriver.Chrome()
        driver.get(url)
        loading = True
        while loading:
            try:
                load_more_button = driver.find_element(By.CSS_SELECTOR, "button[id='load-more-trigger']")
                load_more_button.click()
                sleep(2)
            except Exception as e:
                loading = False
                print(e)
        return driver.page_source

    @staticmethod
    def parse_review_block(review_block: element.Tag):
        date = review_block.find("span", class_="review-date").text
        review = review_block.find("div", class_=re.compile(r"text show-more")).text
        ratio = [int(num) for num in re.findall(r'\d+', review_block.find(string=re.compile(r"found this helpful")).text.strip())]
        all_vote = ratio[1]
        upvote = ratio[0]
        downvote = all_vote - upvote
        if all_vote == 0:
            like_ratio = None
        else:
            like_ratio = f"{upvote/all_vote:.2f}"
        permalink = review_block.find("a", string=re.compile("Permalink"))['href']
        return (date, review, upvote, all_vote, like_ratio, permalink)

    def parse(self, html_source: str) -> List[Tuple]:
        soup = BeautifulSoup(html_source, 'html.parser')
        review_blocks = soup.find_all("div", class_=re.compile("imdb-user-review"))
        reviews = [self.parse_review_block(review_block) for review_block in review_blocks]
        return reviews




    



