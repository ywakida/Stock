import pandas
import datetime
import os
import time
import numpy
import indicator
import chart_plot
import chart_days

# コンフィグ
# gdrivepath = '/content/drive/My Drive/stock/'
basepath = './'
encode = 'utf-8'

chart_folder = chart_days.daily_all_folder
todayspickup_folder = 'todayspickup'
todayspickup_filename = f'./{todayspickup_folder}/master.csv'

pickuptest_folder = 'pickuptest'
os.makedirs(pickuptest_folder, exist_ok=True)


def create_tickers(debug=False):
    """ シミュレーション
    """ 
    tickers_list = pandas.DataFrame()
    tickers_list = pandas.read_csv('tickers_list.csv', header=0, index_col=0)
    # tickers_list = tickers_list[tickers_list.index == 2934] # Jフロンティア
    # tickers_list = tickers_list[tickers_list.index == 2437] # シンワワイズ
    # tickers_list = tickers_list[tickers_list.index == 3434] # アルファCo
    tickers_list = tickers_list[tickers_list.index == 4760] # アルファ
    
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
        
        # 買いの条件
        # chart['Buy'] = (chart['Close'] > chart['SMA75']) & (chart['Low'] < chart['SMA75']) & (chart['Close'] > chart['SwingHigh']) #& (chart['Ashi2'] == '陽たすき')
        chart['Buy'] = (chart['Close'] > chart['SMA75']) & (chart['Close'] > chart['SwingHigh']) & (chart['Close'].shift() < chart['SMA75'])
        # chart['Buy'] = (chart['Close'] > chart['SMA75']) & (chart['Close'] > chart['SwingHigh'])    
                 
        save_filename = f'./{pickuptest_folder}/{ticker}.html'
        # chart = indicator.add_bb(chart, [5, 25, 75, 100, 200])
        chart_plot.plot_simulationchart2(save_filename, ticker, chart, False)
        

    
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
