from datetime import datetime
from time import sleep

from .seace_1 import ExtraDataExtractor, Seace1Spider


class Seace2Spider(Seace1Spider):
    name = 'seace_2'

    def parse(self, response):
        extra_data_extractor = ExtraDataExtractor(self.driver)

        extra_data = extra_data_extractor.get_extra_data(
            'ADQUISICION DE SEMILLA DE AVENA FORRAJERA (AVENA SATIVA L.) VARIEDAD MANTARO 15 , CLASE NO CERTIFICADA PARA DZ - AYACUCHO',
            datetime.strptime('03/11/2021 23:48', '%d/%m/%Y %H:%M'),
            'Bien',
        )
        yield extra_data

        # Close browser after finishing the scrapping
        self.driver.close()
