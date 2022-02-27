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
```bash
scrapy crawl seace_1 -a start_date='yyyy-mm-dd' -a end_date='yyyy-mm-dd'
```
