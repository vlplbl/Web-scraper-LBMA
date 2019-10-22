import datetime
from time import sleep
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self):
        print('Starting...')
        self.year = datetime.date.year

    def get_price(self, metal, num_cols, table_key='tbody'):
        if metal == 'copper':
            url = 'https://www.westmetall.com/en/markdaten.php?action=show_table&field=LME_Cu_cash'
        else:
            url = f'http://lbma.datanauts.co.uk/table?metal={metal}&year={self.year}&type=daily'
        print(f'Connecting to: {url}')
        try:
            source = requests.get(url).text
            soup = BeautifulSoup(source, 'lxml')
        except:
            print("Can't find the page")

        table = soup.find(table_key)
        items = []
        try:
            print(f'Downloading {metal} prices... ')
            for item in table.find_all('td'):
                items.append(item.text)
            rows = []
            for i in range(0, len(items), num_cols):
                rows.append(items[i:i+num_cols])
            return rows
        except:
            print("Can't find the data on that page")

    def create_dataframes(self):
        gold = self.get_price('gold', 7)
        gold_frame = pd.DataFrame(
            gold, columns=['Date', 'AM', 'PM', 'AM(GBP)', 'PM(GBP)', 'AM(EUR)', 'PM(EUR)'])
        gold_frame = gold_frame.iloc[:, :3]
        gold_frame['AM'] = gold_frame['AM'].astype('float64').round(decimals=4)
        gold_frame['PM'] = gold_frame['PM'].astype('float64').round(decimals=4)

        sleep(1)
        silver = self.get_price('silver', 4)
        silver_frame = pd.DataFrame(
            silver, columns=['Date', 'Ag', 'GBP', 'EUR'])
        silver_frame = silver_frame.iloc[:, :2]
        silver_frame['Ag'] = silver_frame['Ag'].astype(
            'float64').round(decimals=4)

        sleep(1)
        copper = self.get_price('copper', 4, table_key='table')
        copper_frame = pd.DataFrame(
            copper, columns=['Date', 'Cu', 'Cu_3M', 'Cu_stock'])
        copper_frame = copper_frame.iloc[:, :2]
        copper_frame.Cu = copper_frame.Cu.str.split('.')
        copper_frame.Cu = copper_frame.Cu.str.join("")
        copper_frame.Cu = copper_frame.Cu.str.replace(',', '.')
        copper_frame.Cu = copper_frame.Cu.astype('float64')
        copper_frame.Date = copper_frame.Date.str.split('.')
        copper_frame.Date = copper_frame.Date.str.join("")
        copper_frame.Date = copper_frame.Date.str.replace(" ", "-")
        copper_frame.Date = copper_frame.Date.str.replace(
            "Febuary", 'February')
        copper_frame.Date = pd.to_datetime(copper_frame.Date, errors='coerce')
        copper_frame.Date = copper_frame.Date.dt.date

        df = pd.merge(gold_frame, silver_frame, how='outer')
        df.Date = pd.to_datetime(df.Date)
        df.Date = df.Date.dt.date
        df = pd.merge(df, copper_frame, how='outer')

        with pd.ExcelWriter('Prices.xlsx', engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, freeze_panes=(1, 1))
            worksheet = writer.sheets['Sheet1']
            width = df.Date.astype(str).map(len).max()
            worksheet.set_column('A:A', width)


scraper = Scraper()
scraper.create_dataframes()
print('Done')
os.system('pause')
