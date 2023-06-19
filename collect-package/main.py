from collect import IMDB

def main():
    config_file = '/Users/pipchang/Documents/VSC/Projects/DH-S/DH-S/data/imdb_config.txt'
    page = IMDB(config_file)
    config = page.get_config()
    page_source = page.download(page.url)
    reviews = page.parse(page_source)
    output_path = f"/Users/pipchang/Documents/VSC/Projects/DH-S/{config.get('Film')}"
    print(reviews)