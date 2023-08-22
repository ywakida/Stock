# pip install beautifulsoup4 lxml html5lib

import pandas
from lxml import html
import requests
import json
from bs4 import BeautifulSoup

class Kabutan():
    
    def __init__(self, ticker, debug=False):
        
        self.__debug = debug
        self.url = f'https://www.google.com/finance/quote/{ticker}:TYO'
        self.volume = 0 # 出来高
        self.tradingvalue = 0 # 売買代金
        self.vwap = 0.0 # VWAP
        self.tick = 0 # ティック数
        self.capitalization = 0 # 時価総額
        self.sharedunderstanding = 0 # 発行株式
        self.open = 0
        self.high = 0
        self.low = 0
        self.close = 0
        self.selling = 0.0 # 売り残
        self.purchase = 0.0 # 買い残

        self.__ticker = ticker
        self.__load()
        
    
    def __load(self):
        data = pandas.read_html(self.url, index_col=0)
        
        if self.__debug == True:
            print("ticker:", self.__ticker, ",len = ", len(data))
        # print(data)
        
        if len(data) > 3:
            list = data[3]
            list.index.name = '項目'
            if self.__debug == True:
                print('OHLC:', list)
            
            if ('始値' in list.index) and ('高値' in list.index) and ('安値' in list.index) and ('終値' in list.index):
                try:
                    self.open = int(list.loc['始値', 1])
                    self.high = int(list.loc['高値', 1])
                    self.low = int(list.loc['安値', 1])
                    self.close = int(list.loc['終値', 1])
                except ValueError:
                    print('ticker:', self.__ticker, ' OHLC値エラー')
        
        if len(data) > 4:
            list = data[4]
            list.index.name = '項目'
            if self.__debug == True:
                print('出来高・売買代金:', list)
            
            if '出来高' in list.index:
                s = list.loc['出来高', 1].replace('株', '').replace(',', '').strip()
                try:
                    self.volume = int(s)
                except ValueError:
                    print('ticker:', self.__ticker, ' 出来高なし')
            if '売買代金' in list.index:                
                s = list.loc['売買代金', 1].replace('百万円', '').replace(',', '').strip()
                try:
                    self.tradingvalue = int(s) * 1000000        
                except ValueError:
                    print('ticker:', self.__ticker, ' 売買代金なし')
            if 'VWAP' in list.index:
                s = list.loc['VWAP', 1].replace('円', '').replace(',', '').strip()
                try:
                    self.vwap = float(s)    
                except ValueError:
                    print('ticker:', self.__ticker, ' VWAPなし')
            if '約定回数' in list.index:
                s = list.loc['約定回数', 1].replace('回', '').replace(',', '').strip()
                try:
                    self.tick = int(s)
                except ValueError:
                    print('ticker:', self.__ticker, ' 約定回数なし')
            if '時価総額' in list.index:
                s = list.loc['時価総額', 1].replace('億円', '').replace(',', '').replace('兆', '').strip()
                try:
                    self.capitalization = int(float(s) * 100000000)
                except ValueError:
                    print('ticker:', self.__ticker, ' 時価総額なし')
            if '発行済株式数' in list.index:
                s = list.loc['発行済株式数', 1].replace('株', '').replace(',', '').strip()
                # print(s)
                try:
                    self.sharedunderstanding = int(s)
                except ValueError:
                    print('ticker:', self.__ticker, ' 発行済株式数なし')    
                
        if len(data) > 6:
            list = data[6]
            list.index.name = '項目'
            if self.__debug == True:
                print('信用取引:', list)
            
            if '売り残' in list.columns and '買い残' in list.columns:
                self.selling = float(list['売り残'][0])
                self.purchase = float(list['買い残'][0])
    
        if self.__debug == True:
            print("ohlc: ", self.open, ", ", self.high, ", ", self.low, ", ", self.close, ", valume:", self.volume, ", tick:", self.tick, ", 売り残:", self.selling, ", 買い残:", self.purchase)
    
        if len(data) > 8:
            list = data[8]
            list.reset_index(inplace=True)
            # print(list)
        
if __name__ == "__main__":
    import time
    import re
    # kabutan = Kabutan(1000, True)
    # kabutan = Kabutan(1401, True)
    #
    start = time.time()
    
    ticker=1934
    url = f'https://www.google.com/finance/quote/{ticker}:TYO'
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    # res.encoding = 'shift-jis'
    # res.encoding = 'utf-8'
    soup = BeautifulSoup(res.content, "lxml")
    tag = soup.find("div", class_="YMlKec fxKbKc")
    if tag != None:
        strvalue = tag.string
        strvalue = strvalue.rstrip('00')
        strvalue = re.sub(r"\D", "", strvalue)
        print(f'ticker:{ticker} - {strvalue}')
        
    else:
        print(f'ticker:{ticker}')
    
    
    # tickers_file = pandas.read_csv('tickers_list.csv', header=0, index_col=0)
    # for ticker, row in tickers_file.iterrows():
    #     url = f'https://www.google.com/finance/quote/{ticker}:TYO'
    #     res = requests.get(url)
    #     # soup = BeautifulSoup(res.content, "html.parser")
    #     soup = BeautifulSoup(res.content, "lxml")
    #     tag = soup.find("div", class_="YMlKec fxKbKc")
    #     if tag != None:
    #         print(f'ticker:{ticker} - {tag.string}')
    #     else:
    #         print(f'ticker:{ticker}')
        



    #     # for tag in soup.find_all("div", class_="YMlKec fxKbKc"):
    #     #     print(f'ticker:{ticker} - {tag.string}')
    #     #     break
        
    print(time.time() - start)
    
    # print(kabutan.sharedunderstanding)
    # print(kabutan.tradingvalue)
    # print(kabutan.tick)
    # print(kabutan.vwap)
    # print(kabutan.open)
    # print(kabutan.high)
    # print(kabutan.low)
    # print(kabutan.close)
    CURRENT_VALUE_XPATH:str = "//*[@id='yDmH0d']/c-wiz/div/div[4]/div/div/main/div[2]/div[1]/div[1]/c-wiz/div/div[1]/div/div[1]/div/div[1]/div/span/div/div"
    PREVIOUS_VALUE_XPATH:str = "//*[@id='yDmH0d']/c-wiz/div/div[4]/div/div/main/div[2]/div[2]/div/div[1]/div[2]/div"


    # print(res.content)
    # print(res.text)
    # soup = BeautifulSoup(res.content, "html.parser")
    # # print(soup.find_all("div"))
    # for tag in soup.find_all("div", class_="YMlKec fxKbKc"):
    #     print(tag.string)

    # # current values
    # current_values = lxml_parsing.xpath(CURRENT_VALUE_XPATH)
    # # previous value
    # previous_values = lxml_parsing.xpath(PREVIOUS_VALUE_XPATH)    
    
    # print(current_values)
    # print(previous_values)
    
    # data = pandas.read_html(url, index_col=0)

    # print(data[0])
    # print("")
    # print(data[1])
    # print("")
    # print(data[2])
    # print("")
    # # print(data[3])
    # # print("")
    # # print(data[4])
    # # print("")
    # print(data[5])
    # print("")
    # print(data[6])
    # print("")
    # print(data[7])
    # print("")
    # print(data[8])
    # print("")
    # print(data[9])

    # import requests, bs4
    # res = requests.get('https://kabutan.jp/stock/?code=2754')
    # res.raise_for_status()
    # soup = bs4.BeautifulSoup(res.text, "html.parser")
    # elems = soup.select('time')
    # for elem in elems:
    #     print(elem)