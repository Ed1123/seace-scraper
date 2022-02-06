from datetime import datetime
from time import sleep

import scrapy
from scrapy.shell import inspect_response
from scrapy_selenium import SeleniumRequest
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def solve_captcha(captcha: bytes) -> str:
    '''Gets a captcha as bytes and returns the solution as a string'''
    return input('Solve the captcha manually and paste it here: ')


class Seace1Spider(scrapy.Spider):
    name = 'seace_1'

    def start_requests(self):
        url = 'https://prodapp2.seace.gob.pe/seacebus-uiwd-pub/buscadorPublico/buscadorPublico.xhtml'
        yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response):
        self.driver = response.request.meta['driver']

        # Wait a couple of seconds to load the website
        # sleep(5)

        # Click "Búsqueda avanzada"
        self.click_element('//fieldset/legend')
        sleep(1)  # Wait one second to load the drop down

        # Enter dates
        self.fill_date(datetime(2022, 1, 6))

        # Solve captcha
        captcha_img = self.get_captcha()
        captcha_str = solve_captcha(captcha_img)
        self.fill_box(
            '//*[@id="tbBuscador:idFormBuscarProceso:codigoCaptcha"]', captcha_str
        )

        # Click the "Buscar" button
        self.click_element('//*[@id="tbBuscador:idFormBuscarProceso:btnBuscarSel"]')

        # For testing
        # with open('captcha_test.png', 'wb') as f:
        #     f.write(captcha_img)
        self.driver.save_screenshot('website.png')

    def get_captcha(self) -> bytes:
        captcha_img = self.driver.find_element_by_xpath(
            '//*[@id="tbBuscador:idFormBuscarProceso:captchaImg"]'
        ).screenshot_as_png
        return captcha_img

    def fill_box(self, xpath: str, input_str: str) -> None:
        '''Fills an html element with the given input data'''
        wait = WebDriverWait(
            self.driver,
            10,
            poll_frequency=1,
            ignored_exceptions=[StaleElementReferenceException],
        )
        box = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        box.send_keys(input_str)

    def click_element(self, xpath: str) -> None:
        self.driver.find_element_by_xpath(xpath).click()

    def fill_date(self, date: datetime) -> None:
        for xpath in [
            '//*[@id="tbBuscador:idFormBuscarProceso:dfechaInicio_input"]',
            '//*[@id="tbBuscador:idFormBuscarProceso:dfechaFin_input"]',
        ]:
            self.fill_box(xpath, date.strftime('%d/%m/%Y'))
