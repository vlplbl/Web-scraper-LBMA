print('Starting...')

import os
from time import sleep
from datetime import date
import pandas as pd
import requests
from bs4 import BeautifulSoup


date = date.today()
year = date.year
day = date.day


def get_gold_price():
    link = f'http://lbma.datanauts.co.uk/table?metal=gold&year={year}&type=daily'
    print(f'Connecting to: {link}')
    try:
        source = requests.get(link).text
        soup = BeautifulSoup(source, 'lxml')
    except:
        print("Can't find the page")

    table = soup.find('tbody')
    items = []
    try:
        print('Downloading gold prices... ')
        for item in table.find_all('td'):
            items.append(item.text)
        rows = []
        for i in range(0, len(items), 7):
            rows.append(items[i:i+7])
        return rows
    except Exception as e:
        print("Can't find the data on that page")


def get_silver_price():
    link = f'http://lbma.datanauts.co.uk/table?metal=silver&year={year}&type=daily'
    print(f'Connecting to: {link}')
    try:
        source = requests.get(link).text
        soup = BeautifulSoup(source, features="lxml")
    except:
        print("Can't find the page")

    table = soup.find('tbody')
    items = []
    try:
        print('Downloading silver prices...')
        for item in table.find_all('td'):
            items.append(item.text)
        rows = []
        for i in range(0, len(items), 4):
            rows.append(items[i:i+4])
        return rows
    except Exception as e:
        print("Can't find the data on that page")


gold = get_gold_price()
gold_frame = pd.DataFrame(
    gold, columns=['Date', 'AM', 'PM', 'AM(GBP)', 'PM(GBP)', 'AM(EUR)', 'PM(EUR)'])
gold_frame = gold_frame.iloc[:, :3]
sleep(1)
silver = get_silver_price()
silver_frame = pd.DataFrame(
    silver, columns=['Date', 'Ag', 'GBP', 'EUR'])
silver_frame = silver_frame.iloc[:, :2]
df = pd.merge(gold_frame, silver_frame, on=['Date', 'Date'])

df.to_excel('Prices.xlsx', index=False)
print('Done')
os.system('pause')