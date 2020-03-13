import requests
from datetime import date
import datetime
from bs4 import BeautifulSoup

urlheader = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
}

url = "https://in.investing.com/instruments/HistoricalDataAjax"

header="India VIX Historical Data"
curr_id="17942"
smlID= "2036406"
column_name='Volatility Index VIX'




class IndiaVIX():
    india_vix = float(0)

    def __init__(self):
        self.india_vix = float(0)
        pass

    def getIndiaVIX(self):
        self.__get_india_vix()

    def __get_india_vix(self):
        today = date.today()
        today = date.strftime(today, '%d/%m/%Y')
        payload = {'header': header,
                   'st_date': today, 'end_date': today,
                   'sort_col': 'date', 'action': 'historical_data',
                   'smlID': smlID, 'sort_ord': 'DESC', 'interval_sec': 'Daily', 'curr_id': curr_id}
        req = requests.post(url, headers=urlheader, data=payload)
        soup = BeautifulSoup(req.content, "lxml")
        table = soup.find('table', id="curr_table")
        split_rows = table.find_all("tr")
        rows = table.findAll('tr')
        header_text = []
        headers = rows[0]

        # add the header text to array
        for th in headers.findAll('th'):
            header_text.append(th.text)

        del header_text[2:]

        row_text_array = []
        for row in rows[1:]:
            row_text = []
            # loop through the elements
            for row_element in row.findAll(['th', 'td']):
                # append the array with the elements inner text
                row_text.append(row_element.text.replace('\n', '').strip())
            del row_text[2:]
            # append the text array to the row text array
            row_text_array.append(row_text)
        self.india_vix = float(row_text_array[0][1])
