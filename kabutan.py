# pip install beautifulsoup4 lxml html5lib

import pandas

class Kabutan():
    
    def __init__(self, ticker, debug=False):
        
        self.__debug = debug
        self.url = f'https://kabutan.jp/stock/?code={ticker}'
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
        
        print("ticker: ", self.__ticker, ",len = ", len(data))
        # print(data)
        
        if len(data) > 3:
            list = data[3]
            list.index.name = '項目'
            if self.__debug == True:
                print('OHLC:', list)
            
            if ('始値' in list.index) and ('高値' in list.index) and ('安値' in list.index) and ('終値' in list.index):
                self.open = int(list.loc['始値', 1])
                self.high = int(list.loc['高値', 1])
                self.low = int(list.loc['安値', 1])
                self.close = int(list.loc['終値', 1])
        
        if len(data) > 4:
            list = data[4]
            list.index.name = '項目'
            if self.__debug == True:
                print('出来高・売買代金:', list)
            
            if '出来高' in list.index:
                s = list.loc['出来高', 1].replace('株', '').replace(',', '')
                self.volume = int(s)     
            if '売買代金' in list.index:                
                s = list.loc['売買代金', 1].replace('百万円', '').replace(',', '')
                self.tradingvalue = int(s) * 1000000        
            if 'VWAP' in list.index:
                s = list.loc['VWAP', 1].replace('円', '').replace(',', '')
                self.vwap = float(s)    
            if '約定回数' in list.index:
                s = list.loc['約定回数', 1].replace('回', '').replace(',', '')
                self.tick = int(s)
            if '時価総額' in list.index:
                s = list.loc['時価総額', 1].replace('億円', '').replace(',', '').replace('兆', '')
                self.capitalization = int(float(s) * 100000000)
            if '発行済株式数' in list.columns:
                s = list.loc['発行済株式数', 1].replace('株', '').replace(',', '')
                self.sharedunderstanding = int(s)
            
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
    
    kabutan = Kabutan(1000, True)
    kabutan = Kabutan(1301, True)
    
    # tickers_file = pandas.read_csv('tickers_list.csv', header=0, index_col=0)

    # for ticker, row in tickers_file.iterrows():
        
    #     kabutan = Kabutan(ticker, True)
        

    # print(kabutan.sharedunderstanding)
    # print(kabutan.tradingvalue)
    # print(kabutan.tick)
    # print(kabutan.vwap)
    # print(kabutan.open)
    # print(kabutan.high)
    # print(kabutan.low)
    # print(kabutan.close)
    
    # url = 'https://kabutan.jp/stock/?code=2754'

    # data = pd.read_html(url, index_col=0)

    # print(data[0])
    # print("")
    # print(data[1])
    # print("")
    # print(data[2])
    # print("")
    # print(data[3])
    # print("")
    # print(data[4])
    # print("")
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