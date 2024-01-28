import pandas
import datetime
import os
import time
import numpy
import indicator
import chart_plot
import chart_days

import mplfinance

# コンフィグ
# gdrivepath = '/content/drive/My Drive/stock/'
basepath = './'
encode = 'utf-8'

chart_folder = chart_days.daily_all_folder
todayspickup_folder = 'todayspickup'
todayspickup_filename = f'./{todayspickup_folder}/master.csv'

def create_tickers(debug=False):
    """ シミュレーション
    """ 
    tickers_list = pandas.DataFrame()
    tickers_list = pandas.read_csv('tickers_list.csv', header=0, index_col=0)
    # tickers_list = tickers_list[tickers_list.index == 2934] # Jフロンティア
    # tickers_list = tickers_list[tickers_list.index == 2437] # シンワワイズ
    # tickers_list = tickers_list[tickers_list.index == 4174] # アピリッツ
    tickers_list = tickers_list[tickers_list.index == 3624] # アクセルマーク
    # tickers_list = tickers_list.head(10)
    
    count_Buy = 0
    count_Up1 = 0
    count_Up1_1 = 0
    count_Up2 = 0
    count_Up2_1 = 0
    
    
    for ticker, row in tickers_list.iterrows():
        # if ticker != 2138:
        #     continue
        if debug == True:
            print('ticker: ', ticker)

        # ファイルが存在しなければ、何もしない
        file_name = f'{chart_folder}/{ticker}.csv'   
        if not os.path.exists(file_name):
            continue
        
        chart = pandas.DataFrame()
        try:
            chart =  pandas.read_csv(file_name, index_col=0, parse_dates=True)
        except:
            pass

        chart = indicator.add_sma(chart, [5, 25, 75, 100, 200])
        chart = indicator.add_sma_slope(chart, [5, 25, 75])
        chart = indicator.add_swing_high_low(chart, 5, True)
        chart = indicator.add_candlestick_pattern(chart)
        chart = indicator.add_sma_pattern(chart)
        chart = indicator.add_rci(chart)
        
        # 買いの条件
        # chart['Buy'] = (chart['Close'] > chart['SMA75']) & (chart['Low'] < chart['SMA75']) & (chart['Close'] > chart['SwingHigh']) #& (chart['Ashi2'] == '陽たすき')
        chart['Buy'] = (chart['Close'] > chart['SMA75']) & (chart['Close'] > chart['SwingHigh']) & (chart['Close'].shift() < chart['SMA75'])
        # chart['Buy'] = (chart['Close'] > chart['SMA75']) & (chart['Close'] > chart['SwingHigh'])
        
        # 買い時のプライス情報
        chart['BuyClose'] = numpy.nan
        chart['BuyClose'].mask(chart['Buy'], chart['Close'], inplace=True)
        chart['BuyClose'].fillna(method='ffill', inplace=True)
        chart['BuyOpen'] = numpy.nan
        chart['BuyOpen'].mask(chart['Buy'], chart['Open'], inplace=True)
        chart['BuyOpen'].fillna(method='ffill', inplace=True)        
        chart['BuyHigh'] = numpy.nan
        chart['BuyHigh'].mask(chart['Buy'], chart['High'], inplace=True)
        chart['BuyHigh'].fillna(method='ffill', inplace=True)        
        chart['BuyLow'] = numpy.nan
        chart['BuyLow'].mask(chart['Buy'], chart['Low'], inplace=True)
        chart['BuyLow'].fillna(method='ffill', inplace=True)        
        
        # ロスカット条件
        chart['Sell'] = (chart['Close'] < chart['BuyLow']) & (chart['Close'].shift() >= chart['BuyLow']) # 買ったときの安値を終値が下回ったとき
        chart['Sell'] |= (chart['Close'] < chart['SMA75']) & (chart['Close'].shift() >= chart['SMA75']) # または、SMAを下回ったとき
    
        # print(chart[['Buy', 'Sell', 'SwingHigh', 'BuyClose', 'BuyLow', 'UnderUp', 'UnderUpHigh']].tail(2000))
        
        chart['Up1'] = chart['Buy'] & (chart['High'].shift(-1) > chart['Close']) # 翌日の高値
        chart['Up1_1'] = chart['Buy'] & (chart['High'].shift(-1) > chart['Close']) & (chart['Close'].shift(-1) > chart['Open'].shift(-1)) # 翌日の高値、かつ、陽線
        chart['Up2'] = chart['Buy'] & (chart['Close'].shift(-1) > chart['Close']) # 翌日の終値
        chart['Up2_1'] = chart['Buy'] & (chart['Close'].shift(-1) > chart['Close']) & (chart['Close'].shift(-1) > chart['Open'].shift(-1)) # 翌日の終値、かつ、陽線
        
        count_Buy += chart['Buy'].sum()
        count_Up1 += chart['Up1'].sum()
        count_Up1_1 += chart['Up1_1'].sum()
        count_Up2 += chart['Up2'].sum()
        count_Up2_1 += chart['Up2_1'].sum()
        
        save_filename = f'./simulation/{ticker}_.html'
        chart = indicator.add_bb(chart, [5, 25, 75, 100, 200])
        chart_plot.plot_simulationchart(save_filename, ticker, chart, False)
        # heikinashi = indicator.create_heikinashi(chart)
        # chart_plot.plot_with_heikinashi_candlestick2(save_filename, ticker,chart.tail(200), heikinashi.tail(200), False)
        
        chart = chart.tail(200)
        marketcolors = mplfinance.make_marketcolors(up='red',           # 上昇時のろうそくの塗りつぶし色
                                                    down='green',       # 下降時のろうそくの塗りつぶし色
                                                    inherit=True,       # エッジカラーを同じにする
                                                    wick={'up':'red', 'down':'green'}   # 上昇時、下降時のろうそくの芯の色
                                                    )
        cs  = mplfinance.make_mpf_style(marketcolors=marketcolors, 
                                        gridcolor="darkgray",           # チャートのグリッド色
                                        facecolor="black",              # チャートの背景色
                                        gridstyle=":"                  # チャートのグリッドの種類 "-":実線, "--":破線, ":":点線, "-.":破線と点線の組み合わせ
                                        )
        apd = [ mplfinance.make_addplot(chart['SMA5'], color="yellow"), mplfinance.make_addplot(chart['SMA25'], color="red"), mplfinance.make_addplot(chart['SMA75'], color="green")]
        mplfinance.plot(chart, type='candle', datetime_format='%Y/%m/%d', savefig=dict(fname='test.png', dpi=500), figratio=(2,1), addplot=apd, style=cs, volume=True)
        
        print(chart.tail(2))
        
    print('Buy:', count_Buy)
    print('Up1:', count_Up1, ':', count_Up1_1)
    print('Up2:', count_Up2, ':', count_Up2_1)
    print('勝率1:', round(float(count_Up1)/count_Buy*100, 0), ' %')
    print('勝率2:', round(count_Up2/count_Buy*100, 0), ' %')
        # print(chart['Buy'].sum())
        # print(chart['Up1'].sum())
        # print(chart['Up2'].sum())
        # period = 5
        # chart[f'max{period}'] = chart['High'].rolling(window=period, center=False, axis=0, min_periods=1).max().shift(-period)
        # chart[f'max{period}'].interpolate(methid='pad', inplace=True)
        # chart[f'min{period}'] = chart['Low'].rolling(window=period, center=False, axis=0, min_periods=1).min().shift(-period)
        # chart[f'min{period}'].interpolate(methid='pad', inplace=True)
        
        # print(chart.tail(1000))
    #     indicator.add_basic(chart, [5, 25, 75, 100])
    #     indicator.add_swing_high_low(chart)
    #     # print(chart)
    #     indicator.add_candlestick_pattern(chart)
    #     indicator.add_sma_pattern(chart)

    #     chart['出来高前日差'] = chart['Volume'].diff()
    #     chart['出来高前日比'] = (chart['Volume'] / chart['Volume'].shift(1)).round(1)
    #     chart['出来高発行株式割合'] = (chart['Volume'] / row['発行株式'] * 100).round(1)
    #     chart['陽線陰線'] = '→'
    #     chart['陽線陰線'].mask((chart['Close'] > chart['Open']), '↑', inplace=True)
    #     chart['陽線陰線'].mask((chart['Close'] < chart['Open']), '↓', inplace=True)
    #     # chart['75over'] = 0
    #     # chart['75over'].mask((chart['Close'] > chart['Open']) & (chart['Low'] <= chart['SMA75']) & (chart['High'] > chart['SMA75']), '1', inplace=True) # 突き抜け
    #     # chart['75over'].mask((chart['Low'] > chart['SMA75']) & (chart['High'] > chart['SMA75']), '2', inplace=True) # 上
    #     # chart['25over'] = 0
    #     # chart['25over'].mask((chart['Close'] > chart['Open']) & (chart['Low'] <= chart['SMA25']) & (chart['High'] > chart['SMA25']), '1', inplace=True) # 突き抜け
    #     # chart['25over'].mask((chart['Low'] > chart['SMA25']) & (chart['High'] > chart['SMA25']), '2', inplace=True) # 上
        
    #     y = chart[chart['SwingHigh']>0]
    #     takane = 0
    #     if not y.empty:
    #         takane = y.iloc[-1]['SwingHigh'] 
        
    #     chart['Swinghighover'] = 0
    #     chart['Swinghighover'].mask((chart['Close'] >= takane), '1', inplace=True)
    #     # chart['三平'] = 'None'
    #     # chart['三平'].mask(((chart['Close'] > chart['Open']) & (chart['Close'].shift(1) > chart['Open'].shift(1)) & (chart['Close'].shift(2) > chart['Open'].shift(2)) 
    #     #                   & (chart['High'] >= charｇt['High'].shift(1)) & (chart['High'].shift(1) >= chart['High'].shift(2))
    #     #                   & (chart['Low'] >= chart['Low'].shift(1)) & (chart['Low'].shift(1) >= chart['Low'].shift(2))), 
    #     #                  'Red', inplace=True)
    #     # chart['三平'].mask(((chart['Close'] < chart['Open']) & (chart['Close'].shift(1) < chart['Open'].shift(1)) & (chart['Close'].shift(2) < chart['Open'].shift(2)) 
    #     #                   & (chart['High'] <= chart['High'].shift(1)) & (chart['High'].shift(1) <= chart['High'].shift(2))
    #     #                   & (chart['Low'] <= chart['Low'].shift(1)) & (chart['Low'].shift(1) <= chart['Low'].shift(2))), 
    #     #                  'Black', inplace=True)        
        
    #     date = chart.index[-1]              
    #     name = row['銘柄名']
    #     shares = row['発行株式']
    #     diff = chart.at[date, '出来高前日差']
    #     volume = chart.at[date, 'Volume']
    #     sharesratio = chart.at[date, '出来高発行株式割合']
    #     previousratio = chart.at[date, '出来高前日比']
    #     pn = chart.at[date, '陽線陰線']   
    #     # sanpei = chart.at[date, '三平']
    #     sanpei = chart.at[date, 'Hei']
    #     ku = chart.at[date, 'Ku']
    #     over75 = chart.at[date, 'over75']
    #     over25 = chart.at[date, 'over25']
    #     ashi1 = chart.at[date, 'Ashi1']
    #     ashi2 = chart.at[date, 'Ashi2']
    #     swinghigh = chart.at[date, 'Swinghighover']

    #     test_chart = pandas.DataFrame({'銘柄名':[name], 
    #                                    '陽線陰線':[pn], 
    #                                    '出来高':[volume], 
    #                                    '出来高前日差':[diff], 
    #                                    '出来高発行株式割合':[sharesratio], 
    #                                    '出来高前日比':[previousratio],
    #                                    '三平':[sanpei], 
    #                                    '空':[ku],
    #                                    '25SMA越':[over25],
    #                                    '75SMA越':[over75],
    #                                    '足1':[ashi1],
    #                                    '足2':[ashi2],
    #                                    '直近高値越':[swinghigh],
    #                                    },
    #                                   index=[ticker])
    
    #     ticker_chart = pandas.concat([ticker_chart, test_chart], sort=False,)

    # # infを0に変換
    # ticker_chart = ticker_chart.replace([numpy.inf, -numpy.inf], numpy.nan)
    # ticker_chart = ticker_chart.fillna(0) # 0でnanを置換
    
    # # 保存
    # os.makedirs(todayspickup_folder, exist_ok=True)  
    # ticker_chart.to_csv(todayspickup_filename, header=True)

    
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
    # change_view()
