# pip install beautifulsoup4 lxml html5lib

import pandas as pd

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

        self.__load()
        
    
    def __load(self):
        data = pd.read_html(self.url, index_col=0)
        
        if len(data) > 4:
            list = data[4]
            
            try:
                s = list.loc['出来高', 1].replace('株', '').replace(',', '')
                self.volume = int(s)
                s = list.loc['売買代金', 1].replace('百万円', '').replace(',', '')
                self.tradingvalue = int(s) * 1000000                
                s = list.loc['VWAP', 1].replace('円', '').replace(',', '')
                self.vwap = float(s)
            
            except Exception:
                pass
            
            s = list.loc['約定回数', 1].replace('回', '').replace(',', '')
            self.tick = int(s)
            s = list.loc['時価総額', 1].replace('億円', '').replace(',', '').replace('兆', '')
            self.capitalization = int(float(s) * 100000000)
            s = list.loc['発行済株式数', 1].replace('株', '').replace(',', '')
            self.sharedunderstanding = int(s)
            
        if len(data) > 3:
            list = data[3]
            try:
                self.open = int(list.loc['始値', 1])
                self.high = int(list.loc['高値', 1])
                self.low = int(list.loc['安値', 1])
                self.close = int(list.loc['終値', 1])
                
                if self.__debug == True:
                    print("ohlc: ", self.open, ", ", self.high, ", ", self.low, ", ", self.close)
            except Exception:
                pass
            
        if len(data) <= 2:
            if self.__debug == True:
                print("false")

if __name__ == "__main__":
    
    kabutan = Kabutan(6730, True)
    kabutan = Kabutan(6731, True)
    kabutan = Kabutan(6734, True)
    kabutan = Kabutan(6736, True)
    kabutan = Kabutan(6737, True)
    kabutan = Kabutan(6740, True)
    kabutan = Kabutan(6741, True)
    kabutan = Kabutan(6742, True)
    kabutan = Kabutan(6743, True)
    kabutan = Kabutan(6744, True)
    kabutan = Kabutan(6745, True)
    kabutan = Kabutan(6748, True)
    kabutan = Kabutan(6750, True)
    kabutan = Kabutan(6752, True)
    kabutan = Kabutan(6753, True)
    kabutan = Kabutan(6754, True)
    kabutan = Kabutan(6755, True)
    kabutan = Kabutan(6757, True)
    kabutan = Kabutan(6758, True)
    kabutan = Kabutan(6762, True)
    kabutan = Kabutan(6763, True)
    kabutan = Kabutan(6768, True)
    kabutan = Kabutan(7120, True)
    
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