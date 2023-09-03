import pandas
import datetime
import os
import yfinance
import time
import numpy
import indicator
from zoneinfo import ZoneInfo

chart_folder = 'yfinance_csv'
todayspickup_folder = 'todayspickup'
todayspickup_filename = f'./{todayspickup_folder}/master.csv'

def test(date=datetime.datetime.today().date(), debug=False):
    print(date)
    
    chart = pandas.DataFrame()
    file_name = f'{chart_folder}/9734.csv'     
    file_name = f'{chart_folder}/6920.csv'
    chart = pandas.read_csv(file_name, index_col=0, parse_dates=True)
    print(chart.tail(5))
    
    # if date in chart.index:
    if date == chart.index[-1].date():
        volume = chart.at[chart.index[-1], 'Volume']
        print(volume)
    else:
        print(f"{date} is not found")
    
    
    
def create_tickers(date=datetime.datetime.today().date(), debug=False):
    """ 本日の注目銘柄のマスターファイルを作成する
    """ 
    tickers_list = pandas.DataFrame()
    tickers_list = pandas.read_csv('tickers_list.csv', header=0, index_col=0)
    # tickers_list = tickers_list.tail(150)

    ticker_chart = pandas.DataFrame() 
    

    for ticker, row in tickers_list.iterrows():
           
        chart = pandas.DataFrame()
        try:
            if debug == False:
                chart = yfinance.download(tickers=f'{ticker}.T', period='100d', interval='1d', progress=False)
            else:
                file_name = f'{chart_folder}/{ticker}.csv'   
                print('ticker: ', ticker, ' filename: ', file_name)
                chart = pandas.read_csv(file_name, index_col=0, parse_dates=True)
                
        except:
            pass
        
        if chart.empty:
            print('ticker: ', ticker, ' filename: ', file_name, ' is empty.')
            continue 
        
        chart.sort_index(inplace=True)
        chart = chart[~chart.index.duplicated(keep='last')]
            
        indicator.add_basic(chart, [5, 25, 75, 100])
        indicator.add_swing_high_low(chart, width=3, only_entitiy=True)
        # print(chart)
        indicator.add_candlestick_pattern(chart)
        indicator.add_sma_pattern(chart)
        indicator.add_rci(chart, 9)
        indicator.add_sma_slope(chart)

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
        
        y = chart[chart['SwingHigh'].notna()] # N/A以外を抽出する
        takane = 0
        if not y.empty:
            takane = y.iloc[-1]['SwingHigh'] 
        
        chart['Swinghighover'] = chart['Close'] > takane # 高値を超えた
        # chart['Swinghighover'].mask((chart['Close'] >= takane), '1', inplace=True)
        
        chart['Over75swinghigh'] = (chart['Swinghighover']) & (chart['crossdSMA75'])
        chart['Hanpatsu75'] = (chart['over75'] > 1) & (chart['Rci'] < -80) & (chart['SMASlope75']> 0)
        
        # 変数への格納
        if date == chart.index[-1].date():
            timestamp = chart.index[-1]               
            name = row['銘柄名']
            shares = row['発行株式']
            diff = chart.at[timestamp, '出来高前日差']
            volume = chart.at[timestamp, 'Volume']
            sharesratio = chart.at[timestamp, '出来高発行株式割合']
            previousratio = chart.at[timestamp, '出来高前日比']
            pn = chart.at[timestamp, '陽線陰線']   
            # sanpei = chart.at[timestamp, '三平']
            sanpei = chart.at[timestamp, 'Hei']
            ku = chart.at[timestamp, 'Ku']
            over75 = chart.at[timestamp, 'over75']
            over25 = chart.at[timestamp, 'over25']
            ashi1 = chart.at[timestamp, 'Ashi1']
            ashi2 = chart.at[timestamp, 'Ashi2']
            swinghigh = chart.at[timestamp, 'Swinghighover']
            over75swinghigh = chart.at[timestamp, 'Over75swinghigh']
            hanpatsu75 = chart.at[timestamp, 'Hanpatsu75']
            
            try:
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
                                            '75SMAと直近高値越':over75swinghigh,
                                            '直近高値':takane,
                                            '75反発':hanpatsu75,
                                            },
                                            index=[ticker])
            except Exception:
                pass
        
            ticker_chart = pandas.concat([ticker_chart, test_chart], sort=False,)

    # infを0に変換
    ticker_chart = ticker_chart.replace([numpy.inf, -numpy.inf], numpy.nan)
    ticker_chart = ticker_chart.fillna(0) # 0でnanを置換
    
    # 保存
    os.makedirs(todayspickup_folder, exist_ok=True)  
    ticker_chart.to_csv(todayspickup_filename, header=True)
    
    
def change_view(debug=False):
    
    tickers_list = pandas.read_csv(todayspickup_filename, header=0, index_col=0)
    
    if not tickers_list.empty:
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
        
        filename = f'./{todayspickup_folder}/over75high.csv'
        tickers_list[tickers_list['75SMAと直近高値越']==True].to_csv(filename, header=True) # 保存
        
        tickers_list = tickers_list.sort_values(by='75SMA越', ascending=True)
        filename = f'./{todayspickup_folder}/hanpatsu75.csv'
        tickers_list[tickers_list['75反発']==True].to_csv(filename, header=True) # 保存
        
if __name__ == "__main__":
    
    os.system('cls')
    

    # pandasのprint表示の仕方を設定
    pandas.set_option('display.max_rows', None)
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.width', 1000)

    print(datetime.datetime.now(ZoneInfo("Asia/Tokyo")).date())
    print('today():', datetime.datetime.today())
    print('today().date():', datetime.datetime.today().date())
    print('today().timestamp():', datetime.datetime.today().timestamp())
    
    # date2 = datetime.datetime(2023, 7, 28).date()
    # print(date2)
    # test(date2)
    # create_tickers(datetime.datetime.today().date(),True)
    # create_tickers(date2,True)
    # change_view()
    
    ticker = 4824
    start = time.time()
    chart = yfinance.download(tickers=f'{ticker}.T', period='100d', interval='1d', progress=False)
    print('100 ', time.time() - start)
    start = time.time()
    chart = yfinance.download(tickers=f'{ticker}.T', period='1d', interval='1d', progress=False)
    file_name = f'{chart_folder}/{ticker}.csv'               
    chart = pandas.read_csv(file_name, index_col=0, parse_dates=True)
    print('1 ', time.time() - start)
    