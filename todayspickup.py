import pandas as pd
import datetime
import os
import yfinance
import json
import numpy as np
import indicator
from zoneinfo import ZoneInfo
import chart_days
import time

# コンフィグ
# gdrivepath = '/content/drive/My Drive/stock/'
basepath = './'
encode = 'utf-8'

ohlc_folder = chart_days.daily_100_folder
todayspickup_folder = 'pickup_today'
todayspickup_filename = f'./{todayspickup_folder}/master.csv'
tickers_list_filename_full = f'{basepath}tickers_list.csv'

def test(date=datetime.datetime.today().date(), debug=False):
    print(date)
    
    chart = pd.DataFrame()
    file_name = f'{ohlc_folder}/9734.csv'     
    file_name = f'{ohlc_folder}/6920.csv'
    chart = pd.read_csv(file_name, index_col=0, parse_dates=True)
    print(chart.tail(5))
    
    # if date in chart.index:
    if date == chart.index[-1].date():
        volume = chart.at[chart.index[-1], 'Volume']
        print(volume)
    else:
        print(f"{date} is not found")
    

def create_tickers2(date=datetime.datetime.today().date(), debug=False):
    try:
        # 東証の全銘柄リストを取得（事前に用意した CSV ファイルを読み込む）
        csv_path = open(tickers_list_filename_full, 'r', encoding=encode)
        tickers_list = pd.read_csv(csv_path, header=0, index_col=0)
        # tickers_list = pd.read_csv(csv_path, dtype={'コード': str}, header=0)
    
        if tickers_list.empty or len(tickers_list) <= 1:
            return

    except Exception as e:
        print(f"{tickers_list_filename_full} CSVを読み込めませんでした: {e}")
        return
    
    print(f"{tickers_list_filename_full}を読み込みました")
    
    start = time.time() # ここで開始
            
    # yfinance 用に 4桁の証券コードに「.T」を付ける
    tickers_list["code"] = tickers_list.index.astype(str).str.zfill(4) + ".T"

    if debug:
        # tickers_list = tickers_list.head(200)
        pass

    # リストを分割
    batch_size = 50
    stock_batches = [tickers_list["code"].tolist()[i:i + batch_size] for i in range(0, len(tickers_list), batch_size)]

    # 分割したリストを順番にダウンロード
    tickers_ohlc = []
    for idx, stock_batch in enumerate(stock_batches):
        print(f"Downloading batch {idx+1}/{len(stock_batches)}...")
        
        try:
            # tickers_ohlc = yfinance.download(tickers_list["code"].tolist(), period="1d", interval='1d', group_by="ticker", progress=True, auto_adjust=False, threads=True)
            ohlc = yfinance.download(stock_batch, period="1d", interval='1d', group_by="ticker", progress=True, auto_adjust=False, threads=True)
            tickers_ohlc.append(ohlc)
            # 通信負荷を考慮し、一定時間スリープ
            time.sleep(1)  # 規定秒待機    
            
        except Exception as e:
            print(f"株価を読み込めませんでした: {e}")
            continue
        
    if tickers_ohlc:
        tickers_ohlc = pd.concat(tickers_ohlc, axis=1)  # 列方向で結合
        
    for ticker, row in tickers_list.iterrows():
        ticker.zfill(4)
        ticker_filename_full = f'{ohlc_folder}/{ticker}.csv'  
        # print(ticker)
        
        # ファイルが存在しなければ、全データをダウンロードし、ファイルを新規作成する     
        if not os.path.exists(ticker_filename_full):
            print(f"{ticker_filename_full}は読み込みなかったのでスキップします")    
            continue
        
        ticker_csv_path = open(ticker_filename_full, 'r', encoding=encode)
        ohlc_old = pd.read_csv(ticker_csv_path, index_col = 0, parse_dates=True)
        
        try:
            ohlc_today = tickers_ohlc[row["code"]]
        except:
            print("インデックスがないためスキップ")
            continue
        
        last_date = ohlc_old.index[-1]
        if last_date == ohlc_today.index[-1]:        
            continue
        
        ohlc_updated = pd.concat([ohlc_old, ohlc_today])
        ohlc_updated.sort_index(inplace=True)
        ohlc_updated = ohlc_updated[~ohlc_updated.index.duplicated(keep='last')]

        # print(ohlc_updated)

        
    print('一括ダウンロード方式:', time.time() - start)
    start = time.time() # ここで開始

    for ticker, row in tickers_list.iterrows():
        # print(ticker)
        chart = pd.DataFrame()
        try:

            chart = yfinance.download(tickers=f'{ticker}.T', period='1mo', interval='1d', progress=False)
            chart.columns = chart.columns.get_level_values(0)

        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON for ticker {ticker}: {e}")
            
        except Exception as e:
            print(f"Failed to retrieve data for ticker {ticker}: {e}")
        
        if chart.empty:
            print('ticker: ', ticker, ' data is empty.')
            continue 
        
        chart.sort_index(inplace=True)
        chart = chart[~chart.index.duplicated(keep='last')]

    print('個別ダウンロード方式:', time.time() - start)
    return


def load_ticker_list(file_path='tickers_list.csv', debug=False, debug_limit=100000):
    df = pd.read_csv(file_path, header=0, index_col=0)
    if debug:
        df = df.head(debug_limit)
    return df

def fetch_chart_data(ticker, row, debug, ohlc_folder):
    try:
        if debug:
            file_name = f'{ohlc_folder}/{ticker}.csv'
            print('ticker:', ticker, 'filename:', file_name)
            return pd.read_csv(file_name, index_col=0, parse_dates=True)
        else:
            df = yfinance.download(tickers=f'{ticker}.T', period='1mo', interval='1d', progress=False)
            df.columns = df.columns.get_level_values(0)
            return df
    except json.JSONDecodeError as e:
        print(f"JSON decode error for {ticker}: {e}")
    except Exception as e:
        print(f"Failed to fetch data for {ticker}: {e}")
    return pd.DataFrame()

def apply_indicators(chart, row):
    indicator.add_basic(chart, [5, 25, 75, 100, 200])
    indicator.add_swing_high_low(chart, width=3, only_entitiy=True)
    indicator.add_candlestick_pattern(chart)
    indicator.add_sma_pattern(chart)
    indicator.add_rci(chart, 9)
    indicator.add_sma_slope(chart)
    indicator.add_breakout(chart)

    chart['出来高前日差'] = chart['Volume'].diff()
    chart['出来高前日比'] = (chart['Volume'] / chart['Volume'].shift(1)).round(1)
    chart['出来高発行株式割合'] = (chart['Volume'] / row['発行株式'] * 100).round(1)

    chart['陽線陰線'] = '→'
    chart.loc[chart['Close'] > chart['Open'], '陽線陰線'] = '↑'
    chart.loc[chart['Close'] < chart['Open'], '陽線陰線'] = '↓'

    chart['75over'] = 0
    chart.loc[(chart['Close'] > chart['Open']) & (chart['Low'] <= chart['SMA75']) & (chart['High'] > chart['SMA75']), '75over'] = 1
    chart.loc[(chart['Low'] > chart['SMA75']) & (chart['High'] > chart['SMA75']), '75over'] = 2

    chart['25over'] = 0
    chart.loc[(chart['Close'] > chart['Open']) & (chart['Low'] <= chart['SMA25']) & (chart['High'] > chart['SMA25']), '25over'] = 1
    chart.loc[(chart['Low'] > chart['SMA25']) & (chart['High'] > chart['SMA25']), '25over'] = 2

    takane = chart[chart['SwingHigh'].notna()].iloc[-1]['SwingHigh'] if chart['SwingHigh'].notna().any() else 0
    chart['Swinghighover'] = chart['Close'] > takane
    chart['Over75swinghigh'] = chart['Swinghighover'] & chart['crossdSMA75']
    chart['Hanpatsu75'] = (chart['over75'] > 1) & (chart['Rci'] < -80) & (chart['SMASlope75'] > 0)
    chart['Perfect2575200'] = (chart['SMA25'] >= chart['SMA75']) & (chart['SMA75'] >= chart['SMA200'])

    return chart, takane

def extract_today_row(chart, row, date, takane):
    """ 本日の
    """ 
    if date != chart.index[-1].date():
        return None

    timestamp = chart.index[-1]
    return pd.DataFrame({
        '銘柄名': [row['銘柄名']],
        '陽線陰線': [chart.at[timestamp, '陽線陰線']],
        '出来高': [chart.at[timestamp, 'Volume']],
        '出来高前日差': [chart.at[timestamp, '出来高前日差']],
        '出来高発行株式割合': [chart.at[timestamp, '出来高発行株式割合']],
        '出来高前日比': [chart.at[timestamp, '出来高前日比']],
        '三平': [chart.at[timestamp, 'Hei']],
        '空': [chart.at[timestamp, 'Ku']],
        '25SMA越': [chart.at[timestamp, 'over25']],
        '75SMA越': [chart.at[timestamp, 'over75']],
        '足1': [chart.at[timestamp, 'Ashi1']],
        '足2': [chart.at[timestamp, 'Ashi2']],
        '直近高値越': [chart.at[timestamp, 'Swinghighover']],
        '75SMAと直近高値越': [chart.at[timestamp, 'Over75swinghigh']],
        '直近高値': [takane],
        '75反発': [chart.at[timestamp, 'Hanpatsu75']],
        'パーフェクトオーダー': [chart.at[timestamp, 'Perfect2575200']],
        'RCI': [chart.at[timestamp, 'Rci']],
        'ブレークアウト日数': [chart.at[timestamp, 'Breakout']],
    }, index=[row.name])


def create_tickers3(date=datetime.datetime.today().date(), debug=False):
#    ohlc_folder = ohlc_folder  # 必要なら引数に
    # todayspickup_folder = './todays_pickup'
    # todayspickup_filename = os.path.join(todayspickup_folder, f'{date}_pickup.csv')

    tickers_list = load_ticker_list(debug=debug)
    ticker_chart = pd.DataFrame()

    for ticker, row in tickers_list.iterrows():
        print(ticker)
        chart = fetch_chart_data(ticker, row, debug, ohlc_folder)
        if chart.empty:
            print(f'ticker: {ticker} data is empty.')
            continue

        chart.sort_index(inplace=True)
        chart = chart[~chart.index.duplicated(keep='last')]

        chart, takane = apply_indicators(chart, row)
        today_row = extract_today_row(chart, row, date, takane)

        if today_row is not None:
            ticker_chart = pd.concat([ticker_chart, today_row], sort=False)
    
    ticker_chart.index.name = 'Ticker'
    ticker_chart.replace([np.inf, -np.inf], np.nan, inplace=True)
    ticker_chart.fillna(0, inplace=True)

    os.makedirs(todayspickup_folder, exist_ok=True)
    ticker_chart.to_csv(todayspickup_filename, header=True)
    
    

def create_tickers4(date=datetime.datetime.today().date(), debug=False):
    """ 本日の注目銘柄のマスターファイルを作成する
    """ 
    tickers_list = pd.DataFrame()
    tickers_list = pd.read_csv('tickers_list.csv', header=0, index_col=0)
    
    # if debug:
    #     # tickers_list = tickers_list[tickers_list.index == '1418'] # インターライフ
    #     tickers_list = tickers_list.head(10)
        

    ticker_chart = pd.DataFrame() 

    for ticker, row in tickers_list.iterrows():
        print(ticker)
        chart = pd.DataFrame()
        try:
            if debug == False:
                chart = yfinance.download(tickers=f'{ticker}.T', period='1mo', interval='1d', progress=False, threads=True)
                chart.columns = chart.columns.get_level_values(0)
                # file_name = f'{ohlc_folder}/{ticker}.csv'
                # chart = pd.read_csv(file_name, index_col=0, parse_dates=True)
                # today_chart = yfinance.download(tickers=f'{ticker}.T', period='1d', interval='1d', progress=False)
                # chart = pd.concat([chart, today_chart], sort=True) 
                # chart = chart[~chart.index.duplicated(keep='last')] # 日付に重複があれば最新で更新する
            else:
                file_name = f'{ohlc_folder}/{ticker}.csv'   
                print('ticker: ', ticker, ' filename: ', file_name)
                chart = pd.read_csv(file_name, index_col=0, parse_dates=True)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON for ticker {ticker}: {e}")
            
        except Exception as e:
            print(f"Failed to retrieve data for ticker {ticker}: {e}")
        
        if chart.empty:
            print('ticker: ', ticker, ' data is empty.')
            continue 
        
        chart.sort_index(inplace=True)
        chart = chart[~chart.index.duplicated(keep='last')]
            
        indicator.add_basic(chart, [5, 25, 75, 100, 200])
        indicator.add_swing_high_low(chart, width=3, only_entitiy=True)
        indicator.add_candlestick_pattern(chart)
        indicator.add_sma_pattern(chart)
        indicator.add_rci(chart, 9)
        indicator.add_sma_slope(chart)
        indicator.add_breakout(chart)

        chart['出来高前日差'] = chart['Volume'].diff()
        chart['出来高前日比'] = (chart['Volume'] / chart['Volume'].shift(1)).round(1)
        chart['出来高発行株式割合'] = (chart['Volume'] / row['発行株式'] * 100).round(1)
        chart['陽線陰線'] = '→'
        chart['陽線陰線'] = chart['陽線陰線'].mask((chart['Close'] > chart['Open']), '↑')
        chart['陽線陰線'] = chart['陽線陰線'].mask((chart['Close'] < chart['Open']), '↓')
        
        chart['75over'] = 0
        chart.loc[(chart['Close'] > chart['Open']) & (chart['Low'] <= chart['SMA75']) & (chart['High'] > chart['SMA75']), '75over'] = 1   # 条件1: 突き抜け        
        chart.loc[(chart['Low'] > chart['SMA75']) & (chart['High'] > chart['SMA75']), '75over'] = 2                                       # 条件2: 完全に上

        chart['25over'] = 0
        chart.loc[(chart['Close'] > chart['Open']) & (chart['Low'] <= chart['SMA25']) & (chart['High'] > chart['SMA25']), '25over'] = 1   # 条件1: 突き抜け（Close > Open かつ Low <= SMA25 かつ High > SMA25）
        chart.loc[(chart['Low'] > chart['SMA25']) & (chart['High'] > chart['SMA25']), '25over'] = 2                                       # 条件2: 完全に上（Low > SMA25 かつ High > SMA25）
        
        y = chart[chart['SwingHigh'].notna()] # N/A以外を抽出する
        takane = 0
        if not y.empty:
            takane = y.iloc[-1]['SwingHigh'] 
        
        chart['Swinghighover'] = chart['Close'] > takane # 高値を超えた
        # chart['Swinghighover'].mask((chart['Close'] >= takane), '1', inplace=True)
        
        chart['Over75swinghigh'] = (chart['Swinghighover']) & (chart['crossdSMA75'])
        chart['Hanpatsu75'] = (chart['over75'] > 1) & (chart['Rci'] < -80) & (chart['SMASlope75']> 0)
        
        chart['Perfect2575200'] = (chart['SMA25'] >= chart['SMA75']) & (chart['SMA75'] >= chart['SMA200'])
        
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
            perfect2575200 = chart.at[timestamp, 'Perfect2575200']
            rci9 = chart.at[timestamp, 'Rci']
            breakout = chart.at[timestamp, 'Breakout']

            # if debug:           
            #     print(chart[['over25', 'over75']].tail(1))
            
            try:
                test_chart = pd.DataFrame({'銘柄名':[name], 
                                            '陽線陰線':[pn], 
                                            '出来高':[volume], 
                                            '出来高前日差':[diff], 
                                            '出来高発行株式割合':[sharesratio], 
                                            '出来高前日比':[previousratio],
                                            '三平':[sanpei], 
                                            '空':[ku],
                                            '25SMA越':over25,
                                            '75SMA越':over75,
                                            '足1':ashi1,
                                            '足2':ashi2,
                                            '直近高値越':swinghigh,
                                            '75SMAと直近高値越':over75swinghigh,
                                            '直近高値':takane,
                                            '75反発':hanpatsu75,
                                            'パーフェクトオーダー':perfect2575200,
                                            'RCI':rci9,
                                            'ブレークアウト日数':breakout,
                                            },
                                            index=[ticker])
                
                # print(test_chart)
                
            except Exception:
                pass
        
            ticker_chart = pd.concat([ticker_chart, test_chart], sort=False,)
            ticker_chart.index.name = 'Ticker' # インデックスラベル名を作成

    # infを0に変換
    ticker_chart = ticker_chart.replace([np.inf, -np.inf], np.nan)
    ticker_chart = ticker_chart.fillna(0) # 0でnanを置換
    
    # 保存
    os.makedirs(todayspickup_folder, exist_ok=True)  
    ticker_chart.to_csv(todayspickup_filename, header=True)


def create_tickers5(date=datetime.datetime.today().date(), debug=False):
    """ 本日の注目銘柄のマスターファイルを作成する
    """ 
    tickers_list = pd.DataFrame()
    tickers_list = pd.read_csv('tickers_list.csv', header=0, index_col=0)
    
    # if debug:
    #     # tickers_list = tickers_list[tickers_list.index == '1418'] # インターライフ
    #     tickers_list = tickers_list.head(10)
        

    ticker_chart = pd.DataFrame() 

    for ticker, row in tickers_list.iterrows():
        print(ticker)
        chart = pd.DataFrame()
        try:
            if debug == False:
                # chart = yfinance.download(tickers=f'{ticker}.T', period='1mo', interval='1d', progress=False)
                # chart.columns = chart.columns.get_level_values(0)
                file_name = f'{ohlc_folder}/{ticker}.csv'
                chart = pd.read_csv(file_name, index_col=0, parse_dates=True)   # 昨日までのデータを読み込み
                today_chart = yfinance.download(tickers=f'{ticker}.T', period='1d', interval='1d', progress=False,threads=True)
                today_chart.index = today_chart.index.normalize()   # インデックスを日付のみに揃える（時刻切り捨て）
                chart = pd.concat([chart, today_chart]) 
                chart = chart[~chart.index.duplicated(keep='last')] # 日付に重複があれば最新で更新する
            else:
                file_name = f'{ohlc_folder}/{ticker}.csv'   
                print('ticker: ', ticker, ' filename: ', file_name)
                chart = pd.read_csv(file_name, index_col=0, parse_dates=True)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON for ticker {ticker}: {e}")
            
        except Exception as e:
            print(f"Failed to retrieve data for ticker {ticker}: {e}")
        
        if chart.empty:
            print('ticker: ', ticker, ' data is empty.')
            continue 
        
        chart.sort_index(inplace=True)
        chart = chart[~chart.index.duplicated(keep='last')]
            
        indicator.add_basic(chart, [5, 25, 75, 100, 200])
        indicator.add_swing_high_low(chart, width=3, only_entitiy=True)
        indicator.add_candlestick_pattern(chart)
        indicator.add_sma_pattern(chart)
        indicator.add_rci(chart, 9)
        indicator.add_sma_slope(chart)
        indicator.add_breakout(chart)

        chart['出来高前日差'] = chart['Volume'].diff()
        chart['出来高前日比'] = (chart['Volume'] / chart['Volume'].shift(1)).round(1)
        chart['出来高発行株式割合'] = (chart['Volume'] / row['発行株式'] * 100).round(1)
        chart['陽線陰線'] = '→'
        chart['陽線陰線'] = chart['陽線陰線'].mask((chart['Close'] > chart['Open']), '↑')
        chart['陽線陰線'] = chart['陽線陰線'].mask((chart['Close'] < chart['Open']), '↓')
        
        chart['75over'] = 0
        chart.loc[(chart['Close'] > chart['Open']) & (chart['Low'] <= chart['SMA75']) & (chart['High'] > chart['SMA75']), '75over'] = 1   # 条件1: 突き抜け        
        chart.loc[(chart['Low'] > chart['SMA75']) & (chart['High'] > chart['SMA75']), '75over'] = 2                                       # 条件2: 完全に上

        chart['25over'] = 0
        chart.loc[(chart['Close'] > chart['Open']) & (chart['Low'] <= chart['SMA25']) & (chart['High'] > chart['SMA25']), '25over'] = 1   # 条件1: 突き抜け（Close > Open かつ Low <= SMA25 かつ High > SMA25）
        chart.loc[(chart['Low'] > chart['SMA25']) & (chart['High'] > chart['SMA25']), '25over'] = 2                                       # 条件2: 完全に上（Low > SMA25 かつ High > SMA25）
        
        y = chart[chart['SwingHigh'].notna()] # N/A以外を抽出する
        takane = 0
        if not y.empty:
            takane = y.iloc[-1]['SwingHigh'] 
        
        chart['Swinghighover'] = chart['Close'] > takane # 高値を超えた
        # chart['Swinghighover'].mask((chart['Close'] >= takane), '1', inplace=True)
        
        chart['Over75swinghigh'] = (chart['Swinghighover']) & (chart['crossdSMA75'])
        chart['Hanpatsu75'] = (chart['over75'] > 1) & (chart['Rci'] < -80) & (chart['SMASlope75']> 0)
        
        chart['Perfect2575200'] = (chart['SMA25'] >= chart['SMA75']) & (chart['SMA75'] >= chart['SMA200'])
        
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
            perfect2575200 = chart.at[timestamp, 'Perfect2575200']
            rci9 = chart.at[timestamp, 'Rci']
            breakout = chart.at[timestamp, 'Breakout']

            # if debug:           
            #     print(chart[['over25', 'over75']].tail(1))
            
            try:
                test_chart = pd.DataFrame({'銘柄名':[name], 
                                            '陽線陰線':[pn], 
                                            '出来高':[volume], 
                                            '出来高前日差':[diff], 
                                            '出来高発行株式割合':[sharesratio], 
                                            '出来高前日比':[previousratio],
                                            '三平':[sanpei], 
                                            '空':[ku],
                                            '25SMA越':over25,
                                            '75SMA越':over75,
                                            '足1':ashi1,
                                            '足2':ashi2,
                                            '直近高値越':swinghigh,
                                            '75SMAと直近高値越':over75swinghigh,
                                            '直近高値':takane,
                                            '75反発':hanpatsu75,
                                            'パーフェクトオーダー':perfect2575200,
                                            'RCI':rci9,
                                            'ブレークアウト日数':breakout,
                                            },
                                            index=[ticker])
                
                # print(test_chart)
                
            except Exception:
                pass
        
            ticker_chart = pd.concat([ticker_chart, test_chart], sort=False,)
            ticker_chart.index.name = 'Ticker' # インデックスラベル名を作成

    # infを0に変換
    ticker_chart = ticker_chart.replace([np.inf, -np.inf], np.nan)
    ticker_chart = ticker_chart.fillna(0) # 0でnanを置換
    
    # 保存
    os.makedirs(todayspickup_folder, exist_ok=True)  
    ticker_chart.to_csv(todayspickup_filename, header=True)
    

def create_tickers(date=datetime.datetime.today().date(), debug=False):
    tickers_list = pd.read_csv('tickers_list.csv', header=0, index_col=0)

    if debug:
        tickers_list = tickers_list.head(1000000)

    ticker_chart = pd.DataFrame()
    tickers = tickers_list.index.tolist()
    batch_size = 10

    # バッチごとに処理
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        ticker_str = ' '.join([f"{ticker}.T" for ticker in batch])
        
        try:
            today_data = yfinance.download(tickers=ticker_str, period='1d', interval='1d', group_by='ticker', progress=False, threads=True, auto_adjust=False)
        except Exception as e:
            print(f"Failed batch download: {e}")
            continue

        for ticker in batch:
            print(ticker)
            try:
                file_name = f'{ohlc_folder}/{ticker}.csv'
                chart = pd.read_csv(file_name, index_col=0, parse_dates=True)
                
                # 今日のデータを追加
                today_chart = today_data[ticker + '.T'] if len(batch) > 1 else today_data
                today_chart.index = today_chart.index.normalize()
                chart = pd.concat([chart, today_chart])
                chart = chart[~chart.index.duplicated(keep='last')]
            except Exception as e:
                print(f"Failed to process ticker {ticker}: {e}")
                continue

            if chart.empty:
                print(f"{ticker} chart is empty")
                continue

            chart.sort_index(inplace=True)
            chart = chart[~chart.index.duplicated(keep='last')]

            # 各種指標追加
            row = tickers_list.loc[ticker]
            
            chart, takane = apply_indicators(chart, row)
            today_row = extract_today_row(chart, row, date, takane)

            if today_row is not None:
                ticker_chart = pd.concat([ticker_chart, today_row], sort=False)
    
            # indicator.add_basic(chart, [5, 25, 75, 100, 200])
            # indicator.add_swing_high_low(chart, width=3, only_entitiy=True)
            # indicator.add_candlestick_pattern(chart)
            # indicator.add_sma_pattern(chart)
            # indicator.add_rci(chart, 9)
            # indicator.add_sma_slope(chart)
            # indicator.add_breakout(chart)

            # chart['出来高前日差'] = chart['Volume'].diff()
            # chart['出来高前日比'] = (chart['Volume'] / chart['Volume'].shift(1)).round(1)
            # chart['出来高発行株式割合'] = (chart['Volume'] / row['発行株式'] * 100).round(1)
            # chart['陽線陰線'] = '→'
            # chart['陽線陰線'] = chart['陽線陰線'].mask((chart['Close'] > chart['Open']), '↑')
            # chart['陽線陰線'] = chart['陽線陰線'].mask((chart['Close'] < chart['Open']), '↓')
            
            # chart['75over'] = 0
            # chart.loc[(chart['Close'] > chart['Open']) & (chart['Low'] <= chart['SMA75']) & (chart['High'] > chart['SMA75']), '75over'] = 1
            # chart.loc[(chart['Low'] > chart['SMA75']) & (chart['High'] > chart['SMA75']), '75over'] = 2

            # chart['25over'] = 0
            # chart.loc[(chart['Close'] > chart['Open']) & (chart['Low'] <= chart['SMA25']) & (chart['High'] > chart['SMA25']), '25over'] = 1
            # chart.loc[(chart['Low'] > chart['SMA25']) & (chart['High'] > chart['SMA25']), '25over'] = 2

            # y = chart[chart['SwingHigh'].notna()]
            # takane = y.iloc[-1]['SwingHigh'] if not y.empty else 0
            # chart['Swinghighover'] = chart['Close'] > takane
            # chart['Over75swinghigh'] = chart['Swinghighover'] & chart['crossdSMA75']
            # chart['Hanpatsu75'] = (chart['over75'] > 1) & (chart['Rci'] < -80) & (chart['SMASlope75'] > 0)
            # chart['Perfect2575200'] = (chart['SMA25'] >= chart['SMA75']) & (chart['SMA75'] >= chart['SMA200'])

            # # 最新日のデータだけ保存
            # if date == chart.index[-1].date():
            #     timestamp = chart.index[-1]
            #     try:
            #         test_chart = pd.DataFrame({
            #             '銘柄名': [row['銘柄名']],
            #             '陽線陰線': [chart.at[timestamp, '陽線陰線']],
            #             '出来高': [chart.at[timestamp, 'Volume']],
            #             '出来高前日差': [chart.at[timestamp, '出来高前日差']],
            #             '出来高発行株式割合': [chart.at[timestamp, '出来高発行株式割合']],
            #             '出来高前日比': [chart.at[timestamp, '出来高前日比']],
            #             '三平': [chart.at[timestamp, 'Hei']],
            #             '空': [chart.at[timestamp, 'Ku']],
            #             '25SMA越': [chart.at[timestamp, 'over25']],
            #             '75SMA越': [chart.at[timestamp, 'over75']],
            #             '足1': [chart.at[timestamp, 'Ashi1']],
            #             '足2': [chart.at[timestamp, 'Ashi2']],
            #             '直近高値越': [chart.at[timestamp, 'Swinghighover']],
            #             '75SMAと直近高値越': [chart.at[timestamp, 'Over75swinghigh']],
            #             '直近高値': [takane],
            #             '75反発': [chart.at[timestamp, 'Hanpatsu75']],
            #             'パーフェクトオーダー': [chart.at[timestamp, 'Perfect2575200']],
            #             'RCI': [chart.at[timestamp, 'Rci']],
            #             'ブレークアウト日数': [chart.at[timestamp, 'Breakout']],
            #         }, index=[ticker])
            #         ticker_chart = pd.concat([ticker_chart, test_chart])
            #     except Exception as e:
            #         print(f"Error extracting latest row for {ticker}: {e}")

    ticker_chart.index.name = 'Ticker'
    ticker_chart = ticker_chart.replace([np.inf, -np.inf], np.nan).fillna(0)

    os.makedirs(todayspickup_folder, exist_ok=True)
    ticker_chart.to_csv(todayspickup_filename, header=True)
        
    
def change_view(debug=False):
    
    tickers_list = pd.read_csv(todayspickup_filename, header=0, index_col=0)
    
    if not tickers_list.empty:
        # print(ticker_chart.sort_values(by='出来高発行株式割合', ascending=False).head(100))
        # print('\n')
        # print(ticker_chart.sort_values(by='出来高前日比', ascending=False).head(100))
        print('各特徴量に従って保存します。')
        
        tickers_list = tickers_list.sort_values(by='出来高発行株式割合', ascending=False)
        filename = f'./{todayspickup_folder}/volume_shares.csv'
        tickers_list.loc[tickers_list['出来高発行株式割合']> 10,['銘柄名','出来高発行株式割合','出来高前日比','75SMA越']].to_csv(filename, header=True) # 保存

        tickers_list = tickers_list.sort_values(by='出来高前日比', ascending=False)
        filename = f'./{todayspickup_folder}/volume_previous.csv'
        tickers_list.loc[tickers_list['出来高前日比']>2,['銘柄名','出来高前日比','出来高発行株式割合','75SMA越']].to_csv(filename, header=True) # 保存

        tickers_list = tickers_list.sort_values(by='三平', ascending=False)
        filename = f'./{todayspickup_folder}/akasanpei.csv'
        tickers_list.loc[tickers_list['三平']>2,['銘柄名','三平']].to_csv(filename, header=True) # 保存

        tickers_list = tickers_list.sort_values(by='三平', ascending=False)
        filename = f'./{todayspickup_folder}/akasanpei_rci.csv'
        tickers_list.loc[(tickers_list['三平']>2) & (tickers_list['RCI']<0.0),['銘柄名','三平','RCI','75SMA越','25SMA越']].to_csv(filename, header=True) # 保存
        
        tickers_list = tickers_list.sort_values(by='三平', ascending=True)
        filename = f'./{todayspickup_folder}/kurosanpei.csv'
        tickers_list.loc[tickers_list['三平']<2,['銘柄名','三平']].to_csv(filename, header=True) # 保存

        tickers_list = tickers_list.sort_values(by='三平', ascending=False)
        filename = f'./{todayspickup_folder}/kurosanpei_rci.csv'
        tickers_list.loc[(tickers_list['三平']<2) & (tickers_list['RCI']>0.0),['銘柄名','三平','RCI','75SMA越','25SMA越'],].to_csv(filename, header=True) # 保存
                
        tickers_list = tickers_list.sort_values(by='空', ascending=False)
        filename = f'./{todayspickup_folder}/aka_ku.csv'
        tickers_list.loc[tickers_list['空']>0,['銘柄名','空']].to_csv(filename, header=True) # 保存

        tickers_list = tickers_list.sort_values(by='空', ascending=True)
        filename = f'./{todayspickup_folder}/kuro_ku.csv'
        tickers_list.loc[tickers_list['空']<0,['銘柄名','空']].to_csv(filename, header=True) # 保存
        
        tickers_list = tickers_list.sort_values(by='75SMA越', ascending=True)
        filename = f'./{todayspickup_folder}/over75day.csv'
        tickers_list.loc[tickers_list['75SMA越']>0,['銘柄名','75SMA越','25SMA越','出来高前日比']].to_csv(filename, header=True) # 保存
        
        filename = f'./{todayspickup_folder}/over75high.csv'
        tickers_list.loc[tickers_list['75SMAと直近高値越']==True,['銘柄名','75SMAと直近高値越']].to_csv(filename, header=True) # 保存
        
        tickers_list = tickers_list.sort_values(by='75SMA越', ascending=True)
        filename = f'./{todayspickup_folder}/hanpatsu75.csv'
        tickers_list.loc[tickers_list['75反発']==True,['銘柄名','75反発']].to_csv(filename, header=True) # 保存
        
        tickers_list = tickers_list.sort_values(by='パーフェクトオーダー', ascending=True)
        filename = f'./{todayspickup_folder}/perfect2575200.csv'
        tickers_list.loc[tickers_list['パーフェクトオーダー']==True,['銘柄名','パーフェクトオーダー','75SMA越']].to_csv(filename, header=True) # 保存

        tickers_list = tickers_list.sort_values(by='ブレークアウト日数', ascending=False)
        filename = f'./{todayspickup_folder}/breakout.csv'
        tickers_list.loc[tickers_list['ブレークアウト日数']>0,['銘柄名','ブレークアウト日数','75SMA越']].to_csv(filename, header=True) # 保存
            
if __name__ == "__main__":
    
    os.system('cls')
    

    # pdのprint表示の仕方を設定
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    print(datetime.datetime.now(ZoneInfo("Asia/Tokyo")).date())
    print('today():', datetime.datetime.today())
    print('today().date():', datetime.datetime.today().date())
    print('today().timestamp():', datetime.datetime.today().timestamp())
    
    date2 = datetime.datetime(2025, 6, 3).date()
    print(date2)
    # test(date2)
    # create_tickers(datetime.datetime.today().date(),True)
    create_tickers(date2,True)
    change_view()
    
    # ticker = 4824
    # start = time.time()
    # chart = yfinance.download(tickers=f'{ticker}.T', period='100d', interval='1d', progress=False)
    # print('100 ', time.time() - start)
    # # print(chart)
    # start = time.time()
    # file_name = f'{ohlc_folder}/{ticker}.csv'
    # chart = pd.read_csv(file_name, index_col=0, parse_dates=True)
    # today_chart = yfinance.download(tickers=f'{ticker}.T', period='1d', interval='1d', progress=False)
    # chart = pd.concat([chart, today_chart], sort=True)                
    # chart = chart[~chart.index.duplicated(keep='last')] # 日付に重複があれば最新で更新する
    # print('1 ', time.time() - start)
    # print(chart.tail(100))
