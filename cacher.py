import os
import json
import datetime

from fetch_info import HolidayParser


class HolidayCacher:
    def __init__(self, source, update=False, cache_file='./holiday_cache.json'):
        self.source = source
        self.update = update
        self.cache_file = cache_file
        if update or not os.path.isfile(cache_file):
            self.parser = HolidayParser(source)
            self.holidays = self.parser.holidays
            self.write_cache()
        else:
            self.read_cache()

    def write_cache(self):
        with open(self.cache_file, 'wt') as f:
            json.dump(self.holidays, f, default=self.serialize_datetime)

    def read_cache(self):
        with open(self.cache_file, 'rt') as f:
            self.holidays = json.load(f, object_hook=self.deserialize_datetime)

    def serialize_datetime(self, obj):
        if isinstance(obj, datetime.datetime):
            return {"__is_datetime__": True, "value": obj.isoformat()}
        raise TypeError("Type {} is not JSON serializable".format(
            type(obj)))

    def deserialize_datetime(self, obj):
        if "__is_datetime__" in obj:
            return  datetime.datetime.fromisoformat(obj['value'])
        else:
            return obj
