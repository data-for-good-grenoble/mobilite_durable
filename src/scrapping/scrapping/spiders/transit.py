""" Scrapy spider to scrape bus line information from Transit App website.

Author: Nicolas Grosjean

Reference: https://github.com/data-for-good-grenoble/mobilite_durable/issues/54
"""


import scrapy
from scrapy.http import Response


class TransitSpider(scrapy.Spider):
    name = "transit"
    start_urls = [
        "https://transitapp.com/fr/region/grenoble/ara-cars-r%C3%A9gion-is%C3%A8re-scolaire",
    ]
    processing_bus_line_number = 0
    total_bus_line_number = 0

    def parse(self, response: Response):
        # Search lines with the class "padding-route-image"
        bus_line_paths = response.xpath('//div[contains(@class, "padding-route-image")]')
        self.total_bus_line_number = len(bus_line_paths)
        self.logger.info(f"Found {self.total_bus_line_number} bus lines")
        for bus_line_path in bus_line_paths:
            # Extract texts form the containing span
            texts = bus_line_path.xpath("..//text()").extract()
            bus_line_number = texts[0] if len(texts) > 0 else ""
            bus_line_name = texts[1] if len(texts) > 1 else ""

            # The link is included in the first <a> parent element
            relative_bus_line_url = bus_line_path.xpath("ancestor::a[1]//@href").get()
            if relative_bus_line_url:
                full_bus_line_url = f"https://transitapp.com/{relative_bus_line_url}"
                yield response.follow(
                    full_bus_line_url,
                    callback=self.parse_bus_line,
                    meta={
                        "bus_line_number": bus_line_number,
                        "bus_line_name": bus_line_name,
                        "bus_line_url": full_bus_line_url,
                    },
                )
            else:
                self.logger.warning(f"No URL found for bus line {bus_line_number}")
                yield {
                    "bus_line_number": bus_line_number,
                    "bus_line_name": bus_line_name,
                    "bus_line_url": "",
                    "stop_names": [],
                }

    def parse_bus_line(self, response: Response):
        self.logger.info(f"Processing bus line {self.processing_bus_line_number + 1}/{self.total_bus_line_number}")
        self.processing_bus_line_number += 1
        bus_line_number = response.meta.get("bus_line_number")
        bus_line_name = response.meta.get("bus_line_name")
        bus_line_url = response.meta.get("bus_line_url")


        # Search stops with RouteStationsList class
        stop_and_hours = response.xpath('//div[contains(@class, "RouteStationsList")]//text()').extract()
        stop_names = stop_and_hours[::2]
        yield {
            "bus_line_number": bus_line_number,
            "bus_line_name": bus_line_name,
            "bus_line_url": bus_line_url,
            "stop_names": stop_names,
        }
