import pandas
import datetime
import math
import os


def add_basic(chart, params=[5, 20, 25, 60, 75]):
    
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

def add_swing_high_low(chart, width=11):
    """スイングハイ、ローの検出

    Args:
        chart (_type_): _description_
        width (int, optional): _description_. Defaults to 5.
    """
    # 直近高値、直近安値の計算
    chart[f'SwingHigh{width}'] = 0
    chart[f'SwingHigh{width}'].mask((chart['High'].rolling(width, center=True).max() == chart['High']), chart['High'], inplace=True)
    chart[f'SwingLow{width}'] = 0
    chart[f'SwingLow{width}'].mask((chart['Low'].rolling(width, center=True).min() == chart['Low']), chart['Low'], inplace=True)


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



if __name__ == "__main__":
    
    os.system('cls')

    # # pandasのprint表示の仕方を設定
    # pandas.set_option('display.max_rows', None)
    # pandas.set_option('display.max_columns', None)
    # pandas.set_option('display.width', 1000)
    
    # # currencies = ['USDJPY', 'EURJPY', 'GBPJPY', 'AUDJPY', 'EURUSD', 'GBPUSD', 'AUDUSD']
    # currencies = ['USDJPY']
    # for currency in currencies:
    #     file_name = f'_chart_csv/{currency}_5m.csv'
    #     if os.path.exists(file_name):
            
    #         chart_5m =  pandas.read_csv(file_name, index_col=0, parse_dates=True)
    #         add_heikinashi(chart_5m)
            
            
    #     else:
    #         print(f"{file_name} is not exsisted.")
            
    
        


#       短期、中期、長期　
# 1M,   5M,         20M,        60M
# 5M,   25M,        100M=1H20M, 300M=5H
# 15M,  75M=1H15M,  300M=5H,    900M=15H 
# 1H,   5H,         20H,        60H=2D12H
# 4H,   20H,        80H=3D8H,   240H=10D
# 8H,   40H=1D16H,  160H=6D16H, 480H=20D
# 1D,   5D,         20D,        60D
# 1W,   20D=1M,     60D=3M,        120D=6M
