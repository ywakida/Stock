import pandas
import datetime
import os
import yfinance
import json

# コンフィグ
basepath = './'
encode = 'utf-8'
per1minute_folder = 'ohlc_1minute'
per5minutes_folder = 'ohlc_5minutes'

def save_online_ohlc(ticker, interval, period, folder):
    """ OHLCデータをオンラインから入手する
    """
    os.makedirs(folder, exist_ok=True)
    save_filename = f'{folder}/{ticker}.csv'
          
    ohlc = pandas.DataFrame()
    try:
        ohlc = yfinance.download(tickers=f'{ticker}.T', interval=interval, period=period, progress=False)
        ohlc.columns = ohlc.columns.get_level_values(0)
        
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON for ticker {ticker}: {e}")
            
    except Exception as e:
        print(f"Failed to retrieve data for ticker {ticker}: {e}")

    if not ohlc.empty:
        if len(ohlc)>1:
            ohlc.to_csv(save_filename)

    print(f"{save_filename} is updated")
    
def task(debug=False):

    # 銘柄一覧の読み出し
    csvfile = open(f'{basepath}tickers_list.csv', 'r', encoding=encode)
    tickers_file = pandas.read_csv(csvfile, header=0, index_col=0)
    
    time_daily = 0
    time_1minute = 0
    time_5minutes = 0

    print('start:', datetime.datetime.now())
    for ticker, row in tickers_file.iterrows():
        if debug:
            print(ticker)
        
        folder = f'{basepath}{per1minute_folder}'
        save_online_ohlc(ticker, '1m', '5d', folder)
        folder = f'{basepath}{per5minutes_folder}'
        save_online_ohlc(ticker, '5m', '1mo', folder)          


    print("time: ", round(time_daily, 3), ", ", round(time_1minute, 3), ", ", round(time_5minutes, 3))

    print('end:', datetime.datetime.now())
     
    
if __name__ == "__main__":
    
    os.system('cls')
    
    # pandasのprint表示の仕方を設定
    pandas.set_option('display.max_rows', None)
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.width', 1000)    
    
    task()
    
