#!/usr/bin/env python
"""This class will incorporate the PhishingDatabase feed into yeti."""

from datetime import timedelta, datetime
import logging

from core.observables import Url
from core.feed import Feed
from core.errors import ObservableValidationError


class PhishingDatabase(Feed):
    """This class will pull the PhishingDatabase feed from github on a 12 hour interval."""

    default_values = {
        "frequency": timedelta(hours=12),
        "name": "PhishingDatabase",
        "source": "https://raw.githubusercontent.com/mitchellkrogza/Phishing.Database/master/phishing-links-NEW-today.txt",
        "description": "Phishing Domains, urls websites and threats database.",
    }

    def update(self):
        for url in self.update_lines():
            self.analyze(url)

    def analyze(self, url):
        context = {"source": self.name, "date_added": datetime.utcnow()}

        try:
            url = Url.get_or_create(value=url)
            url.add_context(context, dedup_list=["date_added"])
            url.add_source(self.name)
            url.tag(["phishing"])
            url.tag(["phishing_database"])
        except ObservableValidationError as e:
            logging.error(e)
