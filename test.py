from re import sub
import pandas
import datetime
import pandas_datareader.data as web
import os
import yfinance
 
def create_daily_chart_csv(folder_path, ticker):
    """ 日足チャートのCSVの作成

    Args:
        folder_path (_type_): _description_
        ticker (_type_): _description_
    """
    file_name = f'{folder_path}/{ticker}.csv' 
    daily_chart = pandas.DataFrame()
           
    if not os.path.exists(file_name):
        try:
            # start = datetime.date(1990,1,4)
            # today = datetime.date.today()
            # daily_chart = web.DataReader(f'{ticker}.T', "yahoo", start, today)
            daily_chart = yfinance.download(tickers=f'{ticker}.T', period='max', progress=False)
                
        except Exception:
            pass
        
        if not daily_chart.empty:
            daily_chart.to_csv(file_name, header=True) # 保存
            print(f'{file_name} is created.')
                    

def update_chart_csv(folder_path, ticker):
    """差分更新更新

    Args:
        folder_path (_type_): _description_
        ticker (_type_): _description_
    """
    file_name = f'{folder_path}/{ticker}.csv'
    if os.path.exists(file_name):
        
        # csvファイルを読み取り、最新日付を取得する
        daily_chart =  pandas.read_csv(file_name, index_col=0, parse_dates=True)
        # last_date = daily_chart.tail(1).index.date[0]
        # print(daily_chart.tail(1).index.date[0])
        last_date = daily_chart.index[-1].date()
        # csvファイルの最新日付の翌日から本日までのデータを取得する
        today = datetime.date.today()
        delta_date = today - last_date
        print('update days = ', delta_date.days)
        
        # 更新がない場合も読みだす
        if delta_date == 0:
            delta_date = 1
            
        update_chart = pandas.DataFrame()
        try:
            # start = last_date + datetime.timedelta(days=1)
            # today = datetime.date.today()
            # update_chart = web.DataReader(f'{ticker}.T', "yahoo", start, today)
            update_chart = yfinance.download(tickers=f'{ticker}.T', period=f'{delta_date.days}d', interval='1d', progress=False)
            # update_chart = update_chart[:-1] # 末尾行は削除

        except Exception:
            pass
        
        # 新しいデータを結合する
        if not update_chart.empty:
            daily_chart = pandas.concat([daily_chart, update_chart], sort=True)
            daily_chart = daily_chart[~daily_chart.index.duplicated(keep='last')] # 重複があれば最新で更新する
            daily_chart.to_csv(file_name, header=True) # 保存
            print(f"{ticker: }{file_name} is updated.")            
        
    else:
        print(f"{ticker: }{file_name} is not existed.")

def create_tickers_csv():
    """使わない予定
    """
    input_filename = 'jpx/data_j.xls'
    output_filename = 'tickers_list2.csv'
    
    if not os.path.exists(output_filename):
        # tickers_list = pandas.read_excel(input_filename, index_col=1)
        tickers_list = pandas.read_excel(input_filename, index_col=1)
        
        # ETF, ETNは除く    
        tickers_list = tickers_list[tickers_list['市場・商品区分']!='ETF・ETN']
        tickers_list = tickers_list[tickers_list['市場・商品区分']!='PRO Market']
        tickers_list = tickers_list[tickers_list['市場・商品区分']!='REIT・ベンチャーファンド・カントリーファンド・インフラファンド']
        tickers_list = tickers_list[tickers_list['市場・商品区分']!='出資証券']
        
        # 5ケタ以上は除く
        tickers_list = tickers_list[tickers_list.index < 10000]
        
        # tickers_data = pandas.read_csv('companylist.csv', encoding="utf-8", header=0, index_col=0)
        # tickers_data = tickers_file.rename(columns={'銘柄名':'trading_name'})
        # tickers_data = tickers_file.rename(columns={'市場・商品区分':'market_segment'})
        # tickers_data = tickers_file.rename(columns={'33業種コード':'industry_33_code'})
        # tickers_data = tickers_file.rename(columns={'33業種区分':'industry_33_segment'})
        # tickers_data = tickers_file.rename(columns={'33業種コード':'industry_33_segment'})
        # tickers_data = tickers_file.rename(columns={'33業種区分':'industry_33_segment'})
        tickers_list['発行株式'] = 0
        tickers_list.to_csv(output_filename)
        

def update_tickers_csv():
    output_filename = 'tickers_list2.csv'
    
    url = 'https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls'
    tickers_list = pandas.read_excel(url, index_col=1)

    # ETF, ETNは除く    
    tickers_list = tickers_list[tickers_list['市場・商品区分']!='ETF・ETN']
    tickers_list = tickers_list[tickers_list['市場・商品区分']!='PRO Market']
    tickers_list = tickers_list[tickers_list['市場・商品区分']!='REIT・ベンチャーファンド・カントリーファンド・インフラファンド']
    tickers_list = tickers_list[tickers_list['市場・商品区分']!='出資証券']
    
    # 5ケタ以上は除く
    tickers_list = tickers_list[tickers_list.index < 10000]
    
    # Dataframeに列を追加
    tickers_list['出来高'] = 0
    tickers_list['売買代金'] = 0
    tickers_list['VWAP'] = 0
    tickers_list['約定回数'] = 0
    tickers_list['時価総額'] = 0
    tickers_list['発行株式'] = 0
    
    for ticker, row in tickers_list.iterrows():
        # print(tickers_list.at[ticker,'発行株式'])        
        # print(tickers_list.at[ticker,'発行株式'] == 0)
        print(ticker)
        
        kabutan = Kabutan(ticker)
        tickers_list.at[ticker,'出来高'] = kabutan.volume
        tickers_list.at[ticker,'売買代金'] = kabutan.tradingvalue
        tickers_list.at[ticker,'VWAP'] = kabutan.vwap
        tickers_list.at[ticker,'約定回数'] = kabutan.tick
        tickers_list.at[ticker,'時価総額'] = kabutan.capitalization
        tickers_list.at[ticker,'発行株式'] = kabutan.sharedunderstanding
        print(tickers_list.at[ticker,'発行株式'])
    
    # 保存
    tickers_list.to_csv(output_filename)    
    
def dif_csv(ticker, folder1, folder2):
    
    file_name1 = f'{folder1}/{ticker}.csv'   
    file_name2 = f'{folder2}/{ticker}.csv'   
    if os.path.exists(file_name1):
        if os.path.exists(file_name2):
            daily_chart1 =  pandas.read_csv(file_name1, index_col=0, parse_dates=True)
            daily_chart2 =  pandas.read_csv(file_name2, index_col=0, parse_dates=True)

            if (daily_chart1.index.date[0] == daily_chart2.index.date[0]):
                # print(f'{ticker}: ', daily_chart1.index.date[0], ' - ', daily_chart2.index.date[0])
                pass
            else:
                print(f'{ticker} is diffrenet.')
       

    
    
# https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls
    
if __name__ == "__main__":
   
    # pandasのprint表示の仕方を設定
    pandas.set_option('display.max_rows', None)
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.width', 1000)

    # update_tickers_csv()

            
    tickers_file = pandas.read_csv('tickers_list.csv', header=0, index_col=0)

    # for ticker, row in tickers_file.iterrows():
    #     folder = 'yfinance_csv'
    #     os.makedirs(folder, exist_ok=True) 
    #     create_daily_chart_csv(folder, ticker)
    #     update_chart_csv(folder, ticker)
    #     # dif_csv(ticker, folder, 'chart_csv')
    #     pass
    #     # print(ticker)

 
            