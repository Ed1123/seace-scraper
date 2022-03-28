# Seace Scraper
This is a scraper that takes data from https://prodapp2.seace.gob.pe/seacebus-uiwd-pub/buscadorPublico/buscadorPublico.xhtml following a given set of steps.

It does by using Scrapy and Selenium libraries mainly.

## Installation
Clone the repository
```bash
git clone https://github.com/Ed1123/seace-scraper.git
```

Install requirements
```bash
cd seace-scraper
pip install -r requirements.txt
```

Install Chrome
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb
```

## Usage
### Seace 1
```bash
scrapy crawl seace_1 -a start_date='yyyy-mm-dd' -a end_date='yyyy-mm-dd'
```
### Seace 2
```bash
scrapy crawl seace_2 -a filepath='parameters.csv'
```


If you want an csv output you can include "-O seace.csv" at the end of the command. Eg:
```bash
scrapy crawl seace_1 -a start_date='yyyy-mm-dd' -a end_date='yyyy-mm-dd' -O seace.csv
```

### Note
At the moment the captche needs to be solved manually in the terminal when ask for. To see the website running and the captcha use the env variable `TEST_MODE=True`.

## Output format
```json
{
    "Nombre o Sigla de la Entidad": "ORGANISMO SUPERVISOR DE LAS CONTRATACIONES DEL ESTADO",
    "Fecha y Hora de Publicacion": "01/11/2021 14:34",
    "Nomenclatura": "CONV-PROC-27-2021-OSCE CI BID-1",
    "Objeto de Contratación": "Servicio",
    "Descripción de Objeto": "CONTRATACIÓN DE CONSULTOR PARA LA EVALUACIÓN DE LA INFRAESTRUTURA ACTUAL DEL OSCE",
    "Valor Referencial / Valor Estimado": "36,000.00",
    "Moneda": "Soles",
    "cui": "2394412",
    "estado": "Contratado",
    "cronograma": {
        "Convocatoria": datetime.datetime(2021, 10, 1, 0, 0),
        "Registro de participantes(Presencial)\nSEACE": datetime.datetime(2021, 10, 6, 17, 30),
        "Presentación de propuestas(Presencial)\nSEACE": datetime.datetime(2021, 10, 7, 0, 0),
        "Otorgamiento de la Buena Pro\nSEACE": datetime.datetime(2021, 10, 12, 0, 0)
    },
    "postores": [
        "10153478428 - TORRES NEGRON JOSE ALFREDO",
        ...
    ],
    "consorcios": [
        ...
    ]
}
```
