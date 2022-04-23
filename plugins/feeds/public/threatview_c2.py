import logging
import re
from datetime import datetime, timedelta

from core.errors import ObservableValidationError
from core.feed import Feed
from core.observables import Hostname, Ip


class ThreatviewC2(Feed):

    default_values = {
        "frequency": timedelta(hours=13),
        "name": "ThreatviewC2",
        "source": "https://threatview.io/Downloads/High-Confidence-CobaltstrikeC2_IP_feed.txt",
        "description": "Infrastructure hosting Command & Control Servers found during Proactive Hunt by Threatview.io",
    }

    def update(self):
        resp = self._make_request(sort=False)
        lines = resp.content.decode("utf-8").split("\n")[2:-1]
        for line in lines:
            self.analyze(line)

    def analyze(self, item):
        item = item.strip()

        context = {"source": self.name, "date_added": datetime.utcnow()}

        try:
            if re.match(r"^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$", item):
                obs = Ip.get_or_create(value=item)
            elif re.match(r"^\w{1,}\.\w{2,}$", item):
                obs = Hostname.get_or_create(value=item)
            else:
                return
            obs.add_context(context)
            obs.add_source(self.name)
            obs.tag("threatview")
            obs.tag("cobalt_strike")
            obs.tag("c2")
        except ObservableValidationError as e:
            logging.error(e)
