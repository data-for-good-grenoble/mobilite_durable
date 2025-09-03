import scrapy


class TransitSpider(scrapy.Spider):
    name = "transit"
    start_urls = [
        "https://transitapp.com/fr/region/grenoble/ara-cars-r%C3%A9gion-is%C3%A8re-scolaire",
    ]

    def parse(self, response):
        # Search lines with the class "padding-route-image"
        bus_line_paths = response.xpath('//div[contains(@class, "padding-route-image")]')
        for bus_line_path in bus_line_paths:
            # Extract texts form the containing span
            texts = bus_line_path.xpath("..//text()").extract()
            bus_line_number = texts[0] if len(texts) > 0 else ""
            bus_line_name = texts[1] if len(texts) > 1 else ""

            # The link is included in the parent of the parent of the parent
            bus_line_url = bus_line_path.xpath("../../..//@href").get()
            if bus_line_url:
                yield response.follow(
                    f"https://transitapp.com/{bus_line_url}",
                    callback=self.parse_bus_line,
                    meta={
                        "bus_line_number": bus_line_number,
                        "bus_line_name": bus_line_name,
                        "bus_line_url": bus_line_url,
                    },
                )

    def parse_bus_line(self, response):
        bus_line_number = response.meta.get("bus_line_number")
        bus_line_name = response.meta.get("bus_line_name")

        # Search stops with color-black-pearl class
        stop_names = response.xpath(
            '//span[contains(@class, "color-black-pearl")]//text()'
        ).extract()
        yield {
            "bus_line_number": bus_line_number,
            "bus_line_name": bus_line_name,
            "stop_names": stop_names,
        }
