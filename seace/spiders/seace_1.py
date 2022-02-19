import os
from datetime import datetime
from time import sleep

import scrapy
from scrapy.utils.conf import closest_scrapy_cfg
from selenium import webdriver
from selenium.common.exceptions import (
    ElementNotInteractableException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def solve_captcha(captcha: bytes) -> str:
    '''Gets a captcha as bytes and returns the solution as a string'''
    # Save captcha img each time. Just for testing
    now = datetime.now().isoformat().replace(':', '-')
    with open(f'captchas/{now}.png', 'wb') as f:
        f.write(captcha)
    return input('Solve the captcha manually and paste it here: ')


class Seace1Spider(scrapy.Spider):
    name = 'seace_1'

    def start_requests(self):
        options = webdriver.ChromeOptions()
        if not os.getenv('TEST_MODE'):
            options.add_argument('headless')
        download_path = os.path.join(os.path.dirname(closest_scrapy_cfg()), 'output')
        prefs = {'download.default_directory': download_path}
        options.add_experimental_option('prefs', prefs)
        self.driver = webdriver.Chrome(
            executable_path=ChromeDriverManager().install(), chrome_options=options
        )
        self.driver.get(
            'https://prodapp2.seace.gob.pe/seacebus-uiwd-pub/buscadorPublico/buscadorPublico.xhtml'
        )
        yield scrapy.Request(url='http://quotes.toscrape.com')

    def parse(self, response):
        # Click "Búsqueda avanzada"
        self.click_element('//fieldset/legend')
        sleep(1)  # Wait one second to load the drop down

        # Enter dates
        self.fill_date(datetime(2022, 1, 6))

        self.fill_catpcha_and_search()

        # Click export to download the file
        self.click_element('//*[@id="tbBuscador:idFormBuscarProceso:btnExportar"]')

    def get_captcha(self) -> bytes:
        captcha_img = self.driver.find_element_by_xpath(
            '//*[@id="tbBuscador:idFormBuscarProceso:captchaImg"]'
        ).screenshot_as_png
        return captcha_img

    def fill_box(self, xpath: str, input_str: str) -> None:
        '''Fills an html element with the given input data'''
        # wait = WebDriverWait(
        #     self.driver,
        #     10,
        #     # poll_frequency=1,
        #     # ignored_exceptions=[StaleElementReferenceException],
        # )
        i = 0
        # WebDriverWait doesn't seem to work properly. As a workaround we're using
        # a while True try statement
        while True:
            try:
                # box = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                box = self.driver.find_element_by_xpath(xpath)
                box.click()
                box.send_keys(input_str)
                break
            except (StaleElementReferenceException, ElementNotInteractableException):
                self.logger.debug(f'Trying to input date again. Retry: {i + 1}')
                sleep(0.1)
                i += 1

    def click_element(self, xpath: str) -> None:
        self.driver.find_element_by_xpath(xpath).click()

    def fill_date(self, date: datetime) -> None:
        for xpath in [
            '//*[@id="tbBuscador:idFormBuscarProceso:dfechaInicio_input"]',
            '//*[@id="tbBuscador:idFormBuscarProceso:dfechaFin_input"]',
        ]:
            self.fill_box(xpath, date.strftime('%d/%m/%Y'))

    def fill_catpcha_and_search(self) -> None:
        '''Solves the captcha, clicks search and retries if the captcha was incorrectly solved.'''
        while True:
            try:
                # Solve captcha
                captcha_img = self.get_captcha()
                captcha_str = solve_captcha(captcha_img)
                self.fill_box(
                    '//*[@id="tbBuscador:idFormBuscarProceso:codigoCaptcha"]',
                    captcha_str,
                )

                # Click the "Buscar" button
                self.click_element(
                    '//*[@id="tbBuscador:idFormBuscarProceso:btnBuscarSel"]'
                )

                # Checking for the "bad captcha" message box
                message_box = WebDriverWait(self.driver, 1).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="frmMesajes:gPrincipal_container"]/div')
                    )
                )
                # Close message box for next try
                ActionChains(self.driver).move_to_element(
                    message_box
                ).perform()  # Hover to make the 'x' visible
                try:
                    WebDriverWait(self.driver, 7).until(
                        EC.visibility_of_element_located(
                            (
                                By.XPATH,
                                '//*[@id="frmMesajes:gPrincipal_container"]/div/div/div[1]',
                            )
                        )
                    ).click()  # Click the 'x'
                except TimeoutException:
                    pass

                # If there is the message, try to solve captcha again
            except TimeoutException:
                # Else, the catpcha is solved and just break the infinite loop
                break
