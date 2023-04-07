import pandas
import datetime
import os
import yfinance
import time
import numpy

ticker_file = pandas.DataFrame()

def task(tickers_list):

    ticker_chart = pandas.DataFrame() 

    folder = 'yfinance_csv'

    for ticker, row in tickers_list.iterrows():
        print('ticker: ', ticker)
        chart = pandas.DataFrame()
        try:
            chart = yfinance.download(tickers=f'{ticker}.T', period='3d', interval='1d', progress=False)
        except:
            pass
        
        if chart.empty:
            continue 
            
        chart['出来高前日差'] = chart['Volume'].diff()
        chart['出来高前日比'] = (chart['Volume'] / chart['Volume'].shift(1)).round(1)
        chart['出来高発行株式割合'] = (chart['Volume'] / row['発行株式'] * 100).round(1)
        chart['陽線陰線'] = '→'
        chart['陽線陰線'].mask((chart['Close'] > chart['Open']), '↑', inplace=True)
        chart['陽線陰線'].mask((chart['Close'] < chart['Open']), '↓', inplace=True)
        
        chart['三平'] = 'None'
        chart['三平'].mask(((chart['Close'] > chart['Open']) & (chart['Close'].shift(1) > chart['Open'].shift(1)) & (chart['Close'].shift(2) > chart['Open'].shift(2)) 
                          & (chart['High'] >= chart['High'].shift(1)) & (chart['High'].shift(1) >= chart['High'].shift(2))
                          & (chart['Low'] >= chart['Low'].shift(1)) & (chart['Low'].shift(1) >= chart['Low'].shift(2))), 
                         'Red', inplace=True)
        chart['三平'].mask(((chart['Close'] < chart['Open']) & (chart['Close'].shift(1) < chart['Open'].shift(1)) & (chart['Close'].shift(2) < chart['Open'].shift(2)) 
                          & (chart['High'] <= chart['High'].shift(1)) & (chart['High'].shift(1) <= chart['High'].shift(2))
                          & (chart['Low'] <= chart['Low'].shift(1)) & (chart['Low'].shift(1) <= chart['Low'].shift(2))), 
                         'Black', inplace=True)        
        
        
        date = chart.index[-1]                
        name = row['銘柄名']
        shares = row['発行株式']
        diff = chart.at[date, '出来高前日差']
        volume = chart.at[date, 'Volume']
        sharesratio = chart.at[date, '出来高発行株式割合']
        previousratio = chart.at[date, '出来高前日比']
        pn = chart.at[date, '陽線陰線']   
        sanpei = chart.at[date, '三平']

        test_chart = pandas.DataFrame({'銘柄名':[name], 
                                       '陽線陰線':[pn], 
                                       '出来高':[volume], 
                                       '出来高前日差':[diff], 
                                       '出来高発行株式割合':[sharesratio], 
                                       '出来高前日比':[previousratio],
                                       '三平':[sanpei]}, 
                                      index=[ticker])
    
        ticker_chart = pandas.concat([ticker_chart, test_chart], sort=False,)

    # infを0に変換
    ticker_chart = ticker_chart.replace([numpy.inf, -numpy.inf], numpy.nan)
    ticker_chart = ticker_chart.fillna(0) # 0でnanを置換
    
    # print(ticker_chart.sort_values(by='出来高発行株式割合', ascending=False).head(100))
    # print('\n')
    # print(ticker_chart.sort_values(by='出来高前日比', ascending=False).head(100))
    
    ticker_chart = ticker_chart.sort_values(by='出来高発行株式割合', ascending=False)
    filename = f'volume_shares.csv'
    ticker_chart.to_csv(filename, header=True) # 保存

    ticker_chart = ticker_chart.sort_values(by='出来高前日比', ascending=False)
    filename = f'volume_previous.csv'
    ticker_chart.to_csv(filename, header=True) # 保存
    
       # chart_filename = f'{folder}/{ticker}.csv'

        # if os.path.exists(chart_filename):

        #     print(f"{ticker}.csv is exsisted.")
        

        #     # open chart csv file

        #     existed_chart = pandas.DataFrame()

        #     existed_chart =  pandas.read_csv(chart_filename, index_col=0, parse_dates=True)
            

        #     update_chart = pandas.DataFrame()

        #     update_chart = yfinance.download(tickers=f'{ticker}.T', period='1d', interval='1d', progress=False)

        #     print(update_chart)

        #     # if not df_1d.empty:

        #     #     chart =  pandas.concat([chart, df_1d], sort=True)
                

        #     if not update_chart.empty:

        #         if len(update_chart) > 1:


        #         daily_chart = pandas.concat([existed_chart, update_chart], sort=True)

        #         daily_chart.drop_duplicates(keep='last', inplace=True) # 重複があれば最新で更新する

        #         daily_chart.to_csv(file_name, header=True) # 保存

        #         print(f"{file_name} is updated {delta_days} days")
                

if __name__ == "__main__":
    
    os.system('cls')

    # pandasのprint表示の仕方を設定
    pandas.set_option('display.max_rows', None)
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.width', 1000)

    tickers_file = pandas.read_csv('tickers_list.csv', header=0, index_col=0)
    # tickers_file = tickers_file.head(200)

    task(tickers_file)
