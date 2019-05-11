import scrapy


class TestSpider(scrapy.Spider):
    name = "test"

    start_urls = [
        'https://tel.local.ch/en/q?what=hotel&where=geneve&rid=GERW'
    ]

    def parse(self, response):
        hotels = response.xpath(
            "//div[@class='listing-container']")
        for hotel in hotels:
            full_page = hotel.xpath(
                ".//a[@class='listing-link clearfix']/@href").extract_first()

            full_page_link = response.urljoin(full_page)
            yield scrapy.Request(url=full_page_link, callback=self.parseLinks)
        next_page = response.xpath(
            "//a[@class='forward']/@href").extract_first()
        if next_page is not None:
            next_page_link = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_link, callback=self.parse)

    def parseLinks(self, response):
        item = response.xpath(
            "//h1[@class='detail-entry-title']").extract_first()
        website = response.xpath(
            "//a[@class='js-kpi-url redirect']/text()").extract_first()

        if item is not None:
            a = {
                "name": response.xpath(
                    "//h1[@class='detail-entry-title']/text()").extract_first(),
                "tel": response.xpath(
                    "//a[@class='tel text-nowrap js-kpi-call']/text()").extract_first(),

                "email": response.xpath("//a[@class='js-kpi-email']/text()").extract_first(),
                "adress": response.xpath(
                    "//span[@class='adr lead']/text()").extract_first(),
                "website": response.xpath("//a[@class='js-kpi-url redirect']/text()").extract_first(),
            }
            if website is not None:
                full_page_link = response.urljoin(website)

                yield scrapy.Request(
                    url=full_page_link, callback=self.getEmailFromWebsite, meta={"obj": a}, errback=self.errback_httpbin)
            else:
                yield {
                    "name": response.xpath(
                        "//h1[@class='detail-entry-title']/text()").extract_first(),
                    "tel": response.xpath(
                        "//a[@class='tel text-nowrap js-kpi-call']/text()").extract_first(),

                    "email": response.xpath("//a[@class='js-kpi-email']/text()").extract_first(),
                    "adress": response.xpath(
                        "//span[@class='adr lead']/text()").extract_first(),
                    "website": response.xpath("//a[@class='js-kpi-url redirect']/text()").extract_first(),
                    "possible_email": None
                }

    def getEmailFromWebsite(self, response):
        obj = response.meta.get("obj")
        obj["possible_email"] = response.xpath(
            '//body').re('([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
        yield obj

    def errback_httpbin(self, failure):
        obj = failure.request.meta.get("obj")
        yield obj
