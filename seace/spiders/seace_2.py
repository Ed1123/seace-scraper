import csv
from datetime import datetime
from typing import Iterable

from .seace_1 import ExtraDataExtractor, Seace1Spider


class Seace2Spider(Seace1Spider):
    name = 'seace_2'

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        try:
            self.filepath_parameter = self.filepath  # type: ignore
        except AttributeError:
            raise AttributeError(
                'Must include a filepath parameter (eg. "-a filepath=here/paramenters.csv").'
            )

    def read_parameters(self) -> Iterable[tuple[str, datetime, str]]:
        with open(self.filepath_parameter, newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                yield (
                    row[0],
                    datetime.strptime(row[1], '%d/%m/%Y %H:%M'),
                    row[2],
                )

    def parse(self, response):
        extra_data_extractor = ExtraDataExtractor(self.driver)

        for parameters in self.read_parameters():
            extra_data = extra_data_extractor.get_extra_data(*parameters)
            yield extra_data

        # Close browser after finishing the scrapping
        self.driver.close()
