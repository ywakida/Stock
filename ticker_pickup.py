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
    
        #print('ticker: ', ticker)
        update_chart = pandas.DataFrame()
        try:
            update_chart = yfinance.download(tickers=f'{ticker}.T', period='3d', interval='1d', progress=False)
        
        except:
            pass
        
        if update_chart.empty:
            continue 
            
        update_chart['VolumeDiff'] = update_chart['Volume'].diff()
        update_chart['VolumePreviousRatio'] = (update_chart['Volume'] / update_chart['Volume'].shift(1)).round(1)
        update_chart['VolumeSharesRatio'] = (update_chart['Volume'] / row['発行株式'] * 100).round(1)
        update_chart['Rays'] = 0
        update_chart['Rays'].mask((update_chart['Close'] > update_chart['Open']), 1, inplace=True)
        update_chart['Rays'].mask((update_chart['Close'] < update_chart['Open']), -1, inplace=True)
        
        # print(update_chart)
        
        date = update_chart.index[-1]                
        name = row['銘柄名']
        shares = row['発行株式']
        diff = update_chart.at[date, 'VolumeDiff']
        volume = update_chart.at[date, 'Volume']
        sharesratio = update_chart.at[date, 'VolumeSharesRatio']
        previousratio = update_chart.at[date, 'VolumePreviousRatio']
        rays = update_chart.at[date, 'Rays']

        
        test_chart = pandas.DataFrame({'name':[name], 'rays':[rays], 'volume':[volume], 'diff':[diff], 'sharesratio':[sharesratio], 'previousratio':[previousratio]}, index=[ticker])
    
        ticker_chart = pandas.concat([ticker_chart, test_chart], sort=False,)
        
        # print(ticker_chart)
    # infを0に変換
    ticker_chart = ticker_chart.replace([numpy.inf, -numpy.inf], numpy.nan)
    ticker_chart = ticker_chart.fillna(0) # 0でnanを置換
    
    print(ticker_chart.sort_values(by='sharesratio', ascending=False).head(100))
    print('\n')
    print(ticker_chart.sort_values(by='previousratio', ascending=False).head(100))
    
    ticker_chart = ticker_chart.sort_values(by='sharesratio', ascending=False)
    filename = f'volume_shares.csv'
    ticker_chart.to_csv(file_name, header=True) # 保存
    
    ticker_chart = ticker_chart.sort_values(by='previousratio', ascending=False)
    filename = f'volume_previous.csv'
    ticker_chart.to_csv(file_name, header=True) # 保存
    
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
    
#    tickers_file = tickers_file.head(1000)
    task(tickers_file)

 
            
