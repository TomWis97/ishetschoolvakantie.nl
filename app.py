from flask import Flask, render_template, request
from werkzeug.middleware import ProxyFix
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
    return render_template("index.html", 
                           current_holiday=holiday.current_holiday(),
                           next_holiday=holiday.next_holiday())

def create_app():
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)
    return app

def setup_app():
    """
    Fetches and interprets source information.
    """
    source = os.getenv('DATA_URL')
    if not source:
        source = 'https://www.rijksoverheid.nl/onderwerpen/schoolvakanties/overzicht-'
                 'schoolvakanties-per-schooljaar/overzicht-schoolvakanties-2023-2024')
    holidays = HolidayChecker(HolidayParser(source))
    global holidays

if __name__ == "__main__":
    setup_app()
