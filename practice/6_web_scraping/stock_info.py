"""
There is a list of most active Stocks on Yahoo Finance https://finance.yahoo.com/most-active.
You need to compose several sheets based on data about companies from this list.
To fetch data from webpage you can use requests lib. To parse html you can use beautiful soup lib or lxml.
Sheets which are needed:
1. 5 stocks with most youngest CEOs and print sheet to output. You can find CEO info in Profile tab of concrete stock.
    Sheet's fields: Name, Code, Country, Employees, CEO Name, CEO Year Born.
2. 10 stocks with best 52-Week Change. 52-Week Change placed on Statistics tab.
    Sheet's fields: Name, Code, 52-Week Change, Total Cash
3. 10 largest holds of Blackrock Inc. You can find related info on the Holders tab.
    Blackrock Inc is an investment management corporation.
    Sheet's fields: Name, Code, Shares, Date Reported, % Out, Value.
    All fields except first two should be taken from Holders tab.


Example for the first sheet (you need to use same sheet format):
==================================== 5 stocks with most youngest CEOs ===================================
| Name        | Code | Country       | Employees | CEO Name                             | CEO Year Born |
---------------------------------------------------------------------------------------------------------
| Pfizer Inc. | PFE  | United States | 78500     | Dr. Albert Bourla D.V.M., DVM, Ph.D. | 1962          |
...

About sheet format:
- sheet title should be aligned to center
- all columns should be aligned to the left
- empty line after sheet

Write at least 2 tests on your choose.
Links:
    - requests docs: https://docs.python-requests.org/en/latest/
    - beautiful soup docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    - lxml docs: https://lxml.de/
"""
import requests
from requests import Response
from bs4 import BeautifulSoup
import json
from memoization import cached


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36'


@cached
def request(url: str) -> Response:
    page = requests.get(url, headers={'User-Agent': USER_AGENT})
    return page


def scrape_main_table() -> list[dict]:
    page = request('https://finance.yahoo.com/most-active')
    soup = BeautifulSoup(page.content, 'html.parser')
    rows_data = []
    trs = soup.find('table', class_='W(100%)').find('tbody').find_all('tr')
    for tr in trs:
        row_data = {}
        tds = tr.find_all('td')
        for td in tds:
            field_name = td.get('aria-label')
            row_data[field_name] = td.get_text()
        rows_data.append(row_data)
    return rows_data


def scrape_ceo(symbol: str) -> dict:
    page = request(f'https://finance.yahoo.com/quote/{symbol}/profile/')
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find('div', class_='table-container').find('table')
    ths = table.find('thead').find('tr').find_all('th')
    column_names = [th.get_text() for th in ths]
    trs = table.find('tbody').find_all('tr')
    rows_data = []
    for tr in trs:
        tds = tr.find_all('td')
        row_data = {}
        for index, td in enumerate(tds):
            row_data[column_names[index]] = td.get_text()
        rows_data.append(row_data)
    ceos = list(filter(lambda row: 'CEO' in row['Title'], rows_data))
    return ceos[0]


def scrape_country(symbol: str) -> str:
    page = request(f'https://finance.yahoo.com/quote/{symbol}/profile/')
    soup = BeautifulSoup(page.content, 'html.parser')
    div = soup.find('div', class_='address').find_all('div')[-1]
    country = div.get_text()
    return country


def scrape_number_of_employees(symbol: str) -> int:
    page = request(f'https://finance.yahoo.com/quote/{symbol}/profile/')
    soup = BeautifulSoup(page.content, 'html.parser')
    strong = soup.find('dl', class_='company-stats').find('strong')
    if strong is None:
        return 0
    employees = int(strong.get_text().replace(',', ''))
    return employees


def scrape_sheet1_data() -> list[list[str]]:
    rows = []
    data = scrape_main_table()
    for company in data:
        symbol = company['Symbol']
        ceo = scrape_ceo(symbol)
        row = [
            company['Name'],
            symbol,
            scrape_country(symbol),
            str(scrape_number_of_employees(symbol)),
            ceo['Name'],
            ceo['Year Born']
        ]
        rows.append(row)
    return rows


class Table:
    def __init__(self, title: str, column_names: list[str], data: list[list[str]]) -> None:
        self.title = title
        self.column_names = column_names
        self.data = data

    def _render_row(widths: list[int], data: list[str]) -> str:
        padded_data = [f' {s} ' for s in data]
        aligned_data = [f'{s : <{w+2}}' for w, s in zip(widths, padded_data)]
        return f'|{"|".join(aligned_data)}|'
    
    def __str__(self) -> str:
        result = ''
        widths = []
        for index, column in enumerate(self.column_names):
            max_width = max([len(row[index]) for row in self.data] + [len(column)])
            widths.append(max_width)
        total_width = len(Table._render_row(widths, self.column_names))
        result += f'{f'_{self.title.replace(' ', '_')}_' : ^{total_width}}'.replace(' ', '=').replace('_', ' ') + '\n'
        result += Table._render_row(widths, self.column_names) + '\n'
        for row in self.data:
            result += '-' * total_width + '\n'
            result += Table._render_row(widths, row) + '\n'
        result += '-' * total_width + '\n'
        return result


class Sheet1(Table):
    def __init__(self):
        self.title = '5 stocks with most youngest CEOs'
        self.column_names = ['Name', 'Code', 'Country', 'Employees', 'CEO Name', 'CEO Year Born']
        rows = scrape_sheet1_data()
        rows = sorted(rows, key=lambda row: row[-1], reverse=True)
        rows = rows[:5]
        self.data = rows


def main():
    sheet1 = Sheet1()
    print(sheet1)


if __name__ == '__main__':
    main()
