"""
株価の銘柄リストを更新する
"""
import pandas
import datetime
from kabutan import Kabutan

list_filename = 'tickers_list.csv'

def update_list():
    """
    銘柄リストを更新する
    """
    output_filename = list_filename
    
    url = 'https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls'
    tickers_list = pandas.read_excel(url, index_col=1)

    # ETF, ETNは除く    
    tickers_list = tickers_list[tickers_list['市場・商品区分']!='ETF・ETN']
    tickers_list = tickers_list[tickers_list['市場・商品区分']!='PRO Market']
    tickers_list = tickers_list[tickers_list['市場・商品区分']!='REIT・ベンチャーファンド・カントリーファンド・インフラファンド']
    tickers_list = tickers_list[tickers_list['市場・商品区分']!='出資証券']
    
    for ticker, row in tickers_list.iterrows():
        print(ticker)
        
    print('end')
    # 5ケタ以上は除く
    # tickers_list = tickers_list[tickers_list.index < 10000]
     
    # Dataframeに列を追加
    tickers_list['出来高'] = 0
    tickers_list['売買代金'] = 0
    tickers_list['VWAP'] = 0
    tickers_list['約定回数'] = 0
    tickers_list['時価総額'] = 0
    tickers_list['発行株式'] = 0
    
    for ticker, row in tickers_list.iterrows():
        # print(tickers_list.at[ticker,'発行株式'])        
        # print(tickers_list.at[ticker,'発行株式'] == 0)
        print(ticker, ' :', datetime.datetime.now())
        
        kabutan = Kabutan(ticker)
               
        tickers_list.at[ticker,'出来高'] = kabutan.volume
        tickers_list.at[ticker,'売買代金'] = kabutan.tradingvalue
        tickers_list.at[ticker,'VWAP'] = kabutan.vwap
        tickers_list.at[ticker,'約定回数'] = kabutan.tick
        tickers_list.at[ticker,'時価総額'] = kabutan.capitalization
        tickers_list.at[ticker,'発行株式'] = kabutan.sharedunderstanding
        # print(tickers_list.at[ticker,'発行株式'])
     
    # 保存
    tickers_list.to_csv(output_filename)    
    
if __name__ == "__main__":
   
    # pandasのprint表示の仕方を設定
    pandas.set_option('display.max_rows', None)
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.width', 1000)

    update_list()

            
