import argparse
from datetime import datetime
import json
import os
import re
import time

from urllib.request import urlopen
from urllib.error import HTTPError
import bs4
import pandas as pd


def get_quotes(book_id):
    url = 'https://www.goodreads.com/work/quotes/' + book_id
    source = urlopen(url)
    soup = bs4.BeautifulSoup(source, 'html.parser')

    time.sleep(2)

    quotes = []
    for node in soup.find_all('div', {'class', 'quoteText'}):
        quotes.append({'quote':re.sub(r'[^\x00-\x7f]', r'', node.contents[0].strip('\n').strip(' ')), \
                       'author': re.sub(r'[^\x00-\x7f]', r'',node.find_all('span', {'class': 'authorOrTitle'})[0].text.strip('\n').strip(' ')), \
                       'book':re.sub(r'[^\x00-\x7f]', r'', node.find_all('a', {'class':'authorOrTitle'})[0].text.strip('\n').strip(' '))})
    return quotes

def condense_books(condensed_books_path,books_directory_path):
    books = []
    df = None
    prev = None
    print(1)
    for file_name in os.listdir(books_directory_path):
        if file_name.endswith('.json') and not file_name.startswith('.') and file_name != "all_books.json":
            print('Here')
            #_book = json.load(
            #    open(books_directory_path + '/' + file_name, 'r'))  # , encoding='utf-8', errors='ignore'))
            #books.append(_book)
            df = pd.read_json(books_directory_path + '/' + file_name)
            prev = pd.concat([df, prev])
    #condensed_books_path = args.output_directory_path + '/all_books'
    prev.to_csv(f"{condensed_books_path}.csv", index=False, encoding='utf-8')
    print(f"{condensed_books_path}.csv")
    #return books

def main():
    start_time = datetime.now()
    script_name = os.path.basename(__file__)

    parser = argparse.ArgumentParser()
    parser.add_argument('--book_ids_path', type=str)
    parser.add_argument('--output_directory_path', type=str)
    parser.add_argument('--format', type=str, action="store", default="json",
                        dest="format", choices=["json", "csv"],
                        help="set file output format")
    args = parser.parse_args()
    if not os.path.exists(args.output_directory_path):
        os.mkdir(args.output_directory_path)
    book_ids = [line.strip() for line in open(args.book_ids_path, 'r') if line.strip()]
    books_already_scraped = [file_name.replace('.json', '') for file_name in os.listdir(args.output_directory_path) if
                             file_name.endswith('.json') and not file_name.startswith('all_books')]
    books_to_scrape = [book_id for book_id in book_ids if book_id not in books_already_scraped]
    condensed_books_path = args.output_directory_path + '/' + args.book_ids_path.strip('.txt')

    for i, book_id in enumerate(books_to_scrape):
        try:
            print(str(datetime.now()) + ' ' + script_name + ': Scraping ' + book_id + '...')
            print(str(datetime.now()) + ' ' + script_name + ': #' + str(
                i + 1 + len(books_already_scraped)) + ' out of ' + str(len(book_ids)) + ' books')

            book = get_quotes(book_id)
            json.dump(book, open(args.output_directory_path + '/' + book_id + '.json', 'w'))

            print('=============================')

        except HTTPError as e:
            print(e)
            exit(0)

    condense_books(condensed_books_path, args.output_directory_path)

    print(str(
        datetime.now()) + ' ' + script_name + f':\n\n🎉 Success! All book metadata scraped. 🎉\n\nMetadata files have been output to /{args.output_directory_path}\nGoodreads scraping run time = ⏰ ' + str(
        datetime.now() - start_time) + ' ⏰')


if __name__ == '__main__':
    main()
