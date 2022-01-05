import scrapy
from scrapy_selenium import SeleniumRequest


class Seace1Spider(scrapy.Spider):
    name = 'seace_1'

    def start_requests(self):
        url = 'https://prodapp2.seace.gob.pe/seacebus-uiwd-pub/buscadorPublico/buscadorPublico.xhtml'
        yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response: SeleniumRequest):
        driver = response.request.meta['driver']
        driver.save_screenshot('test.png')
