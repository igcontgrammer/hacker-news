#!/usr/bin/env python3

from argparse import ArgumentParser
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from pathlib import Path

@dataclass
class HackerNewsLink:
    link: str 
    title: str
    page: int

def main():

    parser = ArgumentParser()
    parser.add_argument("-p", type=int, help='El número de páginas')
    args = parser.parse_args()

    number_of_pages = args.p

    if number_of_pages is None:
        number_of_pages = 0
    
    page_counter = 0
    links: list[HackerNewsLink] = []
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options)

    while page_counter <= number_of_pages:
        url = 'https://news.ycombinator.com/' if page_counter == 0 else f'https://news.ycombinator.com/?p={page_counter}'
        driver.get(url)
        a_elements = driver.find_elements(By.CSS_SELECTOR, '.titleline > a')

        for a in a_elements:
            text = a.text.strip()
            href = a.get_attribute('href')
            links.append(HackerNewsLink(href or '', text, page_counter))

        if number_of_pages == 0:
            break

        page_counter = page_counter + 1

    driver.quit()

    print('Guardando datos...')

    with open('./output/news.txt', 'a') as f:
        text = ''
        for link in links:
            text = text + f"""
                Título: {link.title}
                Link: {link.link}
                Página: {'Principal' if link.page == 0 else {link.page}}
                -----------------------------------------------------------------------------------
            """
        f.write(text)

    output_file = Path('./output/news.txt').resolve()
    path_url = output_file.as_uri()

    print(f'Terminado! Por favor diríjase a {path_url}')
    
if __name__ == "__main__":
    main()
