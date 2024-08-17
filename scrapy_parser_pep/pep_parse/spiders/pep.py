import scrapy
from pep_parse.items import PepParseItem


class PepSpider(scrapy.Spider):
    name = 'pep'
    start_urls = ['https://peps.python.org/']

    def parse(self, response):
        all_links = response.css('tbody tr a[href^="pep-"]')

        for link in all_links:
            yield response.follow(
                link, callback=self.parse_pep
            )

    def parse_pep(self, response):
        title = response.css(
            'h1.page-title::text'
        ).get().strip().replace(' - ', ' ').split(' ', 2)

        number = title[1]
        name = title[2].lstrip('– ').strip()

        status = (
            response.css('dt:contains("Status") + dd').css('abbr::text').get()
        )

        data = {
            'number': number,
            'name': name,
            'status': status,
        }

        yield PepParseItem(data)
