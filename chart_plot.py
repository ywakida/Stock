import pandas
import plotly.graph_objects as go
import plotly.offline
import plotly.io
from plotly.subplots import make_subplots

def add_graphsetting(figure):
    """グラフの全体設定

    Args:
        figure (_type_): _description_
    """
    # 背景やグラフの色の設定
    figure.update_layout(plot_bgcolor="black", paper_bgcolor="grey") # グラフの背景と全体の背景の設定
    figure.update_xaxes(linecolor='black', gridcolor='gray',mirror=True)
    figure.update_yaxes(linecolor='black', gridcolor='gray',mirror=True)
    
    # グラフのサイズ調整
    figure.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    
    # 凡例
    figure.update_layout(showlegend=True) # 表示設定
    figure.update_layout(legend=dict(xanchor='left', yanchor='top')) # 縦揃え、横揃え
    figure.update_layout(legend=dict(bgcolor='gray', bordercolor='white', borderwidth=1)) # 背景色、枠の色、枠の太さ
    figure.update_layout(legend=dict(x=1.002, y=0.98))

    
    # フォントの設定
    figure.update_layout(font=dict(size=10, color='white'))
    
    
    return figure
    
    
def add_candlestick(figure, chart, row=1, col=1, keys={"S":5, "M":20, "L":60, "LL":200}):
    """ろうそく足のプロット情報作成

    Args:
        filename (_type_): _description_
        currency (_type_): _description_
        chart (_type_): _description_
        keys (dict, optional): _description_. Defaults to {"S":5, "M":20, "L":60, "LL":200}.

    Returns:
        _type_: _description_
    """
    # y軸名を定義
    figure.update_yaxes(title_text="レート", row=row, col=col)
    
    ###
    # ろうそく足
    figure.add_trace(go.Candlestick(x=chart.index, open=chart['Open'], high=chart['High'], low=chart['Low'], close=chart['Close'], name='OHLC', increasing_line_width=1, increasing_line_color='red', increasing_fillcolor='red', decreasing_line_width=1, decreasing_line_color='lime', decreasing_fillcolor='lime'), row=row, col=col)
    
    # SMA
    key = 'S'
    if keys.get(key) != None:
        value = keys.get(key)
        figure.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{value}'], name=f'{value} EMA', mode="lines", line=dict(color='yellow', width=1)), row=row, col=col)

    key = 'M'
    if keys.get(key) != None:
        value = keys.get(key)
        figure.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{value}'], name=f'{value} EMA', mode="lines", line=dict(color='red', width=1)), row=row, col=col)
 
        # ボリンジャーバンド
        figure.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}P2'], name=f'{value} BB + 2', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=row, col=col)
        figure.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}P1'], name=f'{value} BB + 1', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=row, col=col)
        figure.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}M1'], name=f'{value} BB - 1', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=row, col=col)
        figure.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}M2'], name=f'{value} BB - 2', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=row, col=col)
           
    key = 'L'
    if keys.get(key) != None:
        value = keys.get(key)
        figure.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{value}'], name=f'{value} EMA', mode="lines", line=dict(color='lime', width=1)), row=row, col=col)
    
    key = 'LL'
    if keys.get(key) != None:
        value = keys.get(key)
        figure.add_trace(go.Scatter(x=chart.index, y=chart[f'SMA{value}'], name=f'{value} SMA', mode="lines", line=dict(color='cyan', width=1)), row=row, col=col)
  
    # スイングハイ・スイングロー
    figure.add_trace(go.Scatter(x=chart[chart["SwingHigh"]>0].index, y=chart[chart["SwingHigh"]>0]["High"]*1.0001, name="高値", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="white"), row=row, col=col)
    figure.add_trace(go.Scatter(x=chart[chart["SwingLow"]>0].index, y=chart[chart["SwingLow"]>0]["Low"]*0.9999, name="低値", mode="markers", marker_symbol="triangle-up", marker_size=5, marker_color="white"), row=row, col=col)
    
    # 非表示にする日付(土日)をリストアップ
    d_all = pandas.date_range(start=chart.index[0],end=chart.index[-1]) # 日付リストを取得
    d_obs = [d.strftime("%Y-%m-%d") for d in chart.index] #株価データの日付リストを取得
    d_breaks = [d for d in d_all.strftime("%Y-%m-%d").tolist() if not d in d_obs] # 株価データの日付データに含まれていない日付を抽出
    figure.update_xaxes(rangebreaks=[dict(values=d_breaks)])
    
    # スケーリング機能
    if row==1:
        figure.update_layout(xaxis1_rangeslider=dict(visible=False))
    
    if row==2:
        figure.update_layout(xaxis2_rangeslider=dict(visible=False))    
    
    return figure


def add_rci(figure, chart, row=1, col=1):
    """平均足のプロット情報作成

    Args:
        filename (_type_): _description_
        currency (_type_): _description_
        chart (_type_): _description_
        keys (dict, optional): _description_. Defaults to {"S":5, "M":20, "L":60, "LL":200}.

    Returns:
        _type_: _description_
    """   
    # y軸名を定義
    figure.update_yaxes(title_text="rci", row=row, col=col)
    
    figure.add_trace(go.Scatter(x=chart.index, y=chart[f'Rci'], name=f'RCI', mode="lines", line=dict(color='yellow', width=2)), row=row, col=col)
    
    
    return figure
    
    
def add_heikinashi_candlestick(figure, chart, row=1, col=1, keys={"S":5, "M":20, "L":60, "LL":200}):
    """平均足のプロット情報作成

    Args:
        filename (_type_): _description_
        currency (_type_): _description_
        chart (_type_): _description_
        keys (dict, optional): _description_. Defaults to {"S":5, "M":20, "L":60, "LL":200}.

    Returns:
        _type_: _description_
    """   
    # y軸名を定義
    figure.update_yaxes(title_text="平均足", row=row, col=col)
    
    ###
    # ろうそく足
    figure.add_trace(go.Candlestick(x=chart.index, open=chart['HA_Open'], high=chart['HA_High'], low=chart['HA_Low'], close=chart['HA_Close'], name='Heikinashi', increasing_line_width=1, increasing_line_color='red', increasing_fillcolor='red', decreasing_line_width=1, decreasing_line_color='green', decreasing_fillcolor='green'), row=row, col=col )
    
    # key = 'S'
    # if keys.get(key) != None:
    #     value = keys.get(key)
    #     figure.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{value}'], name=f'{value} EMA', mode="lines", line=dict(color='yellow', width=1)), row=row, col=col)

    # key = 'M'
    # if keys.get(key) != None:
    #     value = keys.get(key)
    #     figure.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{value}'], name=f'{value} EMA', mode="lines", line=dict(color='red', width=1)), row=row, col=col)
 
    #     # ボリンジャーバンド
    #     # figure.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}P2'], name=f'{value} BB + 2', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=row, col=col)
    #     # figure.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}P1'], name=f'{value} BB + 1', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=row, col=col)
    #     # figure.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}M1'], name=f'{value} BB - 1', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=row, col=col)
    #     # figure.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}M2'], name=f'{value} BB - 2', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=row, col=col)
           
    # key = 'L'
    # if keys.get(key) != None:
    #     value = keys.get(key)
    #     figure.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{value}'], name=f'{value} EMA', mode="lines", line=dict(color='lime', width=1)), row=row, col=col)
    
    # key = 'LL'
    # if keys.get(key) != None:
    #     value = keys.get(key)
    #     figure.add_trace(go.Scatter(x=chart.index, y=chart[f'SMA{value}'], name=f'{value} SMA', mode="lines", line=dict(color='cyan', width=1)), row=row, col=col)
  
    # # スイングハイ・スイングロー
    # # figure.add_trace(go.Scatter(x=chart[chart["SwingHigh"]>0].index, y=chart[chart["SwingHigh"]>0]["High"]*1.0001, name="高値", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="white"), row=row, col=col)
    # # figure.add_trace(go.Scatter(x=chart[chart["SwingLow"]>0].index, y=chart[chart["SwingLow"]>0]["Low"]*0.9999, name="低値", mode="markers", marker_symbol="triangle-up", marker_size=5, marker_color="white"), row=row, col=col)
    
    # スケーリング機能
    if row==1:
        figure.update_layout(xaxis1_rangeslider=dict(visible=False))
    
    if row==2:
        figure.update_layout(xaxis2_rangeslider=dict(visible=False))    
    
    return figure


def add_heikinashi_bar(figure, chart, row=1, col=1, keys={"S":5, "M":20, "L":60, "LL":200}):
    """平均足のプロット情報作成

    Args:
        filename (_type_): _description_
        currency (_type_): _description_
        chart (_type_): _description_
        keys (dict, optional): _description_. Defaults to {"S":5, "M":20, "L":60, "LL":200}.

    Returns:
        _type_: _description_
    """
    # y軸名を定義
    figure.update_yaxes(title_text="平均足(Bar)", row=row, col=col)
    
    # 15分足の平均足の色
    figure.add_trace(go.Bar(x=chart[chart['HA_3V']>0].index, y=chart[chart['HA_3V']>0]['HA_3V'], name='平均足陽線', marker=dict(color='red')), row=row, col=col)
    figure.add_trace(go.Bar(x=chart[chart['HA_3V']<0].index, y=chart[chart['HA_3V']<0]['HA_3V']*-1, name='平均足陰線', marker=dict(color='lime')), row=row, col=col)
    # figure.add_trace(go.Bar(x=chart[chart['HA_3V']>0].index, y=chart[chart['HA_3V']>0]['HA_3V'], name='平均足陽線', marker=dict(color='red')), row=row, col=col)
    # figure.add_trace(go.Bar(x=chart[chart['HA_3V']<0].index, y=chart[chart['HA_3V']<0]['HA_3V'], name='平均足陰線', marker=dict(color='lime')), row=row, col=col)
      
    return figure

def add_deviationrate(figure, chart, row=1, col=1, keys={"S":5, "M":20, "L":60, "LL":200}):
    """乖離率の追加

    Args:
        figure (_type_): _description_
        chart (_type_): _description_
        row (int, optional): _description_. Defaults to 1.
        col (int, optional): _description_. Defaults to 1.
        keys (dict, optional): _description_. Defaults to {"S":5, "M":20, "L":60, "LL":200}.

    Returns:
        _type_: _description_
    """
    figure.update_yaxes(title_text="乖離率", row=2, col=1)
    
    key = 'S'
    if keys.get(key) != None:
        value = keys.get(key)
        figure.add_trace(go.Scatter(x=chart.index, y=chart[f'DR{value}'], name=f'{value} DR', mode="lines", line=dict(color='yellow', width=2)), row=row, col=col)

    key = 'M'
    if keys.get(key) != None:
        value = keys.get(key)   
        figure.add_trace(go.Scatter(x=chart.index, y=chart[f'DR{value}'], name=f'{value} DR', mode="lines", line=dict(color='red', width=2)), row=row, col=col)
           
    key = 'L'
    if keys.get(key) != None:
        value = keys.get(key)
        figure.add_trace(go.Scatter(x=chart.index, y=chart[f'DR{value}'], name=f'{value} DR', mode="lines", line=dict(color='lime', width=2)), row=row, col=col)
    
    key = 'LL'
    if keys.get(key) != None:
        value = keys.get(key)
        figure.add_trace(go.Scatter(x=chart.index, y=chart[f'DR{value}'], name=f'{value} DR', mode="lines", line=dict(color='cyan', width=2)), row=row, col=col)
      
    return figure

def add_sigma(figure, chart, row=1, col=1, keys={"S":5, "M":20, "L":60, "LL":200}):
    """シグマの追加

    Args:
        figure (_type_): _description_
        chart (_type_): _description_
        row (int, optional): _description_. Defaults to 1.
        col (int, optional): _description_. Defaults to 1.
        keys (dict, optional): _description_. Defaults to {"S":5, "M":20, "L":60, "LL":200}.

    Returns:
        _type_: _description_
    """
    figure.update_yaxes(title_text="シグマ", row=2, col=1)
    
    key = 'S'
    if keys.get(key) != None:
        value = keys.get(key)
        # figure.add_trace(go.Scatter(x=chart.index, y=chart[f'SIGMA{key}'], name=f'{value} SIGMA', mode="lines", line=dict(color='yellow', width=2)), row=row, col=col)

    key = 'M'
    if keys.get(key) != None:
        value = keys.get(key)   
        figure.add_trace(go.Scatter(x=chart.index, y=chart[f'SIGMA{value}'], name=f'{value} SIGMA', mode="lines", line=dict(color='red', width=2)), row=row, col=col)
           
    key = 'L'
    if keys.get(key) != None:
        value = keys.get(key)
        figure.add_trace(go.Scatter(x=chart.index, y=chart[f'SIGMA{value}'], name=f'{value} SIGMA', mode="lines", line=dict(color='lime', width=2)), row=row, col=col)
    
    key = 'LL'
    if keys.get(key) != None:
        value = keys.get(key)
        figure.add_trace(go.Scatter(x=chart.index, y=chart[f'SIGMA{value}'], name=f'{value} SIGMA', mode="lines", line=dict(color='cyan', width=2)), row=row, col=col)
      
    return figure

def add_slope(figure, chart, row=1, col=1, keys={"S":5, "M":20, "L":60, "LL":200}):
    """乖離率の追加

    Args:
        figure (_type_): _description_
        chart (_type_): _description_
        row (int, optional): _description_. Defaults to 1.
        col (int, optional): _description_. Defaults to 1.
        keys (dict, optional): _description_. Defaults to {"S":5, "M":20, "L":60, "LL":200}.

    Returns:
        _type_: _description_
    """
    figure.update_yaxes(title_text="傾き", row=2, col=1)
    
    key = 'S'
    if keys.get(key) != None:
        value = keys.get(key)
        # figure.add_trace(go.Scatter(x=chart.index, y=chart[f'Slope{key}'], name=f'{value} Slope', mode="lines", line=dict(color='yellow', width=2)), row=row, col=col)

    key = 'M'
    if keys.get(key) != None:
        value = keys.get(key)   
        figure.add_trace(go.Scatter(x=chart.index, y=chart[f'Slope{value}'], name=f'{value} Slope', mode="lines", line=dict(color='red', width=2)), row=row, col=col)
           
    key = 'L'
    if keys.get(key) != None:
        value = keys.get(key)
        figure.add_trace(go.Scatter(x=chart.index, y=chart[f'Slope{value}'], name=f'{value} Slope', mode="lines", line=dict(color='lime', width=2)), row=row, col=col)
    
    key = 'LL'
    if keys.get(key) != None:
        value = keys.get(key)
        figure.add_trace(go.Scatter(x=chart.index, y=chart[f'Slope{value}'], name=f'{value} Slope', mode="lines", line=dict(color='cyan', width=2)), row=row, col=col)
      
    return figure


def plot_basicchart(filename, currency, chart, auto_open=False, keys={"S":5, "M":20, "L":60, "LL":200}):
    """ろうそく足のプロット

    Args:
        filename (_type_): _description_
        currency (_type_): _description_
        chart (_type_): _description_
        auto_open (bool, optional): _description_. Defaults to False.
        keys (dict, optional): _description_. Defaults to {"S":5, "M":20, "L":60, "LL":200}.
    """
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[1.0], x_title="Date")

    # グラフの設定
    fig = add_graphsetting(fig)
    
    fig = add_candlestick(fig, chart, 1, 1)
    
    # プロット
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)


def plot_with_dr(filename, currency, chart, auto_open=False, keys={"S":5, "M":20, "L":60, "LL":200}):
    """乖離率とのプロット

    Args:
        filename (_type_): _description_
        currency (_type_): _description_
        chart (_type_): _description_
        auto_open (bool, optional): _description_. Defaults to False.
        keys (dict, optional): _description_. Defaults to {"S":5, "M":20, "L":60, "LL":200}.

    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.7, 0.3], x_title="Date")
    
    # グラフの設定
    fig = add_graphsetting(fig)
    
    fig = add_candlestick(fig, chart, 1, 1)
    fig = add_deviationrate(fig, chart, 2, 1)
    
    # プロット
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)

def plot_with_sigma(filename, currency, chart, auto_open=False, keys={"S":5, "M":20, "L":60, "LL":200}):
    """シグマとのプロット

    Args:
        filename (_type_): _description_
        currency (_type_): _description_
        chart (_type_): _description_
        auto_open (bool, optional): _description_. Defaults to False.
        keys (dict, optional): _description_. Defaults to {"S":5, "M":20, "L":60, "LL":200}.
    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.7, 0.3], x_title="Date")
    
    # グラフの設定
    fig = add_graphsetting(fig)
    
    fig = add_candlestick(fig, chart, 1, 1)
    fig = add_sigma(fig, chart, 2, 1)
    
    # プロット
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)

def plot_with_slope(filename, currency, chart, auto_open=False, keys={"S":5, "M":20, "L":60, "LL":200}):
    """シグマとのプロット

    Args:
        filename (_type_): _description_
        currency (_type_): _description_
        chart (_type_): _description_
        auto_open (bool, optional): _description_. Defaults to False.
        keys (dict, optional): _description_. Defaults to {"S":5, "M":20, "L":60, "LL":200}.
    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.7, 0.3], x_title="Date")
    
    # グラフの設定
    fig = add_graphsetting(fig)
    
    fig = add_candlestick(fig, chart, 1, 1)
    fig = add_slope(fig, chart, 2, 1)
    
    # プロット
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)

def plot_with_heikinashi_candlestick(filename, currency, chart, auto_open=False, keys={"S":5, "M":20, "L":60, "LL":200}):
    """平均足チャートとのプロット

    Args:
        filename (_type_): _description_
        currency (_type_): _description_
        chart (_type_): _description_
        auto_open (bool, optional): _description_. Defaults to False.
        keys (dict, optional): _description_. Defaults to {"S":5, "M":20, "L":60, "LL":200}.
    """
    # fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[1.0], x_title="Date")
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.8, 0.2], x_title="Date")
    
    # グラフの設定
    fig = add_graphsetting(fig)
    
    fig = add_candlestick(fig, chart, 1, 1)
    fig = add_heikinashi_candlestick(fig, chart, 1, 1)
    fig = add_rci(fig, chart, row=2, col=1)
    
        
    # プロット
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)

def plot_with_heikinashi_bar(filename, currency, chart, auto_open=False, keys={"S":5, "M":20, "L":60, "LL":200}):
    """平均足チャートとのプロット

    Args:
        filename (_type_): _description_
        currency (_type_): _description_
        chart (_type_): _description_
        auto_open (bool, optional): _description_. Defaults to False.
        keys (dict, optional): _description_. Defaults to {"S":5, "M":20, "L":60, "LL":200}.
    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.9, 0.1], x_title="Date")
    
    # グラフの設定
    fig = add_graphsetting(fig)
    
    fig = add_candlestick(fig, chart, 1, 1)
    fig = add_heikinashi_bar(fig, chart, 2, 1)
    
    # プロット
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)


def plot_5m_debug(filename, currency, chart, auto_open=False, keys={"S":5, "M":20, "L":60, "LL":200}):
    
    fig = go.Figure()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.7, 0.3], x_title="Date")
    # y軸名を定義
    fig.update_yaxes(title_text="レート", row=1, col=1)
    # fig.update_yaxes(title_text="レート(平均足)", row=2, col=1)
    # fig.update_yaxes(title_text="test", row=3, col=1)
    fig.update_yaxes(title_text="シグマ", row=2, col=1)
    # fig.update_yaxes(title_text="パーフェクトオーダー", row=5, col=1)
    # fig.update_yaxes(title_text="下落率(%", row=6, col=1)
    
    # タイトルの表示
    # fig.update_layout(title={'text': f'{currency}', 'y':0.99, 'x':0.5})
    
    fig.update_layout(margin=dict(t=20, b=0, l=0, r=0))
    
    # 黒設定
    fig.update_layout(plot_bgcolor="black")
    fig.update_xaxes(linecolor='black', gridcolor='gray',mirror=True)
    fig.update_yaxes(linecolor='black', gridcolor='gray',mirror=True)
    
    ###
    # ろうそく足
    fig.add_trace(go.Candlestick(x=chart.index, open=chart['Open'], high=chart['High'], low=chart['Low'], close=chart['Close'], name='OHLC', increasing_line_width=1, increasing_line_color='red', increasing_fillcolor='red', decreasing_line_width=1, decreasing_line_color='lime', decreasing_fillcolor='lime'), row=1, col=1 )
    
    # SMA
    key = 'S'
    if keys.get(key) != None:
        value = keys.get(key)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{value}'], name=f'{value} EMA', mode="lines", line=dict(color='yellow', width=1)), row=1, col=1)
               
        # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'SIGMA{key}'], name=f'{value} SIGMA', mode="lines", line=dict(color='yellow', width=2)), row=2, col=1) # Sigma 
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'DR{value}'], name=f'{value} DR', mode="lines", line=dict(color='yellow', width=2)), row=2, col=1) # 乖離率

    key = 'M'
    if keys.get(key) != None:
        value = keys.get(key)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{value}'], name=f'{value} EMA', mode="lines", line=dict(color='red', width=1)), row=1, col=1)
               
        # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'SIGMA{key}'], name=f'{value} SIGMA', mode="lines", line=dict(color='red', width=2)), row=2, col=1) # Sigma 
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'DR{value}'], name=f'{value} DR', mode="lines", line=dict(color='red', width=2)), row=2, col=1) # 乖離率
 
        # ボリンジャーバンド
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}P2'], name=f'{value} BB + 2', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}P1'], name=f'{value} BB + 1', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}M1'], name=f'{value} BB - 1', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}M2'], name=f'{value} BB - 2', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=1, col=1)
       
    
    key = 'L'
    if keys.get(key) != None:
        value = keys.get(key)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{value}'], name=f'{value} EMA', mode="lines", line=dict(color='lime', width=1)), row=1, col=1)
        # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'SIGMA{key}'], name=f'{value} SIGMA', mode="lines", line=dict(color='lime', width=2)), row=2, col=1) # Sigma 
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'DR{value}'], name=f'{value} DR', mode="lines", line=dict(color='lime', width=2)), row=2, col=1) # 乖離率
    
    key = 'LL'
    if keys.get(key) != None:
        value = keys.get(key)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'SMA{value}'], name=f'{value} SMA', mode="lines", line=dict(color='cyan', width=1)), row=1, col=1)
  

    # スイングハイ・スイングロー
    fig.add_trace(go.Scatter(x=chart[chart["SwingHigh"]>0].index, y=chart[chart["SwingHigh"]>0]["High"]*1.0001, name="高値", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="white"), row=1, col=1)
    fig.add_trace(go.Scatter(x=chart[chart["SwingLow"]>0].index, y=chart[chart["SwingLow"]>0]["Low"]*0.9999, name="低値", mode="markers", marker_symbol="triangle-up", marker_size=5, marker_color="white"), row=1, col=1)
    # 売られすぎ
    # fig.add_trace(go.Scatter(x=chart[chart["Boraku"]>=1].index, y=chart[chart["Boraku"]>=1]["Low"]*0.99, name="売られすぎ1.0", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["Boraku"]>=2].index, y=chart[chart["Boraku"]>=2]["Low"]*0.98, name="売られすぎ1.5", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["Boraku"]>=3].index, y=chart[chart["Boraku"]>=3]["Low"]*0.97, name="売られすぎ2.0", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["Boraku"]>=4].index, y=chart[chart["Boraku"]>=4]["Low"]*0.96, name="売られすぎ2.5", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["Boraku"]>=5].index, y=chart[chart["Boraku"]>=5]["Low"]*0.95, name="売られすぎ3.0", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[(chart["SIGMA5"]<-1.0)&(chart["Low"]>chart["SMA75"])&(chart["Perfect"]>=3)&(chart["Parallel"]>-1.0)].index, y=chart[(chart["SIGMA5"]<-1.0)&(chart["Low"]>chart["SMA75"])&(chart["Perfect"]>=3)&(chart["Parallel"]>-1.0)]["Close"]*0.98, name="売られすぎ", mode="markers", marker_symbol="triangle-up", marker_size=5, marker_color="black"), row=1, col=1)

    ###
    # 平均足チャート
    # fig.add_trace(go.Candlestick(x=chart.index, open=chart['HA_Open'], high=chart['HA_High'], low=chart['HA_Low'], close=chart['HA_Close'], name='OHLC', increasing_line_width=1, increasing_line_color='red', increasing_fillcolor='red', decreasing_line_width=1, decreasing_line_color='lime', decreasing_fillcolor='lime'), row=2, col=1 )
    
    # 指数移動平均
    # param = 5
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{param}'], name=f'{param} EMA', mode="lines", line=dict(color='yellow', width=1)), row=2, col=1)
    # param = 20
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{param}'], name=f'{param} EMA', mode="lines", line=dict(color='orange', width=1)), row=2, col=1)
    # param = 60
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{param}'], name=f'{param} EMA', mode="lines", line=dict(color='lime', width=1)), row=2, col=1)
    
    # ボリンジャーバンド
    # param = 5
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}P2'], name=f'{param} BB + 2', mode="lines", line=dict(dash='dot', color='blue', width=1)), row=2, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}P1'], name=f'{param} BB + 1', mode="lines", line=dict(dash='dot', color='cyan', width=1)), row=2, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}M1'], name=f'{param} BB - 1', mode="lines", line=dict(dash='dot', color='cyan', width=1)), row=2, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}M2'], name=f'{param} BB - 2', mode="lines", line=dict(dash='dot', color='blue', width=1)), row=2, col=1)
    
    # 反転
    # fig.add_trace(go.Scatter(x=chart[chart["HA_Reversal_Plus"]==True].index, y=chart[chart["HA_Reversal_Plus"]==True]["HA_High"], name="転換", mode="markers", marker_symbol="star", marker_size=5, marker_color="black"), row=2, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["HA_Reversal_Minus"]==True].index, y=chart[chart["HA_Reversal_Minus"]==True]["HA_Low"], name="転換", mode="markers", marker_symbol="star", marker_size=5, marker_color="black"), row=2, col=1)
    
    ###
    # 15分足の平均足の色
    # fig.add_trace(go.Bar(x=chart[chart['HA_3V_15M']>0].index, y=chart[chart['HA_3V_15M']>0]['HA_3V_15M'], name='15分平均足陽線', marker=dict(color='red')), row=3, col=1)
    # fig.add_trace(go.Bar(x=chart[chart['HA_3V_15M']<0].index, y=chart[chart['HA_3V_15M']<0]['HA_3V_15M'], name='15分平均足陰線', marker=dict(color='lime')), row=3, col=1)

    ###
    # 1時間足の平均足の色
    # fig.add_trace(go.Bar(x=chart[chart['HA_3V_1H']>0].index, y=chart[chart['HA_3V_1H']>0]['HA_3V_1H'], name='1時間平均足', marker=dict(color='red')), row=4, col=1)
    # fig.add_trace(go.Bar(x=chart[chart['HA_3V_1H']<0].index, y=chart[chart['HA_3V_1H']<0]['HA_3V_1H'], name='1時間平均足', marker=dict(color='lime')), row=4, col=1)
        
    ###
    # ライン
    # param = 60
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'SlopeSlope{param}'], name=f'{param} SlopeSlope', mode="lines", line=dict(color='red', width=2)), row=3, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'Slope{param}'], name=f'{param} Slope', mode="lines", line=dict(color='blue', width=2)), row=3, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart["DR20"], name="20days DR", mode="lines", line=dict(color='blue', width=2)), row=3, col=1)
    

    # # Perfect Order
    # fig.add_trace(go.Bar(x=chart.index, y=chart['PerfectOrder'], name='Perfect Order', marker=dict(color='red')), row=5, col=1)
    
    # # Drop
    # fig.add_trace(go.Scatter(x=chart.index, y=chart["Drop5"], name="5days Drop Rate", mode="lines", line=dict(color='red', width=2)), row=6, col=1)
        
    # 非表示にする日付(土日)をリストアップ
    d_all = pandas.date_range(start=chart.index[0],end=chart.index[-1]) # 日付リストを取得
    d_obs = [d.strftime("%Y-%m-%d") for d in chart.index] #株価データの日付リストを取得
    d_breaks = [d for d in d_all.strftime("%Y-%m-%d").tolist() if not d in d_obs] # 株価データの日付データに含まれていない日付を抽出
    fig.update_xaxes(rangebreaks=[dict(values=d_breaks)])
    
    # スケーリング機能
    fig.update_layout(xaxis1_rangeslider=dict(visible=False))
    # fig.update_layout(xaxis2_rangeslider=dict(visible=False))    
    
    # プロット
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)
    # plotly.io.write_image(fig, f'{folder_path}/{ticker}.png')
    
    return fig


def plot_5m(filename, currency, chart, auto_open=False, keys={"S":5, "M":20, "L":60, "LL":200}):
    
    fig = go.Figure()
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[1.0], x_title="Date")
    
    fig.update_layout(title={'text': f'{currency}', 'y':0.99, 'x':0.5})
    fig.update_layout(margin=dict(t=20, b=0, l=0, r=0))
    
    fig.update_layout(plot_bgcolor="black")
    fig.update_xaxes(linecolor='black', gridcolor='gray',mirror=True)
    fig.update_yaxes(linecolor='black', gridcolor='gray',mirror=True)


    # y軸名を定義
    fig.update_yaxes(title_text="レート", row=1, col=1)
    # fig.update_yaxes(title_text="レート(平均足)", row=2, col=1)
    # fig.update_yaxes(title_text="test", row=3, col=1)
    # fig.update_yaxes(title_text="シグマ", row=4, col=1)
    # fig.update_yaxes(title_text="パーフェクトオーダー", row=5, col=1)
    # fig.update_yaxes(title_text="下落率(%", row=6, col=1)
    
    ###
    # ろうそく足
    fig.add_trace(go.Candlestick(x=chart.index, open=chart['Open'], high=chart['High'], low=chart['Low'], close=chart['Close'], name='OHLC', increasing_line_width=1, increasing_line_color='red', increasing_fillcolor='red', decreasing_line_width=1, decreasing_line_color='lime', decreasing_fillcolor='lime'), row=1, col=1 )
    
    # SMA
    key = 'S'
    if keys.get(key) != None:
        value = keys.get(key)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{key}'], name=f'{value} EMA', mode="lines", line=dict(color='yellow', width=1)), row=1, col=1)

    key = 'M'
    if keys.get(key) != None:
        value = keys.get(key)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{key}'], name=f'{value} EMA', mode="lines", line=dict(color='red', width=1)), row=1, col=1)
    
    key = 'L'
    if keys.get(key) != None:
        value = keys.get(key)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{key}'], name=f'{value} EMA', mode="lines", line=dict(color='lime', width=1)), row=1, col=1)
    
    key = 'LL'
    if keys.get(key) != None:
        value = keys.get(key)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'SMA{key}'], name=f'{value} SMA', mode="lines", line=dict(color='cyan', width=1)), row=1, col=1)
    
    # ボリンジャーバンド
    # param = 5
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}P2'], name=f'{param} BB + 2', mode="lines", line=dict(dash='dot', color='blue', width=1)), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}P1'], name=f'{param} BB + 1', mode="lines", line=dict(dash='dot', color='cyan', width=1)), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}M1'], name=f'{param} BB - 1', mode="lines", line=dict(dash='dot', color='cyan', width=1)), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}M2'], name=f'{param} BB - 2', mode="lines", line=dict(dash='dot', color='blue', width=1)), row=1, col=1)
    
    key = 'M'
    if keys.get(key) != None:
        value = keys.get(key)
    
    param = 20
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{key}P2'], name=f'{value} BB + 2', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{key}P1'], name=f'{value} BB + 1', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{key}M1'], name=f'{value} BB - 1', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{key}M2'], name=f'{value} BB - 2', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=1, col=1)
    
    
    # スイングハイ・スイングロー
    fig.add_trace(go.Scatter(x=chart[chart["SwingHigh"]>0].index, y=chart[chart["SwingHigh"]>0]["High"], name="高値", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="white"), row=1, col=1)
    fig.add_trace(go.Scatter(x=chart[chart["SwingLow"]>0].index, y=chart[chart["SwingLow"]>0]["Low"], name="低値", mode="markers", marker_symbol="triangle-up", marker_size=5, marker_color="white"), row=1, col=1)
    # 売られすぎ
    # fig.add_trace(go.Scatter(x=chart[chart["Boraku"]>=1].index, y=chart[chart["Boraku"]>=1]["Low"]*0.99, name="売られすぎ1.0", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["Boraku"]>=2].index, y=chart[chart["Boraku"]>=2]["Low"]*0.98, name="売られすぎ1.5", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["Boraku"]>=3].index, y=chart[chart["Boraku"]>=3]["Low"]*0.97, name="売られすぎ2.0", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["Boraku"]>=4].index, y=chart[chart["Boraku"]>=4]["Low"]*0.96, name="売られすぎ2.5", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["Boraku"]>=5].index, y=chart[chart["Boraku"]>=5]["Low"]*0.95, name="売られすぎ3.0", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[(chart["SIGMA5"]<-1.0)&(chart["Low"]>chart["SMA75"])&(chart["Perfect"]>=3)&(chart["Parallel"]>-1.0)].index, y=chart[(chart["SIGMA5"]<-1.0)&(chart["Low"]>chart["SMA75"])&(chart["Perfect"]>=3)&(chart["Parallel"]>-1.0)]["Close"]*0.98, name="売られすぎ", mode="markers", marker_symbol="triangle-up", marker_size=5, marker_color="black"), row=1, col=1)

    ###
    # 平均足チャート
    # fig.add_trace(go.Candlestick(x=chart.index, open=chart['HA_Open'], high=chart['HA_High'], low=chart['HA_Low'], close=chart['HA_Close'], name='OHLC', increasing_line_width=1, increasing_line_color='red', increasing_fillcolor='red', decreasing_line_width=1, decreasing_line_color='lime', decreasing_fillcolor='lime'), row=2, col=1 )
    
    # 指数移動平均
    # param = 5
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{param}'], name=f'{param} EMA', mode="lines", line=dict(color='yellow', width=1)), row=2, col=1)
    # param = 20
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{param}'], name=f'{param} EMA', mode="lines", line=dict(color='orange', width=1)), row=2, col=1)
    # param = 60
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{param}'], name=f'{param} EMA', mode="lines", line=dict(color='lime', width=1)), row=2, col=1)
    
    # ボリンジャーバンド
    # param = 5
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}P2'], name=f'{param} BB + 2', mode="lines", line=dict(dash='dot', color='blue', width=1)), row=2, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}P1'], name=f'{param} BB + 1', mode="lines", line=dict(dash='dot', color='cyan', width=1)), row=2, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}M1'], name=f'{param} BB - 1', mode="lines", line=dict(dash='dot', color='cyan', width=1)), row=2, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}M2'], name=f'{param} BB - 2', mode="lines", line=dict(dash='dot', color='blue', width=1)), row=2, col=1)
    
    # 反転
    # fig.add_trace(go.Scatter(x=chart[chart["HA_Reversal_Plus"]==True].index, y=chart[chart["HA_Reversal_Plus"]==True]["HA_High"], name="転換", mode="markers", marker_symbol="star", marker_size=5, marker_color="black"), row=2, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["HA_Reversal_Minus"]==True].index, y=chart[chart["HA_Reversal_Minus"]==True]["HA_Low"], name="転換", mode="markers", marker_symbol="star", marker_size=5, marker_color="black"), row=2, col=1)
    
    ###
    # 15分足の平均足の色
    # fig.add_trace(go.Bar(x=chart[chart['HA_3V_15M']>0].index, y=chart[chart['HA_3V_15M']>0]['HA_3V_15M'], name='15分平均足陽線', marker=dict(color='red')), row=3, col=1)
    # fig.add_trace(go.Bar(x=chart[chart['HA_3V_15M']<0].index, y=chart[chart['HA_3V_15M']<0]['HA_3V_15M'], name='15分平均足陰線', marker=dict(color='lime')), row=3, col=1)

    ###
    # 1時間足の平均足の色
    # fig.add_trace(go.Bar(x=chart[chart['HA_3V_1H']>0].index, y=chart[chart['HA_3V_1H']>0]['HA_3V_1H'], name='1時間平均足', marker=dict(color='red')), row=4, col=1)
    # fig.add_trace(go.Bar(x=chart[chart['HA_3V_1H']<0].index, y=chart[chart['HA_3V_1H']<0]['HA_3V_1H'], name='1時間平均足', marker=dict(color='lime')), row=4, col=1)
        
    ###
    # ライン
    # param = 60
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'SlopeSlope{param}'], name=f'{param} SlopeSlope', mode="lines", line=dict(color='red', width=2)), row=3, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'Slope{param}'], name=f'{param} Slope', mode="lines", line=dict(color='blue', width=2)), row=3, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart["DR20"], name="20days DR", mode="lines", line=dict(color='blue', width=2)), row=3, col=1)
    
    # # Sigma
    # fig.add_trace(go.Scatter(x=chart.index, y=chart["SIGMA5"], name="5days SIGMA", mode="lines", line=dict(color='red', width=2)), row=4, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart["SIGMA20"], name="20days SIGMA", mode="lines", line=dict(color='blue', width=2)), row=4, col=1)
    
    # # Perfect Order
    # fig.add_trace(go.Bar(x=chart.index, y=chart['PerfectOrder'], name='Perfect Order', marker=dict(color='red')), row=5, col=1)
    
    # # Drop
    # fig.add_trace(go.Scatter(x=chart.index, y=chart["Drop5"], name="5days Drop Rate", mode="lines", line=dict(color='red', width=2)), row=6, col=1)
        
    # 非表示にする日付(土日)をリストアップ
    d_all = pandas.date_range(start=chart.index[0],end=chart.index[-1]) # 日付リストを取得
    d_obs = [d.strftime("%Y-%m-%d") for d in chart.index] #株価データの日付リストを取得
    d_breaks = [d for d in d_all.strftime("%Y-%m-%d").tolist() if not d in d_obs] # 株価データの日付データに含まれていない日付を抽出
    fig.update_xaxes(rangebreaks=[dict(values=d_breaks)])
    
    # スケーリング機能
    fig.update_layout(xaxis1_rangeslider=dict(visible=False))
    # fig.update_layout(xaxis2_rangeslider=dict(visible=False))    
    
    # プロット
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)
    # plotly.io.write_image(fig, f'{folder_path}/{ticker}.png')
    
    return fig

def plot_5ms_2window(filename, currency, chart, auto_open=False, keys={"S":5, "M":20, "L":60, "LL":200}):
    
    fig = go.Figure()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.5, 0.5], x_title="Date")
    
    fig.update_layout(title={'text': f'{currency}', 'y':0.99, 'x':0.5})
    fig.update_layout(margin=dict(t=20, b=0, l=0, r=0))
    
    fig.update_layout(plot_bgcolor="black")
    fig.update_xaxes(linecolor='black', gridcolor='gray',mirror=True)
    fig.update_yaxes(linecolor='black', gridcolor='gray',mirror=True)


    # y軸名を定義
    fig.update_yaxes(title_text="レート", row=1, col=1)
    fig.update_yaxes(title_text="レート(平均足)", row=2, col=1)
    
    ###
    # ろうそく足
    fig.add_trace(go.Candlestick(x=chart.index, open=chart['Open'], high=chart['High'], low=chart['Low'], close=chart['Close'], name='OHLC', increasing_line_width=1, increasing_line_color='red', increasing_fillcolor='red', decreasing_line_width=1, decreasing_line_color='lime', decreasing_fillcolor='lime'), row=1, col=1 )
    
    ###
    # 平均足チャート
    fig.add_trace(go.Candlestick(x=chart.index, open=chart['HA_Open'], high=chart['HA_High'], low=chart['HA_Low'], close=chart['HA_Close'], name='HHeikinashi', increasing_line_width=1, increasing_line_color='red', increasing_fillcolor='red', decreasing_line_width=1, decreasing_line_color='lime', decreasing_fillcolor='lime'), row=2, col=1 )
    
    # add EMA
    key = 'S'
    if keys.get(key) != None:
        value = keys.get(key)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{value}'], name=f'{value} EMA', mode="lines", line=dict(color='yellow', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{value}'], name=f'{value} EMA', mode="lines", line=dict(color='yellow', width=1)), row=2, col=1)

    key = 'M'
    if keys.get(key) != None:
        value = keys.get(key)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{value}'], name=f'{value} EMA', mode="lines", line=dict(color='red', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{value}'], name=f'{value} EMA', mode="lines", line=dict(color='red', width=1)), row=2, col=1)
    
    key = 'L'
    if keys.get(key) != None:
        value = keys.get(key)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{value}'], name=f'{value} EMA', mode="lines", line=dict(color='lime', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{value}'], name=f'{value} EMA', mode="lines", line=dict(color='lime', width=1)), row=2, col=1)
    
    key = 'LL'
    if keys.get(key) != None:
        value = keys.get(key)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'SMA{value}'], name=f'{value} SMA', mode="lines", line=dict(color='cyan', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'SMA{value}'], name=f'{value} SMA', mode="lines", line=dict(color='cyan', width=1)), row=2, col=1)

    # add bollinger
    key = 'M'
    if keys.get(key) != None:
        value = keys.get(key)    
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}P2'], name=f'{value} BB + 2', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}P1'], name=f'{value} BB + 1', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}M1'], name=f'{value} BB - 1', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}M2'], name=f'{value} BB - 2', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=1, col=1)
        
    # スイングハイ・スイングロー
    fig.add_trace(go.Scatter(x=chart[chart["SwingHigh"]>0].index, y=chart[chart["SwingHigh"]>0]["High"], name="高値", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="white"), row=1, col=1)
    fig.add_trace(go.Scatter(x=chart[chart["SwingLow"]>0].index, y=chart[chart["SwingLow"]>0]["Low"], name="低値", mode="markers", marker_symbol="triangle-up", marker_size=5, marker_color="white"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["HA_SwingHigh"]>0].index, y=chart[chart["HA_SwingHigh"]>0]["HA_High"], name="高値", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="white"), row=2, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["HA_SwingLow"]>0].index, y=chart[chart["HA_SwingLow"]>0]["HA_Low"], name="低値", mode="markers", marker_symbol="triangle-up", marker_size=5, marker_color="white"), row=2, col=1)
    
        
    # 非表示にする日付(土日)をリストアップ
    d_all = pandas.date_range(start=chart.index[0],end=chart.index[-1]) # 日付リストを取得
    d_obs = [d.strftime("%Y-%m-%d") for d in chart.index] #株価データの日付リストを取得
    d_breaks = [d for d in d_all.strftime("%Y-%m-%d").tolist() if not d in d_obs] # 株価データの日付データに含まれていない日付を抽出
    fig.update_xaxes(rangebreaks=[dict(values=d_breaks)])
    
    # スケーリング機能
    fig.update_layout(xaxis1_rangeslider=dict(visible=False))
    fig.update_layout(xaxis2_rangeslider=dict(visible=False))    
    
    # プロット
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)
    # plotly.io.write_image(fig, f'{folder_path}/{ticker}.png')
    
    return fig


def plot_simple(filename, currency, chart, auto_open=False):
    
    fig = go.Figure()
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[1.0], x_title="Date")
    
    fig.update_layout(title={'text': f'{currency}', 'y':0.99, 'x':0.5})
    fig.update_layout(margin=dict(t=20, b=0, l=0, r=0))
    
    fig.update_layout(plot_bgcolor="black")
    fig.update_xaxes(linecolor='black', gridcolor='gray',mirror=True)
    fig.update_yaxes(linecolor='black', gridcolor='gray',mirror=True)


    # y軸名を定義
    fig.update_yaxes(title_text="レート", row=1, col=1)
    # fig.update_yaxes(title_text="レート(平均足)", row=2, col=1)
    # fig.update_yaxes(title_text="test", row=3, col=1)
    # fig.update_yaxes(title_text="シグマ", row=4, col=1)
    # fig.update_yaxes(title_text="パーフェクトオーダー", row=5, col=1)
    # fig.update_yaxes(title_text="下落率(%", row=6, col=1)
    
    ###
    # ろうそく足
    fig.add_trace(go.Candlestick(x=chart.index, open=chart['Open'], high=chart['High'], low=chart['Low'], close=chart['Close'], name='OHLC', increasing_line_width=1, increasing_line_color='red', increasing_fillcolor='red', decreasing_line_width=1, decreasing_line_color='lime', decreasing_fillcolor='lime'), row=1, col=1 )
    
    # SMA
    param = 5
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'SMA{param}'], name=f'{param} SMA', mode="lines", line=dict(color='yellow', width=1)), row=1, col=1)
    param = 20
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'SMA{param}'], name=f'{param} SMA', mode="lines", line=dict(color='red', width=1)), row=1, col=1)
    param = 60
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'SMA{param}'], name=f'{param} SMA', mode="lines", line=dict(color='lime', width=1)), row=1, col=1)
    param = 240
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'SMA{param}'], name=f'{param} SMA', mode="lines", line=dict(color='cyan', width=1)), row=1, col=1)
    
    # ボリンジャーバンド
    # param = 5
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}P2'], name=f'{param} BB + 2', mode="lines", line=dict(dash='dot', color='blue', width=1)), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}P1'], name=f'{param} BB + 1', mode="lines", line=dict(dash='dot', color='cyan', width=1)), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}M1'], name=f'{param} BB - 1', mode="lines", line=dict(dash='dot', color='cyan', width=1)), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}M2'], name=f'{param} BB - 2', mode="lines", line=dict(dash='dot', color='blue', width=1)), row=1, col=1)
    param = 20
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}P2'], name=f'{param} BB + 2', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}P1'], name=f'{param} BB + 1', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}M1'], name=f'{param} BB - 1', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}M2'], name=f'{param} BB - 2', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=1, col=1)
    
    
    # スイングハイ・スイングロー
    fig.add_trace(go.Scatter(x=chart[chart["SwingHigh"]>0].index, y=chart[chart["SwingHigh"]>0]["High"], name="高値", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="white"), row=1, col=1)
    fig.add_trace(go.Scatter(x=chart[chart["SwingLow"]>0].index, y=chart[chart["SwingLow"]>0]["Low"], name="低値", mode="markers", marker_symbol="triangle-up", marker_size=5, marker_color="white"), row=1, col=1)
    # 売られすぎ
    # fig.add_trace(go.Scatter(x=chart[chart["Boraku"]>=1].index, y=chart[chart["Boraku"]>=1]["Low"]*0.99, name="売られすぎ1.0", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["Boraku"]>=2].index, y=chart[chart["Boraku"]>=2]["Low"]*0.98, name="売られすぎ1.5", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["Boraku"]>=3].index, y=chart[chart["Boraku"]>=3]["Low"]*0.97, name="売られすぎ2.0", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["Boraku"]>=4].index, y=chart[chart["Boraku"]>=4]["Low"]*0.96, name="売られすぎ2.5", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["Boraku"]>=5].index, y=chart[chart["Boraku"]>=5]["Low"]*0.95, name="売られすぎ3.0", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[(chart["SIGMA5"]<-1.0)&(chart["Low"]>chart["SMA75"])&(chart["Perfect"]>=3)&(chart["Parallel"]>-1.0)].index, y=chart[(chart["SIGMA5"]<-1.0)&(chart["Low"]>chart["SMA75"])&(chart["Perfect"]>=3)&(chart["Parallel"]>-1.0)]["Close"]*0.98, name="売られすぎ", mode="markers", marker_symbol="triangle-up", marker_size=5, marker_color="black"), row=1, col=1)

    ###
    # 平均足チャート
    # fig.add_trace(go.Candlestick(x=chart.index, open=chart['HA_Open'], high=chart['HA_High'], low=chart['HA_Low'], close=chart['HA_Close'], name='OHLC', increasing_line_width=1, increasing_line_color='red', increasing_fillcolor='red', decreasing_line_width=1, decreasing_line_color='lime', decreasing_fillcolor='lime'), row=2, col=1 )
    
    # 指数移動平均
    # param = 5
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{param}'], name=f'{param} EMA', mode="lines", line=dict(color='yellow', width=1)), row=2, col=1)
    # param = 20
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{param}'], name=f'{param} EMA', mode="lines", line=dict(color='orange', width=1)), row=2, col=1)
    # param = 60
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{param}'], name=f'{param} EMA', mode="lines", line=dict(color='lime', width=1)), row=2, col=1)
    
    # ボリンジャーバンド
    # param = 5
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}P2'], name=f'{param} BB + 2', mode="lines", line=dict(dash='dot', color='blue', width=1)), row=2, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}P1'], name=f'{param} BB + 1', mode="lines", line=dict(dash='dot', color='cyan', width=1)), row=2, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}M1'], name=f'{param} BB - 1', mode="lines", line=dict(dash='dot', color='cyan', width=1)), row=2, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}M2'], name=f'{param} BB - 2', mode="lines", line=dict(dash='dot', color='blue', width=1)), row=2, col=1)
    
    # 反転
    # fig.add_trace(go.Scatter(x=chart[chart["HA_Reversal_Plus"]==True].index, y=chart[chart["HA_Reversal_Plus"]==True]["HA_High"], name="転換", mode="markers", marker_symbol="star", marker_size=5, marker_color="black"), row=2, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["HA_Reversal_Minus"]==True].index, y=chart[chart["HA_Reversal_Minus"]==True]["HA_Low"], name="転換", mode="markers", marker_symbol="star", marker_size=5, marker_color="black"), row=2, col=1)
    
    ###
    # 15分足の平均足の色
    # fig.add_trace(go.Bar(x=chart[chart['HA_3V_15M']>0].index, y=chart[chart['HA_3V_15M']>0]['HA_3V_15M'], name='15分平均足陽線', marker=dict(color='red')), row=3, col=1)
    # fig.add_trace(go.Bar(x=chart[chart['HA_3V_15M']<0].index, y=chart[chart['HA_3V_15M']<0]['HA_3V_15M'], name='15分平均足陰線', marker=dict(color='lime')), row=3, col=1)

    ###
    # 1時間足の平均足の色
    # fig.add_trace(go.Bar(x=chart[chart['HA_3V_1H']>0].index, y=chart[chart['HA_3V_1H']>0]['HA_3V_1H'], name='1時間平均足', marker=dict(color='red')), row=4, col=1)
    # fig.add_trace(go.Bar(x=chart[chart['HA_3V_1H']<0].index, y=chart[chart['HA_3V_1H']<0]['HA_3V_1H'], name='1時間平均足', marker=dict(color='lime')), row=4, col=1)
        
    ###
    # ライン
    # param = 60
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'SlopeSlope{param}'], name=f'{param} SlopeSlope', mode="lines", line=dict(color='red', width=2)), row=3, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'Slope{param}'], name=f'{param} Slope', mode="lines", line=dict(color='blue', width=2)), row=3, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart["DR20"], name="20days DR", mode="lines", line=dict(color='blue', width=2)), row=3, col=1)
    
    # # Sigma
    # fig.add_trace(go.Scatter(x=chart.index, y=chart["SIGMA5"], name="5days SIGMA", mode="lines", line=dict(color='red', width=2)), row=4, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart["SIGMA20"], name="20days SIGMA", mode="lines", line=dict(color='blue', width=2)), row=4, col=1)
    
    # # Perfect Order
    # fig.add_trace(go.Bar(x=chart.index, y=chart['PerfectOrder'], name='Perfect Order', marker=dict(color='red')), row=5, col=1)
    
    # # Drop
    # fig.add_trace(go.Scatter(x=chart.index, y=chart["Drop5"], name="5days Drop Rate", mode="lines", line=dict(color='red', width=2)), row=6, col=1)
        
    # 非表示にする日付(土日)をリストアップ
    d_all = pandas.date_range(start=chart.index[0],end=chart.index[-1]) # 日付リストを取得
    d_obs = [d.strftime("%Y-%m-%d") for d in chart.index] #株価データの日付リストを取得
    d_breaks = [d for d in d_all.strftime("%Y-%m-%d").tolist() if not d in d_obs] # 株価データの日付データに含まれていない日付を抽出
    fig.update_xaxes(rangebreaks=[dict(values=d_breaks)])
    
    # スケーリング機能
    fig.update_layout(xaxis1_rangeslider=dict(visible=False))
    # fig.update_layout(xaxis2_rangeslider=dict(visible=False))    
    
    # プロット
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)
    # plotly.io.write_image(fig, f'{folder_path}/{ticker}.png')
    
    return fig


def plotly_show(filename, currency, chart, auto_open=False):
    
    fig = go.Figure()
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.5, 0.5, 0.1, 0.1], x_title="Date")
    
    fig.update_layout(title={'text': f'{currency}', 'y':0.99, 'x':0.5})
    # fig.update_layout(title={'text': f'{ticker}', 'y':0.9, 'x':0.5})
    fig.update_layout(margin=dict(t=20, b=0, l=0, r=0))
    
    fig.update_layout(plot_bgcolor="black")
    fig.update_xaxes(linecolor='black', gridcolor='gray',mirror=True)
    fig.update_yaxes(linecolor='black', gridcolor='gray',mirror=True)


    # y軸名を定義
    fig.update_yaxes(title_text="レート", row=1, col=1)
    fig.update_yaxes(title_text="レート(平均足)", row=2, col=1)
    fig.update_yaxes(title_text="test", row=3, col=1)
    # fig.update_yaxes(title_text="シグマ", row=4, col=1)
    # fig.update_yaxes(title_text="パーフェクトオーダー", row=5, col=1)
    # fig.update_yaxes(title_text="下落率(%", row=6, col=1)
    
    ###
    # ろうそく足
    fig.add_trace(go.Candlestick(x=chart.index, open=chart['Open'], high=chart['High'], low=chart['Low'], close=chart['Close'], name='OHLC', increasing_line_width=1, increasing_line_color='red', increasing_fillcolor='red', decreasing_line_width=1, decreasing_line_color='lime', decreasing_fillcolor='lime'), row=1, col=1 )
    
    # SMA
    param = 5
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'SMA{param}'], name=f'{param} SMA', mode="lines", line=dict(color='yellow', width=1)), row=1, col=1)
    param = 20
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'SMA{param}'], name=f'{param} SMA', mode="lines", line=dict(color='orange', width=1)), row=1, col=1)
    param = 60
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'SMA{param}'], name=f'{param} SMA', mode="lines", line=dict(color='lime', width=1)), row=1, col=1)
    
    # ボリンジャーバンド
    param = 5
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}P2'], name=f'{param} BB + 2', mode="lines", line=dict(dash='dot', color='blue', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}P1'], name=f'{param} BB + 1', mode="lines", line=dict(dash='dot', color='cyan', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}M1'], name=f'{param} BB - 1', mode="lines", line=dict(dash='dot', color='cyan', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}M2'], name=f'{param} BB - 2', mode="lines", line=dict(dash='dot', color='blue', width=1)), row=1, col=1)
    # param = 20
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}P2'], name=f'{param} BB + 2', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}P1'], name=f'{param} BB + 1', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}M1'], name=f'{param} BB - 1', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}M2'], name=f'{param} BB - 2', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=1, col=1)
    
    
    # スイングハイ・スイングロー
    fig.add_trace(go.Scatter(x=chart[chart["SwingHigh"]>0].index, y=chart[chart["SwingHigh"]>0]["High"], name="高値", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    fig.add_trace(go.Scatter(x=chart[chart["SwingLow"]>0].index, y=chart[chart["SwingLow"]>0]["Low"], name="低値", mode="markers", marker_symbol="triangle-up", marker_size=5, marker_color="black"), row=1, col=1)
    # 売られすぎ
    # fig.add_trace(go.Scatter(x=chart[chart["Boraku"]>=1].index, y=chart[chart["Boraku"]>=1]["Low"]*0.99, name="売られすぎ1.0", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["Boraku"]>=2].index, y=chart[chart["Boraku"]>=2]["Low"]*0.98, name="売られすぎ1.5", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["Boraku"]>=3].index, y=chart[chart["Boraku"]>=3]["Low"]*0.97, name="売られすぎ2.0", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["Boraku"]>=4].index, y=chart[chart["Boraku"]>=4]["Low"]*0.96, name="売られすぎ2.5", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["Boraku"]>=5].index, y=chart[chart["Boraku"]>=5]["Low"]*0.95, name="売られすぎ3.0", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[(chart["SIGMA5"]<-1.0)&(chart["Low"]>chart["SMA75"])&(chart["Perfect"]>=3)&(chart["Parallel"]>-1.0)].index, y=chart[(chart["SIGMA5"]<-1.0)&(chart["Low"]>chart["SMA75"])&(chart["Perfect"]>=3)&(chart["Parallel"]>-1.0)]["Close"]*0.98, name="売られすぎ", mode="markers", marker_symbol="triangle-up", marker_size=5, marker_color="black"), row=1, col=1)

    ###
    # 平均足チャート
    fig.add_trace(go.Candlestick(x=chart.index, open=chart['HA_Open'], high=chart['HA_High'], low=chart['HA_Low'], close=chart['HA_Close'], name='OHLC', increasing_line_width=1, increasing_line_color='red', increasing_fillcolor='red', decreasing_line_width=1, decreasing_line_color='lime', decreasing_fillcolor='lime'), row=2, col=1 )
    
    # 指数移動平均
    param = 5
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{param}'], name=f'{param} EMA', mode="lines", line=dict(color='yellow', width=1)), row=2, col=1)
    param = 20
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{param}'], name=f'{param} EMA', mode="lines", line=dict(color='orange', width=1)), row=2, col=1)
    param = 60
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{param}'], name=f'{param} EMA', mode="lines", line=dict(color='lime', width=1)), row=2, col=1)
    
    # ボリンジャーバンド
    param = 5
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}P2'], name=f'{param} BB + 2', mode="lines", line=dict(dash='dot', color='blue', width=1)), row=2, col=1)
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}P1'], name=f'{param} BB + 1', mode="lines", line=dict(dash='dot', color='cyan', width=1)), row=2, col=1)
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}M1'], name=f'{param} BB - 1', mode="lines", line=dict(dash='dot', color='cyan', width=1)), row=2, col=1)
    fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}M2'], name=f'{param} BB - 2', mode="lines", line=dict(dash='dot', color='blue', width=1)), row=2, col=1)
    
    # 反転
    fig.add_trace(go.Scatter(x=chart[chart["HA_Reversal_Plus"]==True].index, y=chart[chart["HA_Reversal_Plus"]==True]["HA_High"], name="転換", mode="markers", marker_symbol="star", marker_size=5, marker_color="black"), row=2, col=1)
    fig.add_trace(go.Scatter(x=chart[chart["HA_Reversal_Minus"]==True].index, y=chart[chart["HA_Reversal_Minus"]==True]["HA_Low"], name="転換", mode="markers", marker_symbol="star", marker_size=5, marker_color="black"), row=2, col=1)
    
    ###
    # 15分足の平均足の色
    fig.add_trace(go.Bar(x=chart[chart['HA_3V_15M']>0].index, y=chart[chart['HA_3V_15M']>0]['HA_3V_15M'], name='15分平均足陽線', marker=dict(color='red')), row=3, col=1)
    fig.add_trace(go.Bar(x=chart[chart['HA_3V_15M']<0].index, y=chart[chart['HA_3V_15M']<0]['HA_3V_15M'], name='15分平均足陰線', marker=dict(color='lime')), row=3, col=1)

    ###
    # 1時間足の平均足の色
    fig.add_trace(go.Bar(x=chart[chart['HA_3V_1H']>0].index, y=chart[chart['HA_3V_1H']>0]['HA_3V_1H'], name='1時間平均足', marker=dict(color='red')), row=4, col=1)
    fig.add_trace(go.Bar(x=chart[chart['HA_3V_1H']<0].index, y=chart[chart['HA_3V_1H']<0]['HA_3V_1H'], name='1時間平均足', marker=dict(color='lime')), row=4, col=1)
        
    ###
    # ライン
    # param = 60
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'SlopeSlope{param}'], name=f'{param} SlopeSlope', mode="lines", line=dict(color='red', width=2)), row=3, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'Slope{param}'], name=f'{param} Slope', mode="lines", line=dict(color='blue', width=2)), row=3, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart["DR20"], name="20days DR", mode="lines", line=dict(color='blue', width=2)), row=3, col=1)
    
    # # Sigma
    # fig.add_trace(go.Scatter(x=chart.index, y=chart["SIGMA5"], name="5days SIGMA", mode="lines", line=dict(color='red', width=2)), row=4, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart["SIGMA20"], name="20days SIGMA", mode="lines", line=dict(color='blue', width=2)), row=4, col=1)
    
    # # Perfect Order
    # fig.add_trace(go.Bar(x=chart.index, y=chart['PerfectOrder'], name='Perfect Order', marker=dict(color='red')), row=5, col=1)
    
    # # Drop
    # fig.add_trace(go.Scatter(x=chart.index, y=chart["Drop5"], name="5days Drop Rate", mode="lines", line=dict(color='red', width=2)), row=6, col=1)
        
    # 非表示にする日付(土日)をリストアップ
    d_all = pandas.date_range(start=chart.index[0],end=chart.index[-1]) # 日付リストを取得
    d_obs = [d.strftime("%Y-%m-%d") for d in chart.index] #株価データの日付リストを取得
    d_breaks = [d for d in d_all.strftime("%Y-%m-%d").tolist() if not d in d_obs] # 株価データの日付データに含まれていない日付を抽出
    fig.update_xaxes(rangebreaks=[dict(values=d_breaks)])
    
    # スケーリング機能
    # fig.update(layout_xaxis_rangeslider=dict(visible=False))
    fig.update_layout(xaxis1_rangeslider=dict(visible=False))
    fig.update_layout(xaxis2_rangeslider=dict(visible=False))
    
    # プロット
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)
    # plotly.io.write_image(fig, f'{folder_path}/{ticker}.png')
    
    return fig



def plot_heikinashi(filename, currency, chart, auto_open=False):
    
    # fig = go.Figure()
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[1], x_title="Date")
    
    fig.update_layout(title={'text': f'{currency}', 'y':0.99, 'x':0.5})
    # fig.update_layout(title={'text': f'{ticker}', 'y':0.9, 'x':0.5})
    fig.update_layout(margin=dict(t=20, b=0, l=0, r=0))

    # y軸名を定義
    fig.update_yaxes(title_text="レート(平均足)", row=1, col=1)
    
    ###
    # 平均足チャート
    fig.add_trace(go.Candlestick(x=chart.index, open=chart['HA_Open'], high=chart['HA_High'], low=chart['HA_Low'], close=chart['HA_Close'], name='OHLC', increasing_line_width=1, increasing_line_color='red', increasing_fillcolor='red', decreasing_line_width=1, decreasing_line_color='lime', decreasing_fillcolor='lime'), row=1, col=1 )
    
    # 指数移動平均
    # param = 5
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{param}'], name=f'{param} EMA', mode="lines", line=dict(color='yellow', width=1)), row=1, col=1)
    # param = 20
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{param}'], name=f'{param} EMA', mode="lines", line=dict(color='orange', width=1)), row=1, col=1)
    # param = 60
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'EMA{param}'], name=f'{param} EMA', mode="lines", line=dict(color='lime', width=1)), row=1, col=1)
    
    # # ボリンジャーバンド
    # param = 5
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}P2'], name=f'{param} BB + 2', mode="lines", line=dict(dash='dot', color='blue', width=1)), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}P1'], name=f'{param} BB + 1', mode="lines", line=dict(dash='dot', color='cyan', width=1)), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}M1'], name=f'{param} BB - 1', mode="lines", line=dict(dash='dot', color='cyan', width=1)), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{param}M2'], name=f'{param} BB - 2', mode="lines", line=dict(dash='dot', color='blue', width=1)), row=1, col=1)
    
    # # 反転
    # fig.add_trace(go.Scatter(x=chart[chart["HA_Reversal_Plus"]==True].index, y=chart[chart["HA_Reversal_Plus"]==True]["HA_High"], name="転換", mode="markers", marker_symbol="star", marker_size=5, marker_color="black"), row=1, col=1)
    # fig.add_trace(go.Scatter(x=chart[chart["HA_Reversal_Minus"]==True].index, y=chart[chart["HA_Reversal_Minus"]==True]["HA_Low"], name="転換", mode="markers", marker_symbol="star", marker_size=5, marker_color="black"), row=1, col=1)
        
        
    # 非表示にする日付(土日)をリストアップ
    d_all = pandas.date_range(start=chart.index[0],end=chart.index[-1]) # 日付リストを取得
    d_obs = [d.strftime("%Y-%m-%d") for d in chart.index] #株価データの日付リストを取得
    d_breaks = [d for d in d_all.strftime("%Y-%m-%d").tolist() if not d in d_obs] # 株価データの日付データに含まれていない日付を抽出
    fig.update_xaxes(rangebreaks=[dict(values=d_breaks)])
    
    # スケーリング機能
    # fig.update(layout_xaxis_rangeslider=dict(visible=False))
    fig.update_layout(xaxis1_rangeslider=dict(visible=False))
    # fig.update_layout(xaxis2_rangeslider=dict(visible=False))
    
    # プロット
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)
    # plotly.io.write_image(fig, f'{folder_path}/{ticker}.png')
    
    return fig
