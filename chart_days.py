import pandas
import datetime
import os
import yfinance

# コンフィグ
# gdrivepath = '/content/drive/My Drive/stock/'
basepath = './'
encode = 'utf-8'
ohlc_1day_all_folder = 'yfinance_csv'
ohlc_1minute_folder = 'ohlc_1minute'
ohlc_5minute_folder = 'ohlc_5minute'
 
def create_daily_chart_csv(folder_path, ticker):
    """ 日足チャートのCSVの作成
    """  
    file_name = f'{folder_path}/{ticker}.csv'
    
    # ファイルが存在しなければ、全データをダウンロードし、ファイルを新規作成する     
    if not os.path.exists(file_name):
        
        # ダウンロードし、空データでなく、ヘッダのみでもない場合、保存する
        new_chart = yfinance.download(tickers=f'{ticker}.T', period='max', progress=False)
        if not new_chart.empty: # 空データでない
            if len(new_chart) > 1: # ヘッダのみでない                
                new_chart.to_csv(file_name, header=True) # 保存
                print(f'{file_name} is created.')
                
    # ファイルが存在する場合は、既存のファイルに新しいデータを追加更新する
    else:
        # csvファイルを読み取り、最新日付を取得する
        daily_chart =  pandas.read_csv(file_name, index_col=0, parse_dates=True)

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
                update_chart = yfinance.download(tickers=f'{ticker}.T', period=f'{delta_days}d', interval='1d', progress=False)
            except Exception:
                pass
            
          # update_chart = update_chart[:-1] # 末尾行は削除        
            if not update_chart.empty:
                if len(update_chart) > 1:  
                    daily_chart = pandas.concat([daily_chart, update_chart], sort=True)
                    daily_chart.drop_duplicates(keep='last', inplace=True) # 重複があれば最新で更新する
                    daily_chart.to_csv(file_name, header=True) # 保存
                    print(f"{file_name} is updated {delta_days} days")

        else:
        #   daily_chart = yfinance.download(tickers=f'{ticker}.T', period='max', progress=False)
        #   daily_chart.to_csv(file_name, header=True) # 保存
            print(f'{file_name} is incorrect.')
                
def update_ohlc_1day():
    tickers_file = pandas.read_csv('tickers_list.csv', header=0, index_col=0)

    os.makedirs(ohlc_1day_all_folder, exist_ok=True) 
    
    for ticker, row in tickers_file.iterrows():
        
        create_daily_chart_csv(ohlc_1day_all_folder, ticker)


def task():

    # 銘柄一覧の読み出し
    csvfile = open(f'{basepath}tickers_list.csv', 'r', encoding=encode)
    tickers_file = pandas.read_csv(csvfile, header=0, index_col=0)
    print('start:', datetime.datetime.now())
    for ticker, row in tickers_file.iterrows():
        
        folder = f'{basepath}{ohlc_1minute_folder}'
        os.makedirs(folder, exist_ok=True)
        chart_savename = f'{folder}/{ticker}.csv'          
        chart1m = pandas.DataFrame()
        try:
            chart1m = yfinance.download(tickers=f'{ticker}.T', period='5d', interval='1m', progress=False)
        except Exception:
            pass 
        
        if not chart1m.empty:
            if len(chart1m)>1:
                chart1m.to_csv(chart_savename)

        folder = f'{basepath}{ohlc_5minute_folder}'
        os.makedirs(folder, exist_ok=True) 
        chart_savename = f'{folder}/{ticker}.csv'
        chart5m = pandas.DataFrame()        
        try:
            chart5m = yfinance.download(tickers=f'{ticker}.T', period='5d', interval='5m', progress=False)
        except Exception:
            pass
        
        if not chart5m.empty:
          if len(chart5m)>1:
            chart5m.to_csv(chart_savename)
          

    print('end:', datetime.datetime.now())
    
            
    
# https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls
    
if __name__ == "__main__":
    
    os.system('cls')

    # pandasのprint表示の仕方を設定
    pandas.set_option('display.max_rows', None)
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.width', 1000)
    
    update_ohlc_1day()
    # tickers_file = pandas.read_csv('tickers_list.csv', header=0, index_col=0)

    # os.makedirs(ohlc_all_folder, exist_ok=True) 
    
    # for ticker, row in tickers_file.iterrows():
        
    #     create_daily_chart_csv(ohlc_all_folder, ticker)


 
            
