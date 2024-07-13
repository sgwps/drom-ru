from time import sleep
from bs4 import BeautifulSoup

import requests
import consts

def create_year_page_link(brand, year, page):
    return f'https://moscow.drom.ru/{brand}/year-{year}/all/page{page}/?distance=1000'

def get_urls_on_page(url):
    sleep(consts.DELAY)
    page = requests.get(url)
    if page.ok:
        soup = BeautifulSoup(page.content, 'html.parser')
        urls = [link for attr in soup.find_all(class_='css-1nvf6xk eojktn00')[0].find_all('a') if
                (link := attr['href']) and not 'distance' in link]
        return (urls, True)
    else:
        return ([url], False)

def write_urls(urls):
    with open(consts.URLS_DIR + "urls.csv", 'a') as f:
        for url in urls:
            f.write(url + "\n")

def write_error(error):
    with open(consts.URLS_DIR + "errors.csv", 'a') as f:
        f.write(error + '\n')

def clear_errors(error):
    open(consts.URLS_DIR + "errors.csv", "w").close()

def read_errors():
    errors = []
    with open(consts.URLS_DIR + "errors.csv", 'r') as f:
        for line in f:
            errors.append(line.strip())
    return errors

def try_get_urls_on_page(url):
    urls = get_urls_on_page(url)
    if urls[1]:
        write_urls(urls[0])
        return len(urls[0])
    else:
        write_error(urls[0][0])
        return -1

    

def first_try():
    for brand in consts.BRANDS:
        for year in range(consts.YEAR_START, consts.YEAR_END):
            page = 1
            count = 1
            while count != 0:
                count = try_get_urls_on_page(create_year_page_link(brand, year, page))
                if count != -1:
                    print(f"links for {brand}, {year}, {page} ready")
                else:
                    print(f"ERROR for {brand}, {year}, {page}")
                page += 1


def repeat():
    errors = read_errors()
    clear_errors()
    for error in errors:
        try_get_urls_on_page()
    return len(errors)


def main():
    first_try()
    errors_count = repeat()
    while errors_count != 0:
        print(f'{errors_count} errors')
        repeat()

main()