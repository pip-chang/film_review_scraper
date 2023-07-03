from setuptools import setup

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

setup(
    name="film_review_scraper",
    version="1.0",
    description="Scraper for film review websites",
    author="Jianghan Chang",
    author_email="jianghanchang@hotmail.com",
    url="https://github.com/pip-chang/DH-S",
    install_requires=install_requires,
    package_dir={"": "film_review_scraper"},
)
