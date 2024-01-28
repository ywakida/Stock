import os
import pandas
import plotly.graph_objects as go
import plotly.offline
import plotly.io
from plotly.subplots import make_subplots
import chart_days

def add_graphsetting(figure):
    """グラフの全体設定
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

def remove_gap_datetime(figure, chart):
    """空白(GAP)の時刻を除去する
    """
    # print((chart.index[1]-chart.index[0]).seconds)
    minutes = (chart.index[1]-chart.index[0]).seconds / 60
    days = (chart.index[1]-chart.index[0]).days
    
    if days>=1:
        d_all = pandas.date_range(start=chart.index[0],end=chart.index[-1], freq='B') # 月から金のデータ期間の完全な時系列を取得する
    else:
        d_all = pandas.date_range(start=chart.index[0],end=chart.index[-1], freq=f'{minutes}T') # データ期間の完全な時系列を取得する
        # for d in d_all:
        #     print(d)
        
    d_obs = [d.strftime("%Y-%m-%d %H:%M:%S") for d in chart.index] #データの時系列を取得する
    # for d in d_obs:
    #     print(d)
    
    d_breaks = [d for d in d_all.strftime("%Y-%m-%d %H:%M:%S").tolist() if not d in d_obs] # データに含まれていない時刻を抽出
    # for d in d_breaks:
    #     print(d)
    if min==0:
        figure.update_xaxes(rangebreaks=[dict(values=d_breaks)]) # dvalueはmsec    
    else:
        figure.update_xaxes(rangebreaks=[dict(values=d_breaks, dvalue=1000*60*minutes)]) # dvalueはmsec
    
    return figure


def remove_weekend(figure, chart):
    """非表示にする日付(土日)をリストアップ
    """
    d_all = pandas.date_range(start=chart.index[0],end=chart.index[-1]) # 日付リストを取得
    d_obs = [d.strftime("%Y-%m-%d") for d in chart.index] #株価データの日付リストを取得
    d_breaks = [d for d in d_all.strftime("%Y-%m-%d").tolist() if not d in d_obs] # 株価データの日付データに含まれていない日付を抽出
    figure.update_xaxes(rangebreaks=[dict(values=d_breaks)])

    return figure
    
    
def add_candlestick(figure, chart, row=1, col=1, keys={"S":5, "M":25, "L":75, "LL":200}, show_swing=True, show_bollinger=True, show_order=False):
    """ろうそく足のプロット情報作成
    """
    # y軸名を定義
    figure.update_yaxes(title_text="レート", row=row, col=col)
    
    # ろうそく足
    figure.add_trace(go.Candlestick(x=chart.index, open=chart['Open'], high=chart['High'], low=chart['Low'], close=chart['Close'], name='OHLC', increasing_line_width=1, increasing_line_color='red', increasing_fillcolor='red', decreasing_line_width=1, decreasing_line_color='lime', decreasing_fillcolor='lime'), row=row, col=col)
    
    matypes={"S":"SMA", "M":"SMA", "L":"SMA", "LL":"SMA"}
    colors={"S":"yellow", "M":"red", "L":"lime", "LL":"cyan"}
    for key, value in keys.items():
        thismatype = matypes.get(key)
        thiscolor = colors.get(key)
        
        if f'{thismatype}{value}' in chart.columns:
            figure.add_trace(go.Scatter(x=chart.index, y=chart[f'{thismatype}{value}'], name=f'{value} {thismatype}', mode="lines", line=dict(color=thiscolor, width=2)), row=row, col=col)

    # ボリンジャーバンド
    if show_bollinger:
        key = 'M'
        if keys.get(key) != None:
            value = keys.get(key)
                   
            if f'BB{value}P2' in chart.columns and f'BB{value}M2' in chart.columns:
                # figure.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}P2'], name=f'{value} BB + 2', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=row, col=col)
                # figure.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}M2'], name=f'{value} BB - 2', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=row, col=col)
                figure.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}P2'], name=f'', mode="lines", line=dict(color='lavender', width=0)), row=row, col=col)
                figure.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}M2'], name=f'{value} BB ± 2', mode="lines", line=dict(color='lavender', width=0), fill="tonexty", fillcolor="rgba(170, 170, 170,.3)"), row=row, col=col)
            if f'BB{value}P1' in chart.columns and f'BB{value}M1' in chart.columns:
                # figure.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}P1'], name=f'{value} BB + 1', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=row, col=col)
                # figure.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}M1'], name=f'{value} BB - 1', mode="lines", line=dict(dash='dot', color='pink', width=1)), row=row, col=col)
                figure.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}P1'], name=f'', mode="lines", line=dict(color='lavender', width=0)), row=row, col=col)
                figure.add_trace(go.Scatter(x=chart.index, y=chart[f'BB{value}M1'], name=f'{value} BB ± 1', mode="lines", line=dict(color='lavender', width=0), fill="tonexty", fillcolor="rgba(170, 170, 170,.1)"), row=row, col=col)
                
            
    # スイングハイ・スイングロー
    if show_swing:
        if 'SwingHigh' in chart.columns:
            figure.add_trace(go.Scatter(x=chart[chart["SwingHigh"].notna()].index, y=chart[chart["SwingHigh"].notna()]["High"]*1.0002, name="高値", mode="markers", marker_symbol="triangle-down", marker_size=5, marker_color="white"), row=row, col=col)
        if 'SwingLow' in chart.columns:
            figure.add_trace(go.Scatter(x=chart[chart["SwingLow"].notna()].index, y=chart[chart["SwingLow"].notna()]["Low"]*0.9998, name="低値", mode="markers", marker_symbol="triangle-up", marker_size=5, marker_color="white"), row=row, col=col)

    if show_order:
        if 'Buy' in chart.columns:
            figure.add_trace(go.Scatter(x=chart[chart["Buy"]].index, y=chart[chart["Buy"]]["High"]*1.0002, name="買い", mode="markers", marker_symbol="arrow-right", marker_size=7, marker_color="white"), row=row, col=col)
        if 'Sell' in chart.columns:
            figure.add_trace(go.Scatter(x=chart[chart["Sell"]].index, y=chart[chart["Sell"]]["Low"]*0.9998, name="売り", mode="markers", marker_symbol="arrow-left", marker_size=7, marker_color="white"), row=row, col=col)
            
    # スケーリング機能
    if row==1:
        figure.update_layout(xaxis1_rangeslider=dict(visible=False))
    if row==2:
        figure.update_layout(xaxis2_rangeslider=dict(visible=False))    
    if row==3:
        figure.update_layout(xaxis3_rangeslider=dict(visible=False))
        
    return figure


def add_volume(figure, chart, row=1, col=1):
    """平均足のプロット情報作成
    """
    # y軸名を定義
    figure.update_yaxes(title_text="出来高", row=row, col=col)
    
    if 'Volume' in chart.columns:
        figure.add_trace(go.Bar(x=chart.index, y=chart['Volume'], name='出来高', showlegend=False), row=row, col=col)
      
    return figure


def add_rci(figure, chart, row=1, col=1):
    """平均足のプロット情報作成
    """   
    # y軸名を定義
    figure.update_yaxes(title_text="rci", row=row, col=col)
    
    if 'Rci' in chart.columns:
        figure.add_trace(go.Scatter(x=chart.index, y=chart[f'Rci'], name=f'RCI', mode="lines", line=dict(color='yellow', width=2)), row=row, col=col)
    
    return figure
      
def add_heikinashi_candlestick(figure, chart, row=1, col=1):
    """平均足のプロット情報作成
    """   
    # y軸名を定義
    figure.update_yaxes(title_text="平均足", row=row, col=col)
    
    ###
    # ろうそく足
    figure.add_trace(go.Candlestick(x=chart.index, open=chart['HA_Open'], high=chart['HA_High'], low=chart['HA_Low'], close=chart['HA_Close'], name='Heikinashi', increasing_line_width=1, increasing_line_color='red', increasing_fillcolor='red', decreasing_line_width=1, decreasing_line_color='green', decreasing_fillcolor='green'), row=row, col=col )
    
    # スケーリング機能
    if row==1:
        figure.update_layout(xaxis1_rangeslider=dict(visible=False))
    if row==2:
        figure.update_layout(xaxis2_rangeslider=dict(visible=False))    
    
    return figure


def add_heikinashi_bar(figure, chart, row=1, col=1, keys={"S":5, "M":20, "L":60, "LL":200}):
    """平均足のプロット情報作成
    """
    # y軸名を定義
    figure.update_yaxes(title_text="平均足(Bar)", row=row, col=col)
    
    # バー
    figure.add_trace(go.Bar(x=chart[chart['HA_3V']>0].index, y=chart[chart['HA_3V']>0]['HA_3V'], name='平均足陽線', marker=dict(color='red')), row=row, col=col)
    figure.add_trace(go.Bar(x=chart[chart['HA_3V']<0].index, y=chart[chart['HA_3V']<0]['HA_3V']*-1, name='平均足陰線', marker=dict(color='lime')), row=row, col=col)
      
    return figure

def add_heikinashi2(figure, chart, row=1, col=1, keys={"S":5, "M":25, "L":75, "LL":200}):
    """平均足のプロット情報作成
    """   
    # y軸名を定義
    figure.update_yaxes(title_text="平均足", row=row, col=col)
    
    ###
    # ろうそく足
    figure.add_trace(go.Candlestick(x=chart.index, open=chart['Open'], high=chart['High'], low=chart['Low'], close=chart['Close'], name='Heikinashi', increasing_line_width=1, increasing_line_color='red', increasing_fillcolor='red', decreasing_line_width=1, decreasing_line_color='green', decreasing_fillcolor='green'), row=row, col=col )
    
    # スケーリング機能
    if row==1:
        figure.update_layout(xaxis1_rangeslider=dict(visible=False))    
    if row==2:
        figure.update_layout(xaxis2_rangeslider=dict(visible=False))    
    
    return figure


def add_deviationrate(figure, chart, row=1, col=1, keys={"S":5, "M":20, "L":60, "LL":200}):
    """ 乖離率の追加
    """
    figure.update_yaxes(title_text="乖離率", row=row, col=col)
    
    colors={"S":"yellow", "M":"red", "L":"lime", "LL":"cyan"}
    for key, value in keys.items():
        thiscolor = colors.get(key)
        if f'EMADR{value}' in chart.columns:
            figure.add_trace(go.Scatter(x=chart.index, y=chart[f'EMADR{value}'], name=f'{value} EMADR', mode="lines", line=dict(color=thiscolor, width=2)), row=row, col=col)
        elif f'SMADR{value}' in chart.columns:
            figure.add_trace(go.Scatter(x=chart.index, y=chart[f'SMADR{value}'], name=f'{value} SMADR', mode="lines", line=dict(color=thiscolor, width=2)), row=row, col=col)
        else:
            pass
             
    return figure

def add_sigma(figure, chart, row=1, col=1, keys={"S":5, "M":20, "L":60, "LL":200}):
    """シグマの追加
    """
    figure.update_yaxes(title_text="シグマ", row=row, col=col)
    
    colors={"S":"yellow", "M":"red", "L":"lime", "LL":"cyan"}
    for key, value in keys.items():
        thiscolor = colors.get(key)
        
        if f'SIGMA{value}' in chart.columns:
            figure.add_trace(go.Scatter(x=chart.index, y=chart[f'SIGMA{value}'], name=f'{value} SIGMA', mode="lines", line=dict(color=thiscolor, width=2)), row=row, col=col)
      
    return figure

def add_slope(figure, chart, row=1, col=1, keys={"S":5, "M":20, "L":60, "LL":200}):
    """乖離率の追加
    """
    figure.update_yaxes(title_text="傾き", row=row, col=col)
    
    colors={"S":"yellow", "M":"red", "L":"lime", "LL":"cyan"}
    for key, value in keys.items():
        thiscolor = colors.get(key)
        
        if f'Slope{value}' in chart.columns:     
            figure.add_trace(go.Scatter(x=chart.index, y=chart[f'Slope{value}'], name=f'{value} Slope', mode="lines", line=dict(color=thiscolor, width=2)), row=row, col=col)
    
    return figure


def plot_basicchart(filename, currency, chart, auto_open=False, keys={"S":5, "M":25, "L":75, "LL":200}):
    """ろうそく足のプロット
    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.8, 0.2], x_title="Date")

    # グラフの設定
    fig = add_graphsetting(fig)
    
    # X軸から空白期間を除外する
    # fig = remove_gap_datetime(fig, chart)
    fig = remove_weekend(fig, chart)
    
    fig = add_candlestick(fig, chart, 1, 1, keys, show_swing=False, show_order=True)
    fig = add_volume(fig, chart, 2, 1) 
    
    # プロット
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)


def plot_with_rci(filename, currency, chart, auto_open=False, keys={"S":5, "M":25, "L":75, "LL":200}):
    """乖離率とのプロット
    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.7, 0.3], x_title="Date")
    
    # グラフの設定
    fig = add_graphsetting(fig)
    
    # X軸から空白期間を除外する
    fig = remove_gap_datetime(fig, chart)
    
    fig = add_candlestick(fig, chart, 1, 1, keys, show_swing=True, show_order=True)
    fig = add_rci(fig, chart, 2, 1)
    
    # プロット
    # plotly.offline.plot(fig, auto_open=auto_open, image = 'png', image_filename='plot_image', output_type='file', image_width=800, image_height=600)
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)
    

def plot_with_dr(filename, currency, chart, auto_open=False, keys={"S":5, "M":25, "L":75, "LL":200}):
    """乖離率とのプロット
    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.7, 0.3], x_title="Date")
    
    # グラフの設定
    fig = add_graphsetting(fig)
    
    # X軸から空白期間を除外する
    fig = remove_gap_datetime(fig, chart)
    
    fig = add_candlestick(fig, chart, 1, 1, keys)
    fig = add_deviationrate(fig, chart, 2, 1, keys)
    
    # プロット
    # plotly.offline.plot(fig, auto_open=auto_open, image = 'png', image_filename='plot_image', output_type='file', image_width=800, image_height=600)
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)
    
    
def plot_with_sigma(filename, currency, chart, auto_open=False, keys={"S":5, "M":20, "L":60, "LL":200}):
    """シグマとのプロット
    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.7, 0.3], x_title="Date")
    
    # グラフの設定
    fig = add_graphsetting(fig)
    
    # X軸から空白期間を除外する
    fig = remove_gap_datetime(fig, chart)
    
    fig = add_candlestick(fig, chart, 1, 1, keys)
    fig = add_sigma(fig, chart, 2, 1, keys)
    
    # プロット
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)

def plot_with_slope(filename, title, chart, auto_open=False, keys={"S":5, "M":20, "L":60, "LL":200}):
    """シグマとのプロット
    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.7, 0.3], x_title="Date")
    
    # グラフの設定
    fig = add_graphsetting(fig)
    
    # X軸から空白期間を除外する
    fig = remove_gap_datetime(fig, chart)
    
    fig = add_candlestick(fig, chart, 1, 1)
    fig = add_slope(fig, chart, 2, 1)
    
    # プロット
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)

def plot_with_heikinashi_candlestick(filename, title, chart, auto_open=False, keys={"S":5, "M":20, "L":60, "LL":200}):
    """平均足チャートとのプロット
    """
    # fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[1.0], x_title="Date")
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.8, 0.2], x_title="Date")
    
    # グラフの設定
    fig = add_graphsetting(fig)
    
    # X軸から空白期間を除外する
    fig = remove_gap_datetime(fig, chart)
    
    fig = add_candlestick(fig, chart, 1, 1)
    fig = add_heikinashi_candlestick(fig, chart, 1, 1)
    fig = add_rci(fig, chart, row=2, col=1)
    
    # プロット
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)

def plot_with_heikinashi_bar(filename, title, chart, auto_open=False, keys={"S":5, "M":20, "L":60, "LL":200}):
    """平均足チャートとのプロット
    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.9, 0.1], x_title="Date")
    
    # グラフの設定
    fig = add_graphsetting(fig)
    
    # X軸から空白期間を除外する
    fig = remove_gap_datetime(fig, chart)
    
    fig = add_candlestick(fig, chart, 1, 1)
    fig = add_heikinashi_bar(fig, chart, 2, 1)
    
    # プロット
    plotly.offline.plot(fig, filename=filename, show_link=True, auto_open=auto_open)

def plot_with_heikinashi_candlestick2(filename, title, ohlc, heikinashi, auto_open=False, keys={"S":5, "M":25, "L":75, "LL":200}):
    """平均足チャートとのプロット
    """
    # fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[1.0], x_title="Date")
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.5, 0.5], x_title="Date")
    
    # グラフの設定
    fig = add_graphsetting(fig)
    
    # X軸から空白期間を除外する
    fig = remove_gap_datetime(fig, ohlc)
    fig = remove_gap_datetime(fig, heikinashi)
    
    fig = add_candlestick(fig, ohlc, 1, 1, keys, show_swing=False, show_bollinger=True, show_order=False)
    fig = add_heikinashi2(fig, heikinashi, 2, 1)
    
    # プロット
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)


def plot_simulationchart(filename, currency, chart, auto_open=False, keys={"S":5, "M":25, "L":75, "LL":200}):
    """ろうそく足のプロット
    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.7, 0.3], x_title="Date")

    # グラフの設定
    fig = add_graphsetting(fig)
    
    # X軸から土日を除外する
    fig = remove_weekend(fig, chart)
    
    fig = add_candlestick(fig, chart, 1, 1, keys, show_swing=False, show_bollinger=True, show_order=True)
    fig = add_rci(fig, chart, 2, 1)
    # fig = add_volume(fig, chart, 3, 1)
    
    # プロット
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)
    
def plot_simulationchart2(filename, currency, chart, auto_open=False, keys={"S":5, "M":25, "L":75, "LL":200}):
    """ろうそく足のプロット
    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01, row_heights=[0.7, 0.3], x_title="Date")

    # グラフの設定
    fig = add_graphsetting(fig)
    
    # X軸から土日を除外する
    fig = remove_weekend(fig, chart)
    
    fig = add_candlestick(fig, chart, 1, 1, keys, show_swing=False, show_bollinger=True, show_order=True)
    fig = add_volume(fig, chart, 2, 1)
    
    # プロット
    plotly.offline.plot(fig, filename=filename, auto_open=auto_open)
    
    # print('test')
    # plotly.offline.plot(fig, image='png', image_filename='test.png', output_type='file', image_width=1000, image_height=600, auto_open=False)
    
    
if __name__ == "__main__":
    import indicator    
    os.system('cls')

    # pandasのprint表示の仕方を設定
    pandas.set_option('display.max_rows', None)
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.width', 1000)

    tickers_list = pandas.DataFrame()
    tickers_list = pandas.read_csv('tickers_list.csv', header=0, index_col=0)
    
    htmlfolder = 'html'
    os.makedirs(htmlfolder, exist_ok=True) 
    ohlcfolder = chart_days.daily_all_folder
    
    # tickers_list = tickers_list.head(20)
    for ticker, row in tickers_list.iterrows():
        print (f'{ticker}:')
        param = [5, 25, 75, 200]
        ohlc =  pandas.read_csv(f'{ohlcfolder}/{ticker}.csv', index_col=0, parse_dates=True)
        
        # if ohlcfolder == chart_days.per1minute_folder:
        #     rule = '5T'
        #     d_ohlcv = {'Open':'first', 'High':'max', 'Low':'min', 'Close':'last', 'Volume':sum}
        #     ohlc = ohlc.resample(rule).agg(d_ohlcv)
        #     ohlc = ohlc.dropna()
                    
        ohlc = indicator.add_basic(ohlc, param)
        ohlc = indicator.add_sma_dr(ohlc, param)
        ohlc = indicator.add_swing_high_low(ohlc)
        # heikinashi = indicator.create_heikinashi(ohlc)
        
        ohlc = ohlc.tail(1000)
        # heikinashi = heikinashi.tail(500)
        # plot_with_dr(f'{htmlfolder}/{ticker}.html', ticker, ohlc)
        plot_basicchart(f'{htmlfolder}/{ticker}.html', ticker, ohlc)
        
        
        
        
        
    #       S   M   L   LL
    # day   5   25  75  200 
    # week  25  75  375