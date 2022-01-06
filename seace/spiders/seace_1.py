import scrapy
from scrapy.shell import inspect_response
from scrapy_selenium import SeleniumRequest


class Seace1Spider(scrapy.Spider):
    name = 'seace_1'

    def start_requests(self):
        url = 'https://prodapp2.seace.gob.pe/seacebus-uiwd-pub/buscadorPublico/buscadorPublico.xhtml'
        yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response: SeleniumRequest):
        driver = response.request.meta['driver']
        # inspect_response(response, self)
        captcha_img = driver.find_element_by_xpath(
            '//*[@id="tbBuscador:idFormBuscarProceso:captchaImg"]'
        )
        with open('captcha_test.png', 'wb') as f:
            f.write(captcha_img.screenshot_as_png)
        driver.save_screenshot('website.png')
