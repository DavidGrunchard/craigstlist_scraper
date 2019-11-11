# Simple way to import settings for the craigslist scraper
MAX_PRICE = 1500
MIN_PRICE = 800

CRAIGSLIST_SITE = 'sandiego'
ZIP_CODE = 92127
MILES_RADIUS = 5

# searches both apartment and rooms
CATEGORIES = ['apa', 'roo']

# run every 5 minutes
FREQUENCY = 5  # minutes

EMAIL_SMTP_SERVER = 'smtp.gmail.com:465'

try:
    # add private settings like EMAIL and PASSWORD to settings.py
    from private import *
# noinspection PyBroadException
except:
    pass


