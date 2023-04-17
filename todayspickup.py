import pandas
import datetime
import os
import yfinance
import time
import numpy
import indicator

chart_folder = 'yfinance_csv'
todayspickup_folder = 'todayspickup'
todayspickup_filename = f'./{todayspickup_folder}/master.csv'

def create_tickers(debug=False):
    """ 本日の注目銘柄のマスターファイルを作成する
    """ 
    tickers_list = pandas.DataFrame()
    tickers_list = pandas.read_csv('tickers_list.csv', header=0, index_col=0)
    # tickers_list = tickers_list.head(1)

    ticker_chart = pandas.DataFrame() 

    folder = chart_folder

    for ticker, row in tickers_list.iterrows():
        if debug == True:
            print('ticker: ', ticker)
            
        chart = pandas.DataFrame()
        try:
            chart = yfinance.download(tickers=f'{ticker}.T', period='100d', interval='1d', progress=False)
        except:
            pass
        
        if chart.empty:
            continue 
            
        indicator.add_basic(chart, [5, 25, 75, 100])
        indicator.add_swing_high_low(chart)
        # print(chart)
        indicator.add_candlestick_pattern(chart)
        indicator.add_sma_pattern(chart)

        chart['出来高前日差'] = chart['Volume'].diff()
        chart['出来高前日比'] = (chart['Volume'] / chart['Volume'].shift(1)).round(1)
        chart['出来高発行株式割合'] = (chart['Volume'] / row['発行株式'] * 100).round(1)
        chart['陽線陰線'] = '→'
        chart['陽線陰線'].mask((chart['Close'] > chart['Open']), '↑', inplace=True)
        chart['陽線陰線'].mask((chart['Close'] < chart['Open']), '↓', inplace=True)
        # chart['75over'] = 0
        # chart['75over'].mask((chart['Close'] > chart['Open']) & (chart['Low'] <= chart['SMA75']) & (chart['High'] > chart['SMA75']), '1', inplace=True) # 突き抜け
        # chart['75over'].mask((chart['Low'] > chart['SMA75']) & (chart['High'] > chart['SMA75']), '2', inplace=True) # 上
        # chart['25over'] = 0
        # chart['25over'].mask((chart['Close'] > chart['Open']) & (chart['Low'] <= chart['SMA25']) & (chart['High'] > chart['SMA25']), '1', inplace=True) # 突き抜け
        # chart['25over'].mask((chart['Low'] > chart['SMA25']) & (chart['High'] > chart['SMA25']), '2', inplace=True) # 上
        
        y = chart[chart['SwingHigh']>0]
        takane = 0
        if not y.empty:
            takane = y.iloc[-1]['SwingHigh'] 
        
        chart['Swinghighover'] = 0
        chart['Swinghighover'].mask((chart['Close'] >= takane), '1', inplace=True)
        # chart['三平'] = 'None'
        # chart['三平'].mask(((chart['Close'] > chart['Open']) & (chart['Close'].shift(1) > chart['Open'].shift(1)) & (chart['Close'].shift(2) > chart['Open'].shift(2)) 
        #                   & (chart['High'] >= charｇt['High'].shift(1)) & (chart['High'].shift(1) >= chart['High'].shift(2))
        #                   & (chart['Low'] >= chart['Low'].shift(1)) & (chart['Low'].shift(1) >= chart['Low'].shift(2))), 
        #                  'Red', inplace=True)
        # chart['三平'].mask(((chart['Close'] < chart['Open']) & (chart['Close'].shift(1) < chart['Open'].shift(1)) & (chart['Close'].shift(2) < chart['Open'].shift(2)) 
        #                   & (chart['High'] <= chart['High'].shift(1)) & (chart['High'].shift(1) <= chart['High'].shift(2))
        #                   & (chart['Low'] <= chart['Low'].shift(1)) & (chart['Low'].shift(1) <= chart['Low'].shift(2))), 
        #                  'Black', inplace=True)        
        
        date = chart.index[-1]              
        name = row['銘柄名']
        shares = row['発行株式']
        diff = chart.at[date, '出来高前日差']
        volume = chart.at[date, 'Volume']
        sharesratio = chart.at[date, '出来高発行株式割合']
        previousratio = chart.at[date, '出来高前日比']
        pn = chart.at[date, '陽線陰線']   
        # sanpei = chart.at[date, '三平']
        sanpei = chart.at[date, 'Hei']
        ku = chart.at[date, 'Ku']
        over75 = chart.at[date, 'over75']
        over25 = chart.at[date, 'over25']
        ashi1 = chart.at[date, 'Ashi1']
        ashi2 = chart.at[date, 'Ashi2']
        swinghigh = chart.at[date, 'Swinghighover']

        test_chart = pandas.DataFrame({'銘柄名':[name], 
                                       '陽線陰線':[pn], 
                                       '出来高':[volume], 
                                       '出来高前日差':[diff], 
                                       '出来高発行株式割合':[sharesratio], 
                                       '出来高前日比':[previousratio],
                                       '三平':[sanpei], 
                                       '空':[ku],
                                       '25SMA越':[over25],
                                       '75SMA越':[over75],
                                       '足1':[ashi1],
                                       '足2':[ashi2],
                                       '直近高値越':[swinghigh],
                                       },
                                      index=[ticker])
    
        ticker_chart = pandas.concat([ticker_chart, test_chart], sort=False,)

    # infを0に変換
    ticker_chart = ticker_chart.replace([numpy.inf, -numpy.inf], numpy.nan)
    ticker_chart = ticker_chart.fillna(0) # 0でnanを置換
    
    # 保存
    os.makedirs(todayspickup_folder, exist_ok=True)  
    ticker_chart.to_csv(todayspickup_filename, header=True)
    
    
def change_view(debug=False):
    
    tickers_list = pandas.read_csv(todayspickup_filename, header=0, index_col=0)
    
    # print(ticker_chart.sort_values(by='出来高発行株式割合', ascending=False).head(100))
    # print('\n')
    # print(ticker_chart.sort_values(by='出来高前日比', ascending=False).head(100))
    
    tickers_list = tickers_list.sort_values(by='出来高発行株式割合', ascending=False)
    filename = f'./{todayspickup_folder}/volume_shares.csv'
    tickers_list[tickers_list['出来高発行株式割合']> 10].to_csv(filename, header=True) # 保存

    tickers_list = tickers_list.sort_values(by='出来高前日比', ascending=False)
    filename = f'./{todayspickup_folder}/volume_previous.csv'
    tickers_list[tickers_list['出来高前日比']>2].to_csv(filename, header=True) # 保存

    tickers_list = tickers_list.sort_values(by='三平', ascending=False)
    filename = f'./{todayspickup_folder}/akasanpei.csv'
    tickers_list[tickers_list['三平']>0].to_csv(filename, header=True) # 保存
    
    tickers_list = tickers_list.sort_values(by='三平', ascending=True)
    filename = f'./{todayspickup_folder}/kurosanpei.csv'
    tickers_list[tickers_list['三平']<0].to_csv(filename, header=True) # 保存

    tickers_list = tickers_list.sort_values(by='空', ascending=False)
    filename = f'./{todayspickup_folder}/aka_ku.csv'
    tickers_list[tickers_list['空']>0].to_csv(filename, header=True) # 保存

    tickers_list = tickers_list.sort_values(by='空', ascending=True)
    filename = f'./{todayspickup_folder}/kuro_ku.csv'
    tickers_list[tickers_list['空']<0].to_csv(filename, header=True) # 保存
    
    tickers_list = tickers_list.sort_values(by='75SMA越', ascending=True)
    filename = f'./{todayspickup_folder}/over75day.csv'
    tickers_list[tickers_list['75SMA越']>0].to_csv(filename, header=True) # 保存
    
if __name__ == "__main__":
    
    os.system('cls')

    # pandasのprint表示の仕方を設定
    pandas.set_option('display.max_rows', None)
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.width', 1000)

    # tickers_file = tickers_file.head(200)
    create_tickers(True)
    change_view()
