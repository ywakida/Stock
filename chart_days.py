import pandas
import datetime
import os
import yfinance
import time
import json

# コンフィグ
# gdrivepath = '/content/drive/My Drive/stock/'
basepath = './'
encode = 'utf-8'
daily_all_folder = 'ohlc_daily_all'
per1minute_folder = 'ohlc_1minute'
per5minutes_folder = 'ohlc_5minutes'
daily_100_folder = 'ohlc_daily_100days'
 
# フォルダの作成
os.makedirs(daily_all_folder, exist_ok=True)
os.makedirs(per1minute_folder, exist_ok=True)
os.makedirs(per5minutes_folder, exist_ok=True)
os.makedirs(daily_100_folder, exist_ok=True)


def create_daily_chart_csv(ticker):
    """ 日足チャートのCSVの作成
    """  
    daily_all_filename = f'{basepath}{daily_all_folder}/{ticker}.csv'
    daily_100_filename = f'{basepath}{daily_100_folder}/{ticker}.csv'
    
    # ファイルが存在しなければ、全データをダウンロードし、ファイルを新規作成する     
    if not os.path.exists(daily_all_filename):
        
        # ダウンロードし、空データでなく、ヘッダのみでもない場合、保存する
        new_chart = yfinance.download(tickers=f'{ticker}.T', interval='1d', period='max', progress=False)
        new_chart.columns = new_chart.columns.get_level_values(0)
        if not new_chart.empty: # 空データでない
            if len(new_chart) > 1: # ヘッダのみでない                
                new_chart.to_csv(daily_all_filename, header=True) # 保存
                print(f'{daily_all_filename} is created.')
                
    # ファイルが存在する場合は、既存のファイルに新しいデータを追加更新する
    else:
        # csvファイルを読み取り、最新日付を取得する
        daily_chart =  pandas.read_csv(daily_all_filename, index_col=0, parse_dates=True)
        # print(daily_chart)
        # daily_chart.index = pandas.to_datetime(daily_chart.index)
        
        # ファイルにデータがある場合は、ファイル内の最新日付から本日までのデータを追加更新を実施する
        if len(daily_chart) > 1:
            last_date = daily_chart.index[-1].date()
            # csvファイルの最新日付の翌日から本日までのデータを取得する
            today = datetime.date.today()
            delta_date = today - last_date
            delta_days = delta_date.days
                      
            update_chart = pandas.DataFrame()        
            try:
                # update_chart = yfinance.download(tickers=f'{ticker}.T', period=f'{delta_days}d', interval='1d', progress=False)
                # if delta_days < 5:
                #     update_chart = yfinance.download(tickers=f'{ticker}.T', interval='1d', period=f'5d', progress=False)
                # elif delta_days < 20:
                #     update_chart = yfinance.download(tickers=f'{ticker}.T', interval='1d', period=f'1mo', progress=False)
                # elif delta_days < 60:
                #     update_chart = yfinance.download(tickers=f'{ticker}.T', interval='1d', period=f'3mo', progress=False)
                # else:
                #     update_chart = yfinance.download(tickers=f'{ticker}.T', interval='1d', period=f'1y', progress=False)


                update_chart = yfinance.download(tickers=f'{ticker}.T', interval='1d', period=f'5d', progress=False)
                update_chart.columns = update_chart.columns.get_level_values(0)
                
                # update_chart = yfinance.download(tickers=f'{ticker}.T', interval='1d', period=f'max', progress=False)
            except Exception:
                pass
            
          # update_chart = update_chart[:-1] # 末尾行は削除        
            if not update_chart.empty:
                if len(update_chart) > 1:  
                    daily_chart = pandas.concat([daily_chart, update_chart], sort=True)
                    # daily_chart.drop_duplicates(keep='last', inplace=True) # 重複があれば最新で更新する
                    daily_chart = daily_chart[~daily_chart.index.duplicated(keep='last')] # 日付に重複があれば最新で更新する
                    daily_chart.sort_index(inplace=True)
                    daily_chart.to_csv(daily_all_filename, header=True) # 保存
                    daily_chart.tail(100).to_csv(daily_100_filename, header=True) # 保存
                    
                    print(f"{daily_all_filename} and {daily_100_filename} is updated")
                    # print(f"{daily_all_filename} is updated {delta_days} days")

        else:
        #   daily_chart = yfinance.download(tickers=f'{ticker}.T', period='max', progress=False)
        #   daily_chart.to_csv(file_name, header=True) # 保存
            print(f'{daily_all_filename} is incorrect.')
                
def update_ohlc_1day():
    """ 
    """
    tickers_file = pandas.read_csv('tickers_list.csv', header=0, index_col=0)

    os.makedirs(daily_all_folder, exist_ok=True) 
    
    for ticker, row in tickers_file.iterrows():
        
        create_daily_chart_csv(ticker)


def save_online_ohlc(ticker, interval, period, folder):
    """ OHLCデータをオンラインから入手する
    """    
    save_filename = f'{folder}/{ticker}.csv'          
    ohlc = pandas.DataFrame()
    try:
        retry = False
        ohlc = yfinance.download(tickers=f'{ticker}.T', interval=interval, period=period, progress=False)
        ohlc.columns = ohlc.columns.get_level_values(0)
        
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON for ticker {ticker}: {e}")
        retry = True
        
    except Exception as e:
        print(f"Failed to retrieve data for ticker {ticker}: {e}")
        
    while retry == True:
        time.sleep(3)
        try:
            retry = False
            ohlc = yfinance.download(tickers=f'{ticker}.T', interval=interval, period=period, progress=False)
            ohlc.columns = ohlc.columns.get_level_values(0)
            
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON for ticker {ticker}: {e}")
            retry = True
            
        except Exception as e:
            print(f"Failed to retrieve data for ticker {ticker}: {e}")

    if not ohlc.empty:
        if len(ohlc)>1:
            ohlc.to_csv(save_filename)

    # print(ohlc.tail(100))
    print(f"{save_filename} is updated")

def save_latest_ohlc_1minute(debug=False):
    """ 1分足のOHLCデータをオンラインから入手する
    """ 
    # 銘柄一覧の読み出し
    csvfile = open(f'{basepath}tickers_list.csv', 'r', encoding=encode)
    tickers_file = pandas.read_csv(csvfile, header=0, index_col=0)

    folder = f'{basepath}{per1minute_folder}'
    os.makedirs(folder, exist_ok=True)
    
    if debug:
        tickers_file = tickers_file.head(200)
    
    print('start:', datetime.datetime.now())
    for ticker, row in tickers_file.iterrows():
        if debug:
            print(ticker)
        
        save_online_ohlc(ticker, '1m', '5d', folder)

    print('end:', datetime.datetime.now())
    
def save_latest_ohlc_5minutes(debug=False):
    """ 5分足のOHLCデータをオンラインから入手する
    """ 
    # 銘柄一覧の読み出し
    csvfile = open(f'{basepath}tickers_list.csv', 'r', encoding=encode)
    tickers_file = pandas.read_csv(csvfile, header=0, index_col=0)

    folder = f'{basepath}{per5minutes_folder}'
    os.makedirs(folder, exist_ok=True)
    
    if debug:
        tickers_file = tickers_file.head(200)
    
    print('start:', datetime.datetime.now())
    for ticker, row in tickers_file.iterrows():
        if debug:
            print(ticker)
        
        save_online_ohlc(ticker, '5m', '1mo', folder)

    print('end:', datetime.datetime.now())    


def task(debug=False):

    # 銘柄一覧の読み出し
    csvfile = open(f'{basepath}tickers_list.csv', 'r', encoding=encode)
    tickers_file = pandas.read_csv(csvfile, header=0, index_col=0)
    
    time_daily = 0
    
    if debug:
        # tickers_file = tickers_file[tickers_file.index >= '9000']
        tickers_file = tickers_file.head(200)
    
    print('start:', datetime.datetime.now())
    for ticker, row in tickers_file.iterrows():
        if debug:
            print(ticker)
        
        ite1 = time.time()
        create_daily_chart_csv(ticker)
        ite2 = time.time()
        time.sleep(1)
        if debug:
            time_daily += ite2 - ite1
            print("time: ", round(time_daily, 3))

    print('end:', datetime.datetime.now())
    

if __name__ == "__main__":
    
    os.system('cls')

    # pandasのprint表示の仕方を設定
    pandas.set_option('display.max_rows', None)
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.width', 1000)
    
    task(False)
 
            
