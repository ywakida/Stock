import pandas
import os
import numpy
import chart_days

def add_sma(chart, params=[5, 25, 75]):
    """ 単純移動平均線の追加
    """
    for param in params:
        if not f'SMA{param}' in chart.columns:
            chart[f'SMA{param}'] = chart['Close'].rolling(param).mean() 
            
    return chart

def add_sma_dr(chart, params=[5, 25, 75]):
    """ 単純移動平均線からの乖離率(%)
    """
    for param in params:
        if f'SMA{param}' in chart.columns:
            chart[f'SMADR{param}']   = (chart['Close'] - chart[f'SMA{param}']) / chart[f'SMA{param}'] * 100
            
    return chart
        
def add_sma_slope(chart, params=[5, 25, 75], base=1):
    """ シグマ
    """     
    for param in params:
        if f'SMA{param}' in chart.columns:
            chart[f'SMASlope{param}'] = chart[f'SMA{param}'].diff() * base
    
    return chart
            
def add_ema(chart, params=[5, 25, 75]):
    """ 指数移動平均線の追加
    """
    for param in params:
        if not f'EMA{param}' in chart.columns:
            chart[f'EMA{param}'] = chart['Close'].ewm(span=param, adjust=False).mean()
    
    return chart
        
def add_ema_dr(chart, params=[5, 25, 75]):
    """ 指数移動平均線からの乖離率(%)
    """
    for param in params:
        if f'EMA{param}' in chart.columns:
            chart[f'EMADR{param}']   = (chart['Close'] - chart[f'EMA{param}']) / chart[f'EMA{param}'] * 100

    return chart

def add_ema_slope(chart, params=[20], base=1):
    """ シグマ
    """     
    for param in params:
        if f'EMA{param}' in chart.columns:
            chart[f'EMASlope{param}'] = chart[f'EMA{param}'].diff() * base

    return chart

def add_bb(chart, params=[5, 20, 60]):
    """ ボリンジャーバンド
    """
    for param in params:
        chart[f'BB{param}P2'] = chart['Close'].rolling(param).mean() + 2 * chart['Close'].rolling(param).std(ddof = 0) # ddof = 0は母集団
        chart[f'BB{param}P1'] = chart['Close'].rolling(param).mean() + 1 * chart['Close'].rolling(param).std(ddof = 0) # ddof = 0は母集団
        chart[f'BB{param}M1'] = chart['Close'].rolling(param).mean() - 1 * chart['Close'].rolling(param).std(ddof = 0) # ddof = 0は母集団
        chart[f'BB{param}M2'] = chart['Close'].rolling(param).mean() - 2 * chart['Close'].rolling(param).std(ddof = 0) # ddof = 0は母集団
    
    return chart

def add_sigma(chart, params=[20]):
    """ シグマ
    """     
    for param in params:
        chart[f'SIGMA{param}'] = (chart['Close'] - chart['Close'].rolling(param).mean()) / chart['Close'].rolling(param).std(ddof = 0)  # ddof = 0は母集団 
        chart[f'SIGMA{param}'] = chart[f'SIGMA{param}'].mask((chart[f'SIGMA{param}'] >= 0), (chart['High'] - chart['Close'].rolling(param).mean()) / chart['Close'].rolling(param).std(ddof = 0)),
        chart[f'SIGMA{param}'] = chart[f'SIGMA{param}'].mask((chart[f'SIGMA{param}'] < 0), (chart['Low'] - chart['Close'].rolling(param).mean()) / chart['Close'].rolling(param).std(ddof = 0))
        # chart[f'SIGMA{param}'] = chart[f'SIGMA{param}'].ewm(span=5, adjust=False).mean()
    
    return chart 

def add_basic(chart, params=[5, 20, 25, 60, 75, 100, 200]):
    
    for param in params:
        # 単純移動平均 Simple moving average
        chart[f'SMA{param}'] = chart['Close'].rolling(window=param, min_periods=1).mean()
        # chart[f'SMA{param}'] = chart[f'SMA{param}'].bfill()
        
        # 乖離率 Deviation rate
        # 乖離率は、一定以上のデータがないと有効でない
        chart[f'DR{param}']   = (chart['Close'] - chart[f'SMA{param}']) / chart[f'SMA{param}'] * 100
       
        # 前日からの傾き
        chart[f'Slope{param}'] = chart[f'SMA{param}'].diff(1)
        
        # 傾き変化量
        chart[f'SlopeSlope{param}'] = chart[f'Slope{param}'].diff(1)
        
        # 指数移動平均
        chart[f'EMA{param}'] = chart['Close'].ewm(span=param, adjust=False, min_periods=1).mean()
        
        # ボリンジャーバンド
        chart[f'BB{param}P2'] = chart['Close'].rolling(window=param, min_periods=1).mean() + 2 * chart['Close'].rolling(window=param, min_periods=1).std(ddof = 0) # ddof = 0は母集団
        chart[f'BB{param}P1'] = chart['Close'].rolling(window=param, min_periods=1).mean() + 1 * chart['Close'].rolling(window=param, min_periods=1).std(ddof = 0) # ddof = 0は母集団
        chart[f'BB{param}M1'] = chart['Close'].rolling(window=param, min_periods=1).mean() - 1 * chart['Close'].rolling(window=param, min_periods=1).std(ddof = 0) # ddof = 0は母集団
        chart[f'BB{param}M2'] = chart['Close'].rolling(window=param, min_periods=1).mean() - 2 * chart['Close'].rolling(window=param, min_periods=1).std(ddof = 0) # ddof = 0は母集団

        # シグマ値
        chart[f'SIGMA{param}'] = (chart[f'DR{param}'] - chart[f'DR{param}'].mean()) / chart[f'DR{param}'].std()
    
    return chart

def add_volume(chart, window=5, day=1):
    
    # 平均出来高
    chart[f'Volume{window}'] = chart['Volume'].rolling(window).mean()
    chart[f'Volume{window}_{day}'] = chart[f'Volume{window}'].shift(day)
    return chart

def calc_rci(prices):
    """ RCI 計算関数
    """
    day_cnt = len(prices)
    # 日付昇順ランク
    rank_day = numpy.arange(day_cnt) + 1
    # 株価昇順ランク
    rank_price = numpy.array(pandas.Series(prices).rank())
    rci = 1 - (6 * ((rank_day - rank_price)**2).sum()) / (day_cnt * (day_cnt**2 - 1))
    return rci * 100 # パーセント値で返却

def add_rci(chart, days=9):
    """ RCIの追加
    """        
    chart['Rci'] = chart['Close'].rolling(days).apply(calc_rci, raw=True)
    return chart

def create_heikinashi(chart):
    """平均足の追加
    """
    new_chart = pandas.DataFrame() 
    
    param = 3
    if param == 0:
        new_chart['Close'] = (chart['High'] + chart['Low'] + chart['Open'] + chart['Close']) / 4
        new_chart['Open'] = (chart['Open'] + chart['Close']) / 2
    else:
        ad = True
        new_chart['Close'] = (chart['High'].ewm(span=param, adjust=ad).mean() + chart['Low'].ewm(span=param, adjust=ad).mean() + chart['Open'].ewm(span=param, adjust=ad).mean() + chart['Close'].ewm(span=param, adjust=ad).mean()) / 4
        new_chart['Open'] = (chart['Open'].ewm(span=param, adjust=ad).mean() + chart['Close'].ewm(span=param, adjust=ad).mean()) / 2

    new_chart['Open'] = chart['Open'].shift(1) # 前回の値に変更
    new_chart['High'] = pandas.concat([chart['Open'], chart['Close'], chart['High']], axis='columns').max(axis='columns')
    new_chart['Low'] = pandas.concat([chart['Open'], chart['Close'], chart['Low']], axis='columns').min(axis='columns')

    diff = 0
    if diff != 0:
        new_chart['Close'] = new_chart['Close'] - diff
        new_chart['Open'] = new_chart['Open'] - diff
        new_chart['High'] = new_chart['High'] - diff
        new_chart['Low'] = new_chart['Low'] - diff    
    
    # 平均足の陽線と陰線の反転
    new_chart['N2P'] = (chart['Close'] > chart['Open']) & (chart['Close'] < chart['Open']).shift(1) # Negative to Positive
    new_chart['P2N'] = (chart['Close'] < chart['Open']) & (chart['Close'] > chart['Open']).shift(1) # Positive to Negative
    
    return new_chart
        
def add_heikinashi(chart):
    """平均足の追加
    """
    diff = 200
    chart['HA_Close'] = (chart['High'] + chart['Low'] + chart['Open'] + chart['Close']) / 4
    chart['HA_Open'] = (chart['Open'] + chart['Close']) / 2
    chart['HA_Open'] = chart['HA_Open'].shift(1) # 前回の値に変更
    chart['HA_High'] = pandas.concat([chart['HA_Open'], chart['HA_Close'], chart['High']], axis='columns').max(axis='columns') - diff
    chart['HA_Low'] = pandas.concat([chart['HA_Open'], chart['HA_Close'], chart['Low']], axis='columns').min(axis='columns') - diff
    chart['HA_Close'] = chart['HA_Close'] - diff
    chart['HA_Open'] = chart['HA_Open'] - diff
    
    
    # 平均足の陽線と陰線の反転
    chart['HA_Reversal_Plus'] = (chart['HA_Close'] > chart['HA_Open']) & (chart['HA_Close'] < chart['HA_Open']).shift(1)
    chart['HA_Reversal_Minus'] = (chart['HA_Close'] < chart['HA_Open']) & (chart['HA_Close'] > chart['HA_Open']).shift(1)
    
    # 陽線が1, 陰線が-1
    chart['HA_3V'] = 0
    chart['HA_3V'] = chart['HA_3V'].mask((chart['HA_Close'] > chart['HA_Open']), 1)
    chart['HA_3V'] = chart['HA_3V'].mask((chart['HA_Close'] < chart['HA_Open']), -1)
    
    # 平均足の実体差(=陽線、陰線判定)　陽線が>0, 陰線が<0
    chart['HA_BodyDiff'] = chart['HA_Close'] - chart['HA_Open']
    
    return chart
    
def add_swing_high_low(chart, width=5, fill=False, only_entitiy=True):
    """スイングハイ、ローの検出
    """
    # 直近高値、直近安値の計算
    window=width * 2 + 1
    chart[f'SwingHigh'] = numpy.nan
    chart[f'SwingLow'] = numpy.nan
    if only_entitiy:
        high = chart[['Open', 'Close']].max(axis=1)
        low = chart[['Open', 'Close']].min(axis=1)
        chart[f'SwingHigh'] = chart[f'SwingHigh'].mask((high.rolling(window, center=True).max() == high), high)
        chart[f'SwingLow'] = chart[f'SwingLow'].mask((low.rolling(window, center=True).min() == low), low)
    else:
        chart[f'SwingHigh'] = chart[f'SwingHigh'].mask((chart['High'].rolling(window, center=True).max() == chart['High']), chart['High'])
        chart[f'SwingLow'] = chart[f'SwingLow'].mask((chart['Low'].rolling(window, center=True).min() == chart['Low']), chart['Low'])

    if fill:
        chart[f'SwingHigh'] = chart[f'SwingHigh'].ffill()
        chart[f'SwingLow'] = chart[f'SwingLow'].ffill()
        
    return chart

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
    
    return chart
    

def add_sma_pattern(chart, param=[25, 75, 100]):
    # 連続して、SMAを超えた回数をカウントする
    for sma in param:
        if f'SMA{sma}' in chart.columns:
            # 連続してSMAを終値が超えている回数
            # chart[f'over{sma}'] = 0
            # chart[f'over{sma}'] = chart[f'over{sma}'].mask((chart['Close'] > chart[f'SMA{sma}']), 1)
            # y = chart[f'over{sma}'].groupby((chart[f'over{sma}'] != chart[f'over{sma}'].shift()).cumsum()).cumcount() + 1 # 同じ数が連続している個数を算出
            # chart[f'over{sma}'] = chart[f'over{sma}'] * y
            # 条件を満たすフラグ列（True: Close > SMA）
            flag = chart['Close'] > chart[f'SMA{sma}']
            chart[f'over{sma}'] = flag.groupby((~flag).cumsum()).cumcount() + 1 # Trueの連続回数をカウント（Falseになったらリセット）
            chart[f'over{sma}'] = chart[f'over{sma}'] * flag.astype(int)    # Falseのところは0に

            # 連続して下値を切り上げている回数
            chart[f'UnderUp'] = 0
            chart[f'UnderUp'] = chart[f'UnderUp'].mask(chart[['Close', 'Open']].min(axis='columns') > chart[['Close', 'Open']].min(axis='columns').shift(), 1)
            y = chart[f'UnderUp'].groupby((chart[f'UnderUp'] != chart[f'UnderUp'].shift()).cumsum()).cumcount() + 1 # 同じ数が連続している個数を算出
            chart[f'UnderUp'] = chart[f'UnderUp'] * y
            
            # 連続して下値を切り上げている回数の最大
            chart[f'UnderUpHigh'] = numpy.nan
            chart[f'UnderUpHigh'] = chart[f'UnderUpHigh'].mask((chart['UnderUp'].rolling(3, center=True).max() == chart['UnderUp']), chart['UnderUp'])
            chart[f'UnderUpHigh'] = chart[f'UnderUpHigh'].mask(chart['UnderUp'] == 0, 0)
            # chart[f'UnderUpHigh'] = chart[f'UnderUpHigh'].fillna(method='bfill')
            chart[f'UnderUpHigh'] = chart[f'UnderUpHigh'].bfill()
            chart[f'UnderUpHigh'] = chart[f'UnderUpHigh'].fillna(chart['UnderUp'].iloc[-1])
        
            # 前日終値がSMAより低く、かつ、当日、始値がSMAより低いところから、終値がSMAを超えたかを確認する（当日の陽線およびSMAクロス、または、前日SMAより下で、当日SMAより上の陽線)
            # chart[f'crossdSMA{sma}'] = (chart['Close'] > chart['Open']) & (chart['Close'] > chart[f'SMA{sma}']) & ( (chart['Open'] < chart[f'SMA{sma}']) | (chart['Close'].shift(1) < chart[f'SMA{sma}'])) # True/False 陽線
            
            # 陽線でも陰線でもよいが、SMAを超えたかを確認する
            chart[f'crossdSMA{sma}'] = (chart['Close'] > chart[f'SMA{sma}']) & ( (chart['Open'] < chart[f'SMA{sma}']) | (chart['Close'].shift(1) < chart[f'SMA{sma}'])) # True/False 陽線

    return chart
        
def add_candlestick_pattern(chart):
    """ローソク足のパターンの追加

    Args:
        chart (_type_): チャート
        day (int, optional): day. Defaults to 1.
    """
    # 実体の差分(陽線>0、陰線<0)
    chart['BodyDiff'] = chart['Close'] - chart['Open']
    chart['Ashi1'] = 'なし'
    chart['Ashi1'] = chart['Ashi1'].mask((chart['Open']<chart['Close']) & (chart['Open']==chart['Low']) & (chart['Close']==chart['High']), '陽の丸坊主') # 強気線
    chart['Ashi1'] = chart['Ashi1'].mask((chart['Open']<chart['Close']) & (chart['Open']==chart['Low']) & (chart['Close']<chart['High']), '陽の寄付坊主') # 強気線・上値暗示
    chart['Ashi1'] = chart['Ashi1'].mask((chart['Open']<chart['Close']) & (chart['Open']>chart['Low']) & (chart['Close']==chart['High']), '陽の大引坊主') # 強気線・上値暗示
    chart['Ashi1'] = chart['Ashi1'].mask((chart['Open']<chart['Close']) & (chart['Open']>chart['Low']) & (chart['Close']<chart['High']), 'コマ・陽の極線') # 迷い
    
    chart['Ashi1'] = chart['Ashi1'].mask((chart['Open']>chart['Close']) & (chart['Close']==chart['Low']) & (chart['Open']==chart['High']), '陰の丸坊主') # 弱気線    
    chart['Ashi1'] = chart['Ashi1'].mask((chart['Open']>chart['Close']) & (chart['Close']==chart['Low']) & (chart['Open']<chart['High']), '陰の大引坊主') # 弱気線・下値暗示
    chart['Ashi1'] = chart['Ashi1'].mask((chart['Open']>chart['Close']) & (chart['Close']>chart['Low']) & (chart['Open']==chart['High']), '陰の寄付坊主') # 弱気線・下値暗示
    chart['Ashi1'] = chart['Ashi1'].mask((chart['Open']>chart['Close']) & (chart['Close']>chart['Low']) & (chart['Open']<chart['High']), 'コマ・陰の極線') # 迷い
    
    chart['Ashi1'] = chart['Ashi1'].mask((chart['Open']==chart['Close']) & (chart['Open']==chart['High']) & (chart['Close']>chart['Low']), 'トンボ') # 転換期
    
    chart['Ashi2'] = 'なし'

    # はらみ線
    # 高値圏で出現すれば天井
    chart['Ashi2'] = chart['Ashi2'].mask((chart['Open']<chart['Close']) & (chart['Open'].shift()<chart['Close'].shift()) & (chart['Open']>chart['Open'].shift()) & (chart['Close']<chart['Close'].shift()), '陽の陽はらみ(高値圏で天井)')
    chart['Ashi2'] = chart['Ashi2'].mask((chart['Open']>chart['Close']) & (chart['Open'].shift()<chart['Close'].shift()) & (chart['Open']<chart['Close'].shift()) & (chart['Close']>chart['Open'].shift()), '陽の陰はらみ(高値圏で天井)')
    # 安値圏で出現すれば底
    chart['Ashi2'] = chart['Ashi2'].mask((chart['Open']>chart['Close']) & (chart['Open'].shift()>chart['Close'].shift()) & (chart['Open']<chart['Open'].shift()) & (chart['Close']>chart['Close'].shift()), '陰の陰はらみ(安値圏で底)')
    chart['Ashi2'] = chart['Ashi2'].mask((chart['Open']<chart['Close']) & (chart['Open'].shift()>chart['Close'].shift()) & (chart['Open']>chart['Close'].shift()) & (chart['Close']<chart['Open'].shift()), '陰の陽はらみ(安値圏で底)')
    
    # つつみ線
    chart['Ashi2'] = chart['Ashi2'].mask((chart['Open']<chart['Close']) & (chart['Open'].shift()<chart['Close'].shift()) & (chart['Open']<chart['Open'].shift()) & (chart['Close']>chart['Close'].shift()), '陽の陽つつみ')
    chart['Ashi2'] = chart['Ashi2'].mask((chart['Open']<chart['Close']) & (chart['Open'].shift()>chart['Close'].shift()) & (chart['Open']<chart['Close'].shift()) & (chart['Close']>chart['Open'].shift()), '陰の陽つつみ(下落から上昇)')
    chart['Ashi2'] = chart['Ashi2'].mask((chart['Open']>chart['Close']) & (chart['Open'].shift()<chart['Close'].shift()) & (chart['Open']>chart['Close'].shift()) & (chart['Close']<chart['Open'].shift()), '陽の陰つつみ')
    chart['Ashi2'] = chart['Ashi2'].mask((chart['Open']>chart['Close']) & (chart['Open'].shift()>chart['Close'].shift()) & (chart['Open']>chart['Open'].shift()) & (chart['Close']<chart['Close'].shift()), '陰の陰つつみ(上昇から下落)')

    # 出会い線
    deai_diff=1
    # 上昇基調のなかでは買いのサインです。
    chart['Ashi2'] = chart['Ashi2'].mask((chart['Open']<chart['Close']) & (chart['Open'].shift()>chart['Close'].shift()) & (chart['Close']>=chart['Close'].shift()-deai_diff) & (chart['Close']<=chart['Close'].shift()+deai_diff), '陽振り分け(買い圧強)')
    # 下落基調の中では売りのサインです。
    chart['Ashi2'] = chart['Ashi2'].mask((chart['Open']>chart['Close']) & (chart['Open'].shift()<chart['Close'].shift()) & (chart['Close']>=chart['Close'].shift()-deai_diff) & (chart['Close']<=chart['Close'].shift()+deai_diff), '陰振り分け(売り圧強)') 

    # 振り分け線
    furiwake_diff=1
    # 上昇基調のなかでは買いのサインです。
    chart['Ashi2'] = chart['Ashi2'].mask((chart['Open']<chart['Close']) & (chart['Open'].shift()>chart['Close'].shift()) & (chart['Open']>=chart['Open'].shift()-furiwake_diff) & (chart['Open']<=chart['Open'].shift()+furiwake_diff), '陽振り分け(上昇中買い)')
    # 下落基調の中では売りのサインです。
    chart['Ashi2'] = chart['Ashi2'].mask((chart['Open']>chart['Close']) & (chart['Open'].shift()<chart['Close'].shift()) & (chart['Open']>=chart['Open'].shift()-furiwake_diff) & (chart['Open']<=chart['Open'].shift()+furiwake_diff), '陰振り分け(下落中売り)')    
    
    # たすき線
    # 下落基調では売りのサインです。逆のサイント勘違いしやすい
    chart['Ashi2'] = chart['Ashi2'].mask((chart['Open']<chart['Close']) & (chart['Open'].shift()>chart['Close'].shift()) & (chart['Open']>chart['Close'].shift()) & (chart['Close']>chart['Open'].shift()), '陽たすき(下落中売り)')
    # 上昇基調では買いのサインです。逆のサイント勘違いしやすい
    chart['Ashi2'] = chart['Ashi2'].mask((chart['Open']>chart['Close']) & (chart['Open'].shift()<chart['Close'].shift()) & (chart['Open']<chart['Close'].shift()) & (chart['Close']<chart['Open'].shift()), '陰たすき(上昇中買い)')


    # 毛抜き天井・毛抜き底
    kenuki_diff=1
    # 2営業日の高値がほぼ同じ水準の場合。陰線・陽線の組み合わせは問いません。高値圏で現れれば天井が意識されているサインです。
    chart['Ashi2'] = chart['Ashi2'].mask((chart['High']>=chart['High'].shift()-kenuki_diff) & (chart['High']<=chart['High'].shift()+kenuki_diff), '毛抜き天井(高値圏売り)')
    # 2営業日の安値がほぼ同じ水準の場合。陰線・陽線の組み合わせは問いません。安値圏で現れればそこが底値として意識されるサインです。
    chart['Ashi2'] = chart['Ashi2'].mask((chart['Low']>=chart['Low'].shift()-kenuki_diff) & (chart['Low']<=chart['Low'].shift()+kenuki_diff), '毛抜き底(安値圏買い)')

    
    
    # > : 連続陽線で実体がひとつ前より上がっている数
    # < : 連続陰線で実体がひとつ前より下がっている数
    chart['Hei'] = 0
    chart['Hei'] = chart['Hei'].mask((chart['Close'] > chart['Open']) & (chart['Close'].shift() > chart['Open'].shift()) & (chart['Close'] >= chart['Close'].shift()) & (chart['Open'] >= chart['Open'].shift()), 1)
    chart['Hei'] = chart['Hei'].mask((chart['Close'] < chart['Open']) & (chart['Close'].shift() < chart['Open'].shift()) & (chart['Close'] <= chart['Close'].shift()) & (chart['Open'] <= chart['Open'].shift()), -1)
    y = chart['Hei'].groupby((chart['Hei'] != chart['Hei'].shift()).cumsum()).cumcount() + 2 # 同じ数が連続している個数を算出
    chart['Hei'] = chart['Hei'] * y
    
    # 空
    chart['Ku'] = 0
    chart['Ku'] = chart['Ku'].mask((chart['Low'] > chart['High'].shift()), 1)
    chart['Ku'] = chart['Ku'].mask((chart['High'] < chart['Low'].shift()), -1)
    y = chart['Ku'].groupby((chart['Ku'] != chart['Ku'].shift()).cumsum()).cumcount() + 1 # 同じ数が連続している個数を算出
    chart['Ku'] = chart['Ku'] * y
    
    return chart

def add_breakout(chart, max=120):
    """ 過去何日分を超えたかを知る
    """
    sample=5
    chart['Breakout'] = 0
    for N in range(sample, max, sample):  # sampleからmaxまでsample刻み（含む）
        rolling_max = chart['High'].rolling(window=N, min_periods=1).max().shift(1)
        chart['Breakout'] = chart['Breakout'].mask(chart['Close'] > rolling_max, N)
        
    return chart

import chart_plot
if __name__ == "__main__":
    
    os.system('cls')

    # pandasのprint表示の仕方を設定
    pandas.set_option('display.max_rows', None)
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.width', 1000)
    
    # df = pandas.DataFrame(data=[0, 0, 1, 1, 1, -1, -1, -1, -1], columns=['value'])
    
    # y = df['value']
    # df['count'] = y.groupby((y != y.shift()).cumsum()).cumcount() + 1
    # df['value'] = df['count'] * df['value']
    # print(df)    
    
    tickers_list = pandas.read_csv('tickers_list.csv', header=0, index_col=0)
    # tickers_list = pandas.read_csv('todayspickup/over75high.csv', header=0, index_col=0)
    # tickers_list = tickers_list.head(1)
    # tickers_list = tickers_list[tickers_list.index == 2934]
    # tickers_list = tickers_list[tickers_list.index == 6573] # アジャイル
    # tickers_list = tickers_list[tickers_list.index == 4934] # プレミアアンチエイジング
    # tickers_list = tickers_list[tickers_list.index == 1605] # INPEX
    # tickers_list = tickers_list[tickers_list.index == 4263] # サスメド
    # tickers_list = tickers_list[tickers_list.index == 3778] # さくらインターネット
    # tickers_list = tickers_list[tickers_list.index == 9522] # リニューアルブル 
    # tickers_list = tickers_list[tickers_list.index == 6194] # アトラエ
    # tickers_list = tickers_list[tickers_list.index == '4435'] # カオナビ
    tickers_list = tickers_list[tickers_list.index == '1418'] # インターライフ
    
    print(tickers_list)
    
    folder = chart_days.daily_all_folder
    for ticker, row in tickers_list.iterrows():
        
        chart_filename = f'{folder}/{ticker}.csv'
        if os.path.exists(chart_filename):
            print(f"{ticker}.csv is exsisted.")
    
            # open chart csv file
            chart = pandas.DataFrame()
            chart =  pandas.read_csv(chart_filename, index_col=0, parse_dates=True)

            # chart = chart[~chart.index.duplicated(keep='last')]        
            # chart.sort_index(inplace=True)
            # print(chart.tail(100))    
            # print(chart[chart['Close'] <2000])
            
            # add_basic(chart)            
            # add_rci(chart)
            # add_swing_high_low(chart, width=2, only_entitiy=True, fill=True)
            # add_heikinashi(chart)
            # add_candlestick_pattern(chart)
            # add_sma_pattern(chart)
            add_breakout(chart)
            # print(chart[['High', 'SwingHigh']].tail(100))
            
            # chart = create_heikinashi(chart)
            # add_basic(chart)
            print(chart.tail(200))
            
            
            
            add_swing_high_low(chart, width=2, only_entitiy=True, fill=False)
            save_folder = 'html'
            os.makedirs(save_folder, exist_ok=True) 
            save_filename = f'./{save_folder}/{ticker}.html'
            chart_plot.plot_simulationchart(save_filename, ticker, chart.tail(100), auto_open=False)
