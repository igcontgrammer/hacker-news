#!/usr/bin/env python3

import subprocess
import webbrowser

from argparse import ArgumentParser
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = './templates'

@dataclass
class HackerNewsLink:
    link: str 
    title: str
    page: int

def _generate_txt(links: list[HackerNewsLink]):
    output_file = Path('./output/news.txt').resolve()
    path_url = output_file.as_uri()
    with open(output_file, 'a') as f:
        text = ''
        for link in links:
            text = text + f"""
                Título: {link.title}
                Link: {link.link}
                Página: {'Principal' if link.page == 0 else {link.page}}
                -----------------------------------------------------------------------------------
            """
        f.write(text)
    print(f'Obtención finalizada! Por favor diríjase a {path_url}')

def _generate_html(links: list[HackerNewsLink]):
    output_file = Path('./output/index.html').resolve()
    path_url = output_file.as_uri()
    loader = FileSystemLoader(TEMPLATES_DIR)
    env = Environment(loader=loader)
    template = env.get_template('index.html')

    context = {
      'title': 'Hacker News Web Scrapper',
      'items': links
    }

    html_rendered = template.render(context)

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_rendered)

            webbrowser.open_new_tab(path_url)

            # webbrowser.open_new(url)
        print(f'Reporte HTML generado con éxito! Diríjase a: ./output/index.html')
            
    except Exception as e:
        print(str(e))

def print_help():
    message = """

    Comandos disponibles:

    -p [n] donde N es el número de páginas que se desea buscar
    -f [txt|html] por defecto es .txt
    --clear para limpiar la carpeta output/ de búsquedas anteriores

    """
    print(message)

def main():

    parser = ArgumentParser()
    parser.add_argument("-p", type=int, help='El número de páginas')
    parser.add_argument("-f", type=str, help='Tipo formato, si es .txt o .html')
    parser.add_argument("--clear", action='store_true', help='Tipo formato, si es .txt o .html')
    args = parser.parse_args()

    number_of_pages = args.p
    output_format = args.f
    clear_output = args.clear

    if clear_output:
        try:
            subprocess.run(
                'rm -rf ./output/*', 
                shell=True, 
                check=True, 
                capture_output=True
            )
            print('carpeta output limpia')
            return None
        except Exception as e:
            print(str(e))
        return None

    if number_of_pages is None:
        number_of_pages = 0
    if output_format is None:
        output_format = 'txt'
    if output_format not in ['txt', 'html']:
        print_help()
        return None

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

    if output_format == 'txt':
        _generate_txt(links)
    elif output_format == 'html':
        _generate_html(links)
    else:
        print_help()
        return None
    
if __name__ == "__main__":
    main()
