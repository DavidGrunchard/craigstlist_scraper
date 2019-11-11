import datetime
import json
import smtplib
import time
from email.mime.text import MIMEText
from getpass import getpass
from typing import *
from craigslist import CraigslistHousing

import settings

# For now using a simple json file is sufficient
DBFILE = 'craigslist.json'


def writejson(obj: List[str]):
    """
    writes the given object to disk (list of posting IDs)
    :param obj:
    """
    with open(DBFILE, 'w') as out:
        json.dump(obj, out, indent=4)


def loadjson() -> List[str]:
    """
    loads the previous matches from disk
    :return: list of postings IDs
    """
    try:
        with open(DBFILE) as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return []


class CraiglistScraper:
    """
    scrapes craigslist for apartment postings matching certain criterias,
    then sends email for new matches found.
    """

    def __init__(self) -> None:
        if hasattr(settings, 'PASSWORD'):
            self.password = settings.PASSWORD
        else:
            # this is only when ran locally, it does not work in docker :)
            self.password = getpass("Enter password for " + settings.EMAIL + " : ")
            # use sendMail function to validate credentials
            self.sendMail([])

        self.existing_listings = loadjson()

    def getListings(self, category='apa'):
        """
        Fetches the listings from craigslist using the settings defined in settings.py
        and the given category string (see craiglist categories).
        The craigslist site is hardcoded to sandiego but easy to refactor later.
        :param category:
        :return: list of craigslist postings matching the criterias
        """
        clh = CraigslistHousing(site=settings.CRAIGSLIST_SITE, category=category,
                                filters={'max_price': settings.MAX_PRICE,
                                         'search_distance': settings.MILES_RADIUS,
                                         'zip_code': settings.ZIP_CODE})

        # only need to fetch the last 20 for now
        # TODO get more postings on first run?
        return clh.get_results(sort_by='newest', geotagged=True, limit=1)

    def sendMail(self, items: List[Dict]):
        """
        sends emails for each item passed. Currently it uses gmail SMTP to send
        the emails. The body isn't formatted to look nice, it simply includes all the
        fields in the item. The subject is filtered to a few fields.
        :param items:
        """
        server = smtplib.SMTP_SSL(settings.EMAIL_SMTP_SERVER)
        sender = settings.EMAIL
        server.login(sender, self.password)
        subject_items = ['name', 'price', 'where']
        for item in items:
            msg = MIMEText(json.dumps(item, indent=4))
            # TODO: it currently sends an email from/to the same account
            msg['From'] = sender
            msg['To'] = sender
            msg['Subject'] = " | ".join(str(item[x]) for x in subject_items)
            server.send_message(msg)
        server.quit()

    def mainLoop(self):
        """
        main loop of the scraper. It will loop forever,
        each pass will check for new postings. The loop sleep time is configurable.
        """
        while True:
            for cat in settings.CATEGORIES:
                try:
                    # fetch new listings and exclude those already found
                    newListings = [x for x in self.getListings(cat) if x['id'] not in self.existing_listings]

                    # TODO use logging instead
                    print(f"{datetime.datetime.now()}: found {len(newListings)} new listings in '{cat}'")

                    # if there is any new listing, add to the list and send mails
                    if newListings:
                        self.existing_listings.extend(x['id'] for x in newListings)
                        self.sendMail(newListings)
                        writejson(self.existing_listings)

                except ConnectionError as c:
                    # TODO use logging instead
                    print(str(c))

            time.sleep(60 * settings.FREQUENCY)


if __name__ == "__main__":
    # Create new scraper and start scraping!
    scraper = CraiglistScraper()
    scraper.mainLoop()
