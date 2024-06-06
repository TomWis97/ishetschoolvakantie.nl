from fetch_info import HolidayParser
import locale
import datetime


class HolidayChecker:
    def __init__(self, holidays: HolidayParser) -> None:
        self.holidays = holidays

    def current_holiday(
            self,
            now: datetime.datetime = datetime.datetime.now()) -> list:
        """
        Returns a list of current holidays. (Usually zero or
        one items. But can be 2 in case of "adviesweek".
        """
        current_holidays = []
        for holiday in self.holidays:
            if (holiday['nationwide']['start'] < now
            and holiday['nationwide']['end'] > now):
                current_holidays.append(holiday)
        return current_holidays

    def next_holiday(
            self,
            now: datetime.datetime = datetime.datetime.now()) -> dict:
        """
        Returns a dictionary containing information about the next holiday.
        """
        sorted_holidays = sorted(
                self.holidays, key=lambda d: d['nationwide']['start'])
        for holiday in sorted_holidays:
            if holiday['nationwide']['start'] > now:
                return holiday


if __name__ == "__main__":
    locale.setlocale(locale.LC_TIME, ('nl', 'UTF-8'))
    holidays = HolidayParser(
        'https://www.rijksoverheid.nl/onderwerpen/schoolvakanties/overzicht-'
        'schoolvakanties-per-schooljaar/overzicht-schoolvakanties-2023-2024')
    h = HolidayChecker(holidays.holidays)
    print(h.current_holiday(now=datetime.datetime(day=16, month=10, year=2023)))
    print(h.current_holiday())
    print(h.next_holiday())
