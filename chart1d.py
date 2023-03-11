import pandas
import datetime
import os
import yfinance

# コンフィグ
basepath = './'
encode = 'utf-8'

def task():

    # 銘柄一覧の読み出し
    csvfile = open(f'{basepath}tickers_list.csv', 'r', encoding=encode)
    tickers_file = pandas.read_csv(csvfile, header=0, index_col=0)

    print('start:', datetime.datetime.now())
    for ticker, row in tickers_file.iterrows():
        
        try:
          folder = f'{basepath}chart1m1d'
          os.makedirs(folder, exist_ok=True) 
          chart_savename = f'{folder}/{ticker}_1m.csv'          
          chart1m = pandas.DataFrame()
          chart1m = yfinance.download(tickers=f'{ticker}.T', period='1d', interval='1m', progress=False)
          if not chart1m.empty:
            if len(chart1m)>1:
              chart1m.to_csv(chart_savename)

          folder = f'{basepath}chart5m1d'
          os.makedirs(folder, exist_ok=True) 
          chart_savename = f'{folder}/{ticker}_5m.csv'
          chart5m = pandas.DataFrame()        
          chart5m = yfinance.download(tickers=f'{ticker}.T', period='1d', interval='5m', progress=False)
          if not chart5m.empty:
            if len(chart5m)>1:
              chart5m.to_csv(chart_savename)
          
        except Exception:
          pass

    print('end:', datetime.datetime.now())
    
    
if __name__ == "__main__":
    
    os.system('cls')
    
    # pandasのprint表示の仕方を設定
    pandas.set_option('display.max_rows', None)
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.width', 1000)    
    
    task()
    