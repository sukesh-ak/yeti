import logging
from datetime import datetime, timedelta

from core.errors import ObservableValidationError
from core.feed import Feed
from core.observables import Hostname


class DynamicDomains(Feed):

    default_values = {
        "frequency": timedelta(hours=24),
        "name": "DynamicDomains",
        "source": "http://mirror1.malwaredomains.com/files/dynamic_dns.txt",
        "description": "Malwaredomains.com Dynamic Domains list",
    }

    def update(self):
        for line in self.update_lines():
            if line.startswith("#"):
                continue

            self.analyze(line)

    def analyze(self, item):
        item = item.strip()
        logging.debug(item)
        sline = item.split()

        hostname = sline[0]

        context = {}
        context["source"] = self.name
        context["provider"] = sline[0]
        context["date_added"] = datetime.utcnow()

        try:
            hostname = Hostname.get_or_create(value=hostname)
            hostname.add_context(context, dedup_list=["date_added"])
            hostname.add_source(self.name)
            hostname.tag("dyndns")
        except ObservableValidationError:
            pass
