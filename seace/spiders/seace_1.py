import os
from dataclasses import dataclass
from datetime import datetime
from time import sleep
from typing import Optional

import pandas as pd
import scrapy
from attr import asdict
from scrapy.utils.conf import closest_scrapy_cfg
from selenium import webdriver
from selenium.common.exceptions import (
    ElementNotInteractableException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def solve_captcha(captcha: bytes) -> str:
    '''Gets a captcha as bytes and returns the solution as a string'''
    # Save captcha img each time. Just for testing
    now = datetime.now().isoformat().replace(':', '-')
    with open(f'captchas/{now}.png', 'wb') as f:
        f.write(captcha)
    return input('Solve the captcha manually and paste it here: ')


@dataclass
class ExtraData:
    cui: str
    estado: str
    fecha_registro_de_participantes: datetime
    fecha_formulación_de_consultas_y_observaciones: datetime
    fecha_absolución_de_consultas_y_observaciones: datetime
    fecha_integración_de_las_bases: datetime
    fecha_presentación_de_ofertas: datetime
    fecha_evaluación_y_calificación: datetime
    fecha_otorgamiento_de_la_buena_pro: datetime
    postores: list[Optional[str]]
    consorcios: list[Optional[str]]
    # fecha_de_cambio_de_estado: datetime
    # estado_anterior: str
    # # cambio_de
    # # cambio_a
    # fecha_de_cambio_de_postor: datetime
    # postor_anterior: str
    # # cambio_de_postor_de
    # # cambio_de_postor_a


class SeaceScraper:
    def click_search(self):
        # Click the "Buscar" button
        self.click_element('//*[@id="tbBuscador:idFormBuscarProceso:btnBuscarSel"]')

        # Waiting for the grey box window to appear and dissipate
        # Max of 10 minutes each
        grey_box = '//div[contains(@id, "blocker")]'
        WebDriverWait(self.driver, 600).until(
            EC.visibility_of_element_located((By.XPATH, grey_box))
        )
        WebDriverWait(self.driver, 600).until(
            EC.invisibility_of_element((By.XPATH, grey_box))
        )

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
                self.click_search()

                # Checking for the "bad captcha" message box. If it appears in 5 sec
                # (after the grey box dissipated), the captcha wasn't solved and the loop
                # will continue, else, it will raise a TimeoutException because the message
                # box didn't appear indicating the captcha was solved.
                message_box = WebDriverWait(self.driver, 5).until(
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
        # 1 sec for the results to finish loading
        sleep(1)

    def get_text(self, xpath: str) -> str:
        return self.driver.find_element_by_xpath(xpath).text

    def get_captcha(self) -> str:
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
                # Clear field before entering the input string
                box.clear()
                box.send_keys(input_str)
                break
            except (StaleElementReferenceException, ElementNotInteractableException):
                self.logger.debug(f'Trying to input date again. Retry: {i + 1}')
                sleep(0.5)
                i += 1

    def click_element(self, xpath: str) -> None:
        self.driver.find_element_by_xpath(xpath).click()

    def select_year(self, year: int) -> None:
        '''Clicks the dropdown and select the year'''
        self.click_element(
            '//*[@id="tbBuscador:idFormBuscarProceso:anioConvocatoria_label"]'
        )
        self.click_element(
            f'//*[@id="tbBuscador:idFormBuscarProceso:anioConvocatoria_panel"]/div/ul/li[@data-label={year}]'
        )


class Seace1Spider(scrapy.Spider, SeaceScraper):
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
        def get_column_in_row(id: int):
            return row.find_element_by_xpath(f'./td[{id}]').text

        extra_data_extractor = ExtraDataExtractor(self.driver)

        # Click "Búsqueda avanzada"
        self.click_element('//fieldset/legend')
        sleep(1)  # Wait one second to load the drop down

        for date in self.get_date_range_parameter():
            rows = self.get_data_for_a_date(date)
            for row in rows:
                data = {
                    'Nombre o Sigla de la Entidad': get_column_in_row(2),
                    'Fecha y Hora de Publicacion': get_column_in_row(3),
                    'Nomenclatura': get_column_in_row(4),
                    'Objeto de Contratación': get_column_in_row(6),
                    'Descripción de Objeto': get_column_in_row(7),
                    'Valor Referencial / Valor Estimado': get_column_in_row(10),
                    'Moneda': get_column_in_row(11),
                }
                extra_data = extra_data_extractor.get_extra_data(
                    data['Descripción de Objeto'],
                    datetime.strptime(
                        data['Fecha y Hora de Publicacion'], '%d/%m/%Y %H:%M'
                    ),
                    data['Objeto de Contratación'],
                )
                yield data | asdict(extra_data)

        # Close browser after finishing the scrapping
        self.driver.close()

    def get_date_range_parameter(self) -> pd.DatetimeIndex:
        try:
            return pd.date_range(start=self.start_date, end=self.end_date)
        except AttributeError:
            raise AttributeError('Must include parameters start_date and end_dated.')
        except ValueError:
            raise ValueError('Must provide date in the format \'YYYY-MM-DD\'.')

    def get_data_for_a_date(self, date: datetime):
        # Enter dates
        self.fill_date(date)

        self.fill_catpcha_and_search()

        # Click export to download the file
        sleep(1)
        return self.driver.find_elements_by_xpath(
            '//*[@id="tbBuscador:idFormBuscarProceso:dtProcesos_data"]/tr'
        )
        self.click_element('//*[@id="tbBuscador:idFormBuscarProceso:btnExportar"]')

    def fill_date(self, date: datetime) -> None:
        self.select_year(date.year)

        # Fill start and end date
        for xpath in [
            '//*[@id="tbBuscador:idFormBuscarProceso:dfechaInicio_input"]',
            '//*[@id="tbBuscador:idFormBuscarProceso:dfechaFin_input"]',
        ]:
            self.fill_box(xpath, date.strftime('%d/%m/%Y'))


class ExtraDataExtractor(SeaceScraper):
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def get_cui(self) -> str:
        self.click_element(
            '//*[@id="tbBuscador:idFormBuscarProceso:dtProcesos:0:graCodCUI"]'
        )
        sleep(1)
        cui = self.driver.find_elements_by_xpath(
            '//*[@id="tbBuscador:idFormBuscarProceso:dataTableCodCUI_data"]/tr/td'
        )[0].text
        # Close CUI window
        self.click_element(
            '//*[@id="tbBuscador:idFormBuscarProceso:frmListaCodigoCUI"]/div[1]/a/span'
        )
        sleep(1)
        return cui

    def select_objeto_contratación(self, objeto_contratación: str) -> None:
        '''Clicks the dropdown and select the objecto de contratación'''
        self.click_element(
            '/html/body/div[3]/div/div[1]/div[1]/div[1]/form/table[1]/tbody/tr[1]/td/table/tbody/tr[2]/td[2]/div/label'
        )
        self.click_element(
            f'/html/body/div[15]/div/ul/li[@data-label="{objeto_contratación}"]'
        )

    def get_datetime(self, xpath: str) -> datetime:
        date_text = self.driver.find_element_by_xpath(xpath).text
        if len(date_text) == 16:
            return datetime.strptime(date_text, '%d/%m/%Y %H:%M')
        elif len(date_text) == 10:
            return datetime.strptime(date_text, '%d/%m/%Y')
        else:
            raise SyntaxError(
                f'{date_text} is not in the correct format. Either dd/mm/yyyy hh:mm or dd/mm/yyyy.'
            )

    def get_postores_consorcios(
        self,
    ) -> tuple[list[Optional[str]], list[Optional[str]]]:
        postores = []
        consorcios = []
        for element in self.driver.find_elements_by_xpath(
            '//*[@id="tbFicha:idGridLstItems:0:dtParticipantes_data"]/tr/td[1]'
        ):
            if element.text[:3].isdigit():
                postores.append(element.text)
            else:
                consorcios.append(element.text)
        return postores, consorcios

    def get_extra_data(
        self, descripción_objeto: str, date: datetime, objeto_contratación: str
    ) -> ExtraData:
        '''
        Testing code:
        descripción_objeto = 'ADQUISICION DE SEMILLA DE AVENA FORRAJERA (AVENA SATIVA L.) VARIEDAD MANTARO 15 , CLASE NO CERTIFICADA PARA DZ - AYACUCHO'
        date = datetime.strptime('03/11/2021 23:48', '%d/%m/%Y %H:%M')
        objeto_contratación = 'Bien'
        extra_data_extractor = ExtraDataExtractor(self.driver)
        extra_data_extractor.get_extra_data(descripción_objeto, date, objeto_contratación)
        '''
        # Input data
        self.fill_box(
            '//*[@id="tbBuscador:idFormBuscarProceso:descripcionObjeto"]',
            descripción_objeto,
        )
        self.select_year(date.year)
        self.select_objeto_contratación(objeto_contratación)
        # May be needed to input the full date and compare the full timpestamp after searching, just for multiple results.

        self.fill_catpcha_and_search()
        # Sleep while waiting for the search to load.
        # Include in the fill_catpcha_and_search method during the optimization
        sleep(10)

        # Get CUI before entering the calendar view
        cui = self.get_cui()

        # Click calendar
        self.click_element(
            '//*[@id="tbBuscador:idFormBuscarProceso:dtProcesos:0:grafichaSel"]'
        )

        # Click "Ver listado de item"
        self.click_element('//*[@id="tbFicha:j_idt1204"]/legend')
        sleep(1)

        postores, consorcios = self.get_postores_consorcios()

        extra_data = ExtraData(
            cui=cui,
            estado=self.get_text(
                '//*[@id="tbFicha:idGridLstItems_content"]/table/tbody/tr[1]/td/table[2]/tbody/tr[2]/td[8]'
            ),
            fecha_registro_de_participantes=self.get_datetime(
                '//*[@id="tbFicha:dtCronograma_data"]/tr[2]/td[3]'
            ),
            fecha_formulación_de_consultas_y_observaciones=self.get_datetime(
                '//*[@id="tbFicha:dtCronograma_data"]/tr[3]/td[3]'
            ),
            fecha_absolución_de_consultas_y_observaciones=self.get_datetime(
                '//*[@id="tbFicha:dtCronograma_data"]/tr[4]/td[3]'
            ),
            fecha_integración_de_las_bases=self.get_datetime(
                '//*[@id="tbFicha:dtCronograma_data"]/tr[5]/td[3]'
            ),
            fecha_presentación_de_ofertas=self.get_datetime(
                '//*[@id="tbFicha:dtCronograma_data"]/tr[6]/td[3]'
            ),
            fecha_evaluación_y_calificación=self.get_datetime(
                '//*[@id="tbFicha:dtCronograma_data"]/tr[7]/td[3]'
            ),
            fecha_otorgamiento_de_la_buena_pro=self.get_datetime(
                '//*[@id="tbFicha:dtCronograma_data"]/tr[8]/td[3]'
            ),
            postores=postores,
            consorcios=consorcios,
        )

        # Click the return button to perform more searches
        self.click_element(
            '//*[@id="tbFicha:idFormFichaSeleccion"]/table[1]/tfoot/tr/td/div/button'
        )

        return extra_data
