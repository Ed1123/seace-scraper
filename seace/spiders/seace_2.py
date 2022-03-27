import scrapy


class Seace2Spider(scrapy.Spider):
    name = 'seace_2'
    allowed_domains = ['http://quotes.toscrape.com']
    start_urls = ['http://http://quotes.toscrape.com/']

    def parse(self, response):
        pass
