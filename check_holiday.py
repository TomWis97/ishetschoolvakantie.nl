from fetch_info import HolidayParser
import locale
import datetime

class HolidayChecker:
    def __init__(self, holidays):
        self.holidays = holidays
    
    def current_holiday(self, now=datetime.datetime.now()):
        current_holidays = []
        for holiday in self.holidays:
            if holiday['nationwide']['start'] < now and holiday['nationwide']['end'] > now:
                    current_holidays.append(holiday)
        return current_holidays

if __name__ == "__main__":
    locale.setlocale(locale.LC_TIME, ('nl', 'UTF-8'))
    holidays = HolidayParser('https://www.rijksoverheid.nl/onderwerpen/schoolvakanties/overzicht-schoolvakanties-per-schooljaar/overzicht-schoolvakanties-2024-2025')
    h = HolidayChecker(holidays.holidays)
    print(h.current_holiday(now=datetime.datetime(day=15,month=8,year=2025)))
    print(h.current_holiday())

