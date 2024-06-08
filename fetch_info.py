import requests
import datetime
import locale
import json
import re
from bs4 import BeautifulSoup


class HolidayParser:
    def __init__(self, url=None) -> None:
        """
        Set-up Holiday parser object. It checks which information is available,
        dynamically generates a list of available URL's and processes those
        pages with parse_webpage().
        """
        if url is None:
            # Dynamically generate list of available URLs.
            urls = []
            for year in range(
                    datetime.datetime.now().year - 1,
                    datetime.datetime.now().year + 5):
                url_base = ('https://www.rijksoverheid.nl/onderwerpen/school'
                            'vakanties/overzicht-schoolvakanties-per-'
                            'schooljaar/overzicht-schoolvakanties-{}-{}')
                testing_year = url_base.format(year, year + 1)
                # Fetch headers; if HTTP status code is 200, page is available
                if requests.head(testing_year).status_code == 200:
                    urls.append(testing_year)
            self.urls = urls
        else:
            self.urls = [url]

        holidays = []
        for url in self.urls:
            holidays = holidays + self.parse_webpage(url)
        self.holidays = holidays

    def parse_webpage(self, url) -> dict:
        """
        Parses a webpage containing the dates with BeautifulSoup. Returns a
        list containing the holidays and dates discovered on webpage.
        """
        page = requests.get(url).text
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.find_all('table')[0]
        regions = [x.text for x in table.find_all('th', scope='col')]
        self.regions = regions
        holidays = []
        for row in table.tbody.find_all('tr'):
            # Each row contains a holiday.
            holiday_name = row.th.p.text
            index = 0
            region_dates = {}
            earliest_start = None
            latest_end = None
            for column in row.find_all('td'):
                start, end = self.parse_column(column.text)
                if earliest_start is None or start < earliest_start:
                    earliest_start = start
                if latest_end is None or end > latest_end:
                    latest_end = end
                region_dates[regions[index]] = {
                    'start': start,
                    'end': end}
                index += 1
            holidays.append({
                'name': holiday_name,
                'nationwide': {
                    'start': earliest_start,
                    'end': latest_end},
                'regions': region_dates})
        advice = self.parse_adviceweek(soup)
        holidays.append(advice)
        return holidays

    def parse_column(self, text) -> tuple:
        """
        Each column contains information about that specific region.
        """
        start_string, end_string = [x.strip() for x in text.split(' t/m ')]
        end_date = datetime.datetime.strptime(end_string, '%d %B %Y')
        if len(start_string.split(' ')) < 3:
            start_date = datetime.datetime.strptime(
                start_string + ' ' + str(end_date.year),
                '%d %B %Y')
        else:
            start_date = datetime.datetime.strptime(start_string, '%d %B %Y')
        return start_date, end_date

    def parse_adviceweek(self, soup) -> dict:
        """
        Information about the "adviesweek" is written in text. So we need to
        interpret that text.
        """
        advice_text = soup.find(
                'h2',
                string="Adviesweek meivakantie").find_next_sibling('p').text
        start, end = self.parse_column(
                re.search(r'(?<=adviesdata: ).*?(?=\.)', advice_text).group())
        holiday_name = "Adviesweek meivakantie"
        regions = {}
        for region in self.regions:
            regions[region] = {
                'start': start,
                'end': end}
        return {
            'name': holiday_name,
            'nationwide': {
                'start': start,
                'end': end},
            'regions': regions}


if __name__ == "__main__":
    locale.setlocale(locale.LC_TIME, ('nl', 'UTF-8'))
