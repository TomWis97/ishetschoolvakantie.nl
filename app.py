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

class HolidayExtension:
    def __init__(self, source, app=None):
        self.h = HolidayChecker(HolidayParser(source).holidays)
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.extensions['holiday_instance'] = self.h

@app.route('/')
def serve_index():
    """
    Show main page.
    """
    if app.config['force_date']:
        return render_template("index.html",
                               current_holiday=app.extensions['holiday_instance'].current_holiday(app.config['force_date']),
                               next_holiday=app.extensions['holiday_instance'].next_holiday(app.config['force_date']))
    else:
        return render_template("index.html",
                               current_holiday=app.extensions['holiday_instance'].current_holiday(),
                               next_holiday=app.extensions['holiday_instance'].next_holiday())


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
    if app.config['force_date']:
        current = app.extensions['holiday_instance'].current_holiday(app.config['force_date'])
    else:
        current = app.extensions['holiday_instance'].current_holiday()
    normalized_holidays = []
    for holiday in current:
        normalized_holidays.append(
                normalize_holiday(holiday))
    return normalized_holidays


@app.route('/api/v1/next')
def serve_next():
    if app.config['force_date']:
        return normalize_holiday(app.extensions['holiday_instance'].next_holiday(app.config['force_date']))
    else:
        return normalize_holiday(app.extensions['holiday_instance'].next_holiday())


@app.route('/api')
def serve_api_docs():
    return app.send_static_file('apidoc.html')


def create_app():
    setup_app(app)
    if os.getenv('BEHIND_REVERSE_PROXY'):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)
    return app

def setup_app(app):
    """
    Fetches and interprets source information.
    """
    source = os.getenv('DATA_URL')
    if not source:
        source = None

    # Force a date to be displayed (for debugging).
    force_date_value = os.getenv('FORCE_DATE')
    if force_date_value:
        force_date = datetime.datetime.fromisoformat(force_date_value)
    else:
        force_date = None
    app.config['force_date'] = force_date

    holiday_extension = HolidayExtension(source, app)


create_app()
