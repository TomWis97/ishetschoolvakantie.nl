import requests
import datetime
import locale
import json
import re
from bs4 import BeautifulSoup

class HolidayParser:
    def __init__(self, url):
        self.url = url
        self.holidays = self.parse_webpage()
        
    def parse_webpage(self):
        page = requests.get(self.url).text
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.find_all('table')[0]
        regions = [ x.text for x in table.find_all('th', scope='col') ]
        self.regions = regions
        holidays = []
        for row in table.tbody.find_all('tr'):
            holiday_name = row.th.p.text
            index = 0
            region_dates = {}
            earliest_start = None
            latest_end = None
            for column in row.find_all('td'):
                start, end = self.parse_column(column.text)
                if earliest_start == None or start < earliest_start:
                    earliest_start = start
                if latest_end == None or end > latest_end:
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

    def parse_column(self, text):
        start_string, end_string = text.split(' t/m ')
        end_date = datetime.datetime.strptime(end_string, '%d %B %Y')
        if len(start_string.split(' ')) < 3:
            start_date = datetime.datetime.strptime(
                start_string + ' ' + str(end_date.year),
                '%d %B %Y')
        else:
            start_date = datetime.datetime.strptime(start_string, '%d %B %Y')
        return start_date, end_date

    def parse_adviceweek(self, soup):
        advice_text = soup.find('h2', string="Adviesweek meivakantie").find_next_sibling('p').text
        start, end = self.parse_column(re.search(r'(?<=adviesdata: ).*?(?=\.)', advice_text).group())
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
    h = HolidayParser('https://www.rijksoverheid.nl/onderwerpen/schoolvakanties/overzicht-schoolvakanties-per-schooljaar/overzicht-schoolvakanties-2024-2025')
    print(h.holidays)

