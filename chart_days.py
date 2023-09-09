import pandas
import datetime
import os
import yfinance
import time

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
        if not new_chart.empty: # 空データでない
            if len(new_chart) > 1: # ヘッダのみでない                
                new_chart.to_csv(daily_all_filename, header=True) # 保存
                print(f'{daily_all_filename} is created.')
                
    # ファイルが存在する場合は、既存のファイルに新しいデータを追加更新する
    else:
        # csvファイルを読み取り、最新日付を取得する
        daily_chart =  pandas.read_csv(daily_all_filename, index_col=0, parse_dates=True)

        # ファイルにデータがある場合は、ファイル内の最新日付から本日までのデータを追加更新を実施する
        if len(daily_chart) > 1:
            last_date = daily_chart.index[-1].date()
            # csvファイルの最新日付の翌日から本日までのデータを取得する
            today = datetime.date.today()
            delta_date = today - last_date
            delta_days = delta_date.days

            if delta_days < 5:
                delta_days = 5
          
            update_chart = pandas.DataFrame()        
            try:
                # update_chart = yfinance.download(tickers=f'{ticker}.T', period=f'{delta_days}d', interval='1d', progress=False)
                update_chart = yfinance.download(tickers=f'{ticker}.T', interval='1d', period=f'7d', progress=False)
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


def save_online_ohlc(ticker, interval, folder):
    """ OHLCデータをオンラインから入手する
    """    
    save_filename = f'{folder}/{ticker}.csv'          
    ohlc = pandas.DataFrame()
    try:
        ohlc = yfinance.download(tickers=f'{ticker}.T', interval=interval, period='7d', progress=False)
    except Exception:
        pass 

    if not ohlc.empty:
        if len(ohlc)>1:
            ohlc.to_csv(save_filename)

    # print(ohlc.tail(100))
    print(f"{save_filename} is updated")

def task(debug=False):

    # 銘柄一覧の読み出し
    csvfile = open(f'{basepath}tickers_list.csv', 'r', encoding=encode)
    tickers_file = pandas.read_csv(csvfile, header=0, index_col=0)
    
    time_daily = 0
    time_1minute = 0
    time_5minutes = 0
    
    if debug:
        tickers_file = tickers_file.head(100)
    
    print('start:', datetime.datetime.now())
    for ticker, row in tickers_file.iterrows():
        # print(ticker)
        
        ite1 = time.time()
        create_daily_chart_csv(ticker)
        ite2 = time.time()
        folder = f'{basepath}{per1minute_folder}'
        save_online_ohlc(ticker, '1m', folder)
        ite3 = time.time()
        folder = f'{basepath}{per5minutes_folder}'
        save_online_ohlc(ticker, '5m', folder)          
        ite4 = time.time()
        
        if debug:
            time_daily += ite2-ite1
            time_1minute += ite3 - ite2
            time_5minutes += ite4 - ite3

    print(round(time_daily, 3), ", ", round(time_1minute, 3), ", ", round(time_5minutes, 3))

    print('end:', datetime.datetime.now())
    

if __name__ == "__main__":
    
    os.system('cls')

    # pandasのprint表示の仕方を設定
    pandas.set_option('display.max_rows', None)
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.width', 1000)
    
    task()
 
            
