# -*- coding: utf-8 -*-
from unicodedata import name
import scrapy


class ToScrapeCSSSpider(scrapy.Spider):

    def __init__(self, **kwargs):
        self.name = "toscrape-css"
        super(ToScrapeCSSSpider, self).__init__(name=name, **kwargs)

        self.start_urls = [
            'http://quotes.toscrape.com/',
        ]
        self.arguments = kwargs

    def parse(self, response):
        for quote in response.css("div.quote"):
            yield {
                'text': quote.css("span.text::text").extract_first(),
                'author': quote.css("small.author::text").extract_first(),
                'tags': quote.css("div.tags > a.tag::text").extract()
            }

        next_page_url = response.css("li.next > a::attr(href)").extract_first()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))

