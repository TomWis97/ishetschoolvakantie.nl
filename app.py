from flask import Flask, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import json
import locale
import datetime

from fetch_info import HolidayParser
from check_holiday import HolidayChecker

app = Flask(__name__)
locale.setlocale(locale.LC_TIME, ('nl', 'UTF-8'))


@app.route('/')
def serve_index():
    """
    Show main page.
    """
    if force_date:
        return render_template("index.html",
                               current_holiday=h.current_holiday(force_date),
                               next_holiday=h.next_holiday(force_date))
    else:
        return render_template("index.html",
                               current_holiday=h.current_holiday(),
                               next_holiday=h.next_holiday())


def normalize_holiday(holiday):
    """
    Input a holiday formatted-object and convert datetime objects
    to strings.
    """
    regions = {}
    for region, dates in holiday['regions'].items():
        regions[region] = {
                'start': dates['start'].date().isoformat(),
                'end': dates['end'].date().isoformat()}

    return {'name': holiday['name'],
            'nationwide': {
                'start': holiday['nationwide']['start'].date().isoformat(),
                'end': holiday['nationwide']['end'].date().isoformat()},
            'regions': regions}


@app.route('/api/v1/current')
def serve_current():
    if force_date:
        current = h.current_holiday(force_date)
    else:
        current = h.current_holiday()
    normalized_holidays = []
    for holiday in current:
        normalized_holidays.append(
                normalize_holiday(holiday))
    return normalized_holidays


@app.route('/api/v1/next')
def serve_next():
    if force_date:
        return normalize_holiday(h.next_holiday(force_date))
    else:
        return normalize_holiday(h.next_holiday())


@app.route('/api')
def serve_api_docs():
    return app.send_static_file('apidoc.html')


def create_app():
    setup_app()
    if os.getenv('BEHIND_REVERSE_PROXY'):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)
    return app

def setup_app():
    """
    Fetches and interprets source information.
    """
    source = os.getenv('DATA_URL')
    if not source:
        source = None

    # Force a date to be displayed (for debugging).
    global force_date
    force_date_value = os.getenv('FORCE_DATE')
    if force_date_value:
        force_date = datetime.datetime.fromisoformat(force_date_value)
    else:
        force_date = None

    global h
    h = HolidayChecker(HolidayParser(source).holidays)


setup_app()
