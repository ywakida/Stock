import pandas
import datetime
import math
import os


def add_basic(chart, params=[5, 20, 25, 60, 75, 100, 200]):
    
    for param in params:
        # 単純移動平均 Simple moving average
        chart[f'SMA{param}'] = chart['Close'].rolling(param).mean()
        # chart[f'SMA{param}'].fillna(method='bfill', inplace=True)
        
        # 乖離率 Deviation rate
        # 乖離率は、一定以上のデータがないと有効でない
        chart[f'DR{param}']   = (chart['Close'] - chart[f'SMA{param}']) / chart[f'SMA{param}'] * 100
       
        # 前日からの傾き
        chart[f'Slope{param}'] = chart[f'SMA{param}'].diff(1)
        
        # 傾き変化量
        chart[f'SlopeSlope{param}'] = chart[f'Slope{param}'].diff(1)
        
        # 指数移動平均
        chart[f'EMA{param}'] = chart['Close'].ewm(span=param, adjust=False).mean()
        
        # ボリンジャーバンド
        chart[f'BB{param}P2'] = chart['Close'].rolling(param).mean() + 2 * chart['Close'].rolling(param).std(ddof = 0) # ddof = 0は母集団
        chart[f'BB{param}P1'] = chart['Close'].rolling(param).mean() + 1 * chart['Close'].rolling(param).std(ddof = 0) # ddof = 0は母集団
        chart[f'BB{param}M1'] = chart['Close'].rolling(param).mean() - 1 * chart['Close'].rolling(param).std(ddof = 0) # ddof = 0は母集団
        chart[f'BB{param}M2'] = chart['Close'].rolling(param).mean() - 2 * chart['Close'].rolling(param).std(ddof = 0) # ddof = 0は母集団

        # シグマ値
        chart[f'SIGMA{param}'] = (chart[f'DR{param}'] - chart[f'DR{param}'].mean()) / chart[f'DR{param}'].std()
        
        
# def add_basic(chart, keys={"S":5, "M":20, "L":60, "LL":200}):
#     """ 基本インジケータの追加

#     Args:
#         chart (_type_): _description_
#         keys (dict, optional): _description_. Defaults to {"S":5, "M":20, "L":60, "LL":200}.
#     """
#     for key, value in keys.items():
#         # 単純移動平均 Simple moving average
#         chart[f'SMA{key}'] = chart['Close'].rolling(value).mean() # 5分足の短期移動平均
        
#         # 乖離率 Deviation rate
#         chart[f'DR{key}']   = (chart['Close'] - chart[f'SMA{key}']) / chart[f'SMA{key}'] * 100
       
#         # 前日からの傾き
#         chart[f'Slope{key}'] = chart[f'SMA{key}'].diff(1)
        
#         # 傾き変化量
#         chart[f'SlopeSlope{key}'] = chart[f'Slope{key}'].diff(1)
        
#         # 指数移動平均
#         chart[f'EMA{key}'] = chart['Close'].ewm(span=value, adjust=False).mean()
        
#         chart[f'Median{key}'] = chart['High'].rolling(value, center=True).median()
        
#         # ボリンジャーバンド
#         chart[f'BB{key}P2'] = chart['Close'].rolling(value).mean() + 2 * chart['Close'].rolling(value).std(ddof = 0) # ddof = 0は母集団
#         chart[f'BB{key}P1'] = chart['Close'].rolling(value).mean() + 1 * chart['Close'].rolling(value).std(ddof = 0) # ddof = 0は母集団
#         chart[f'BB{key}M1'] = chart['Close'].rolling(value).mean() - 1 * chart['Close'].rolling(value).std(ddof = 0) # ddof = 0は母集団
#         chart[f'BB{key}M2'] = chart['Close'].rolling(value).mean() - 2 * chart['Close'].rolling(value).std(ddof = 0) # ddof = 0は母集団
        
#         # 変則シグマ
#         # chart[f'SIGMA{key}'] = (chart['Close'] - chart['Close'].rolling(value).mean()) / chart['Close'].rolling(value).std(ddof = 0)  # ddof = 0は母集団
#         # chart[f'SIGMA{key}'].mask((chart[f'SIGMA{key}'] > 0), (chart['High'] - chart['Close'].rolling(value).mean()) / chart['Close'].rolling(value).std(ddof = 0), inplace=True)
#         # chart[f'SIGMA{key}'].mask((chart[f'SIGMA{key}'] < 0), (chart['Low'] - chart['Close'].rolling(value).mean()) / chart['Close'].rolling(value).std(ddof = 0), inplace=True)
#         # # chart[f'SIGMA{key}'] = chart[f'SIGMA{key}'].ewm(span=5, adjust=False).mean()
        
#         # シグマ値
#         chart[f'SIGMA{key}'] = (chart[f'DR{key}'] - chart[f'DR{key}'].mean()) / chart[f'DR{key}'].std()
        
def add_volume(chart, window=5, day=1):
    
    # 平均出来高
    chart[f'Volume{window}'] = chart['Volume'].rolling(window).mean()
    chart[f'Volume{window}_{day}'] = chart[f'Volume{window}'].shift(day)

 
def add_heikinashi(chart):
    """平均足の追加

    Args:
        chart (_type_): _description_
    """
    chart['HA_Close'] = (chart['High'] + chart['Low'] + chart['Open'] + chart['Close']) / 4
    chart['HA_Open'] = (chart['Open'] + chart['Close']) / 2
    chart['HA_Open'] = chart['HA_Open'].shift(1) # 前回の値に変更
    chart['HA_High'] = pandas.concat([chart['HA_Open'], chart['HA_Close'], chart['High']], axis='columns').max(axis='columns')
    chart['HA_Low'] = pandas.concat([chart['HA_Open'], chart['HA_Close'], chart['Low']], axis='columns').min(axis='columns')
    
    # 平均足の陽線と陰線の反転
    chart['HA_Reversal_Plus'] = (chart['HA_Close'] > chart['HA_Open']) & (chart['HA_Close'] < chart['HA_Open']).shift(1)
    chart['HA_Reversal_Minus'] = (chart['HA_Close'] < chart['HA_Open']) & (chart['HA_Close'] > chart['HA_Open']).shift(1)
    
    # 陽線が1, 陰線が-1
    chart['HA_3V'] = 0
    chart['HA_3V'].mask((chart['HA_Close'] > chart['HA_Open']), 1, inplace=True)
    chart['HA_3V'].mask((chart['HA_Close'] < chart['HA_Open']), -1, inplace=True)
    
    # 平均足の実体差(=陽線、陰線判定)　陽線が>0, 陰線が<0
    chart['HA_BodyDiff'] = chart['HA_Close'] - chart['HA_Open']

def add_swing_high_low(chart, width=11):
    """スイングハイ、ローの検出

    Args:
        chart (_type_): _description_
        width (int, optional): _description_. Defaults to 5.
    """
    # 直近高値、直近安値の計算
    chart[f'SwingHigh'] = 0
    chart[f'SwingHigh'].mask((chart['High'].rolling(width, center=True).max() == chart['High']), chart['High'], inplace=True)
    chart[f'SwingLow'] = 0
    chart[f'SwingLow'].mask((chart['Low'].rolling(width, center=True).min() == chart['Low']), chart['Low'], inplace=True)


def add_before(chart, day=1):
    """X日前の値

    Args:
        chart (_type_): チャート
        day (int, optional): day. Defaults to 1.
    """
    chart[f'OpenBefore{day}'] = chart['Open'].shift(day)
    chart[f'HighBefore{day}'] = chart['High'].shift(day)
    chart[f'LowBefore{day}'] = chart['Low'].shift(day)
    chart[f'CloseBefore{day}'] = chart['Close'].shift(day)

def add_candlestick_pattern(chart):
    """ローソク足のパターンの追加

    Args:
        chart (_type_): チャート
        day (int, optional): day. Defaults to 1.
    """
    # 実体の差分(陽線>0、陰線<0)
    chart['BodyDiff'] = chart['Close'] - chart['Open']
    chart['Ashi1'] = 'なし'
    chart['Ashi1'].mask((chart['Open']<chart['Close']) & (chart['Open']==chart['Low']) & (chart['Close']==chart['High']), '陽の丸坊主', inplace=True) # 強気線
    chart['Ashi1'].mask((chart['Open']<chart['Close']) & (chart['Open']==chart['Low']) & (chart['Close']<chart['High']), '陽の寄付坊主', inplace=True) # 強気線・上値暗示
    chart['Ashi1'].mask((chart['Open']<chart['Close']) & (chart['Open']>chart['Low']) & (chart['Close']==chart['High']), '陽の大引坊主', inplace=True) # 強気線・上値暗示
    chart['Ashi1'].mask((chart['Open']<chart['Close']) & (chart['Open']>chart['Low']) & (chart['Close']<chart['High']), 'コマ・陽の極線', inplace=True) # 迷い
    
    chart['Ashi1'].mask((chart['Open']>chart['Close']) & (chart['Close']==chart['Low']) & (chart['Open']==chart['High']), '陰の丸坊主', inplace=True) # 弱気線    
    chart['Ashi1'].mask((chart['Open']>chart['Close']) & (chart['Close']==chart['Low']) & (chart['Open']<chart['High']), '陰の大引坊主', inplace=True) # 弱気線・下値暗示
    chart['Ashi1'].mask((chart['Open']>chart['Close']) & (chart['Close']>chart['Low']) & (chart['Open']==chart['High']), '陰の寄付坊主', inplace=True) # 弱気線・下値暗示
    chart['Ashi1'].mask((chart['Open']>chart['Close']) & (chart['Close']>chart['Low']) & (chart['Open']<chart['High']), 'コマ・陰の極線', inplace=True) # 迷い
    
    chart['Ashi1'].mask((chart['Open']==chart['Close']) & (chart['Open']==chart['High']) & (chart['Close']>chart['Low']), 'トンボ', inplace=True) # 転換期
    
    
    
    # > : 連続陽線で実体がひとつ前より上がっている数
    # < : 連続陰線で実体がひとつ前より下がっている数
    chart['Hei'] = 0
    chart['Hei'].mask((chart['Close'] > chart['Open']) & (chart['Close'].shift() > chart['Open'].shift()) & (chart['Close'] >= chart['Close'].shift()) & (chart['Open'] >= chart['Open'].shift()), 1, inplace=True)
    chart['Hei'].mask((chart['Close'] < chart['Open']) & (chart['Close'].shift() < chart['Open'].shift()) & (chart['Close'] <= chart['Close'].shift()) & (chart['Open'] <= chart['Open'].shift()), -1, inplace=True)
    y = chart['Hei'].groupby((chart['Hei'] != chart['Hei'].shift()).cumsum()).cumcount() + 1 # 同じ数が連続している個数を算出
    chart['Hei'] = chart['Hei'] * y
    

import chart_plot
if __name__ == "__main__":
    
    os.system('cls')

    # pandasのprint表示の仕方を設定
    pandas.set_option('display.max_rows', None)
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.width', 1000)
    
    df = pandas.DataFrame(data=[0, 0, 1, 1, 1, -1, -1, -1, -1], columns=['value'])
    
    y = df['value']
    df['count'] = y.groupby((y != y.shift()).cumsum()).cumcount() + 1
    df['value'] = df['count'] * df['value']
    print(df)
    
    tickers_list = pandas.read_csv('tickers_list.csv', header=0, index_col=0)
    tickers_list = tickers_list.head(100)

    for ticker, row in tickers_list.iterrows():
        folder = 'yfinance_csv'
        
        chart_filename = f'{folder}/{ticker}.csv'
        if os.path.exists(chart_filename):
            print(f"{ticker}.csv is exsisted.")
    
            # open chart csv file
            chart = pandas.DataFrame()
            chart =  pandas.read_csv(chart_filename, index_col=0, parse_dates=True)
            
            add_candlestick_pattern(chart)
            add_basic(chart)
            add_swing_high_low(chart)
            
            # print(chart)
            
            save_filename = f'./html/{ticker}_.html'
            chart_plot.plot_basicchart(save_filename, ticker, chart.tail(300), auto_open=False)
                