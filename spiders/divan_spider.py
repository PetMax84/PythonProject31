import re
from urllib.parse import urljoin
import scrapy
from w3lib.url import url_query_cleaner

class DivanLightingSpider(scrapy.Spider):
    name = "divan_lighting"
    allowed_domains = ["divan.ru"]
    start_urls = ["https://www.divan.ru/category/svet"]

    custom_settings = {
        "DOWNLOAD_DELAY": 0.5,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
        "AUTOTHROTTLE_ENABLED": True,
        "FEED_FORMAT": "csv",
        "FEED_URI": "results.csv",
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    product_link_pattern = re.compile(r'/product/')
    pagination_pattern = re.compile(r'(/category/.+page-\d+)|([?&]page=\d+)')
    price_rx = re.compile(r'(\d[\d\s\u00A0]*\d)\s*(руб|₽)', flags=re.IGNORECASE)

    def parse(self, response):
        for href in response.css('a::attr(href)').getall():
            if href and self.product_link_pattern.search(href):
                absolute = urljoin(response.url, href)
                # Исправлено: убран remove_query
                absolute = url_query_cleaner(absolute)
                yield scrapy.Request(absolute, callback=self.parse_product)

        for href in response.css('a::attr(href)').getall():
            if href and self.pagination_pattern.search(href):
                absolute = urljoin(response.url, href)
                yield scrapy.Request(absolute, callback=self.parse)

    def parse_product(self, response):
        name = response.css('h1::text').get() or response.css('[itemprop=name]::text').get()
        if name:
            name = name.strip()

        price = None
        for sel in [
            '[itemprop=price]::attr(content)',
            '.price::text',
            '.product-price::text',
            '.product__price::text',
            '.price-new::text',
            '.price-value::text',
            '.catalog-price__value::text',
        ]:
            text = response.css(sel).get()
            if text:
                text = text.strip()
                m = self.price_rx.search(text)
                if m:
                    price = m.group(1).replace('\xa0', ' ').strip()
                    break
                digits = re.sub(r'[^0-9]', '', text)
                if digits:
                    price = digits
                    break

        if not price:
            m = self.price_rx.search(response.text)
            if m:
                price = m.group(1).replace('\xa0', ' ').strip()

        yield {
            "name": name,
            "price": price,
            "url": response.url,
        }
