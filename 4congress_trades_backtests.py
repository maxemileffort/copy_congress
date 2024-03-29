#ignoring warnings
import warnings
warnings.simplefilter('ignore')

#importing neccesary modules
from datetime import datetime
import os,sys
import pandas as pd
import pandas_ta as ta
import numpy as np

from backtesting import Backtest, Strategy

import yfinance as yf

"""# Download Data"""

import glob

start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

old_html_files = glob.glob('*.html')
for f in old_html_files:
   os.remove(f)

# find correct file and load
files = glob.glob('*.csv')
files = [f for f in files if 'potential_trades' in f]
files = sorted(files,
               key=os.path.getmtime,
               reverse=True)
df = pd.read_csv(files[0])

df['Ticker'] = df['Ticker'].str.replace(':US', '')
df = df.dropna(subset=['Ticker'])
df['TradeDate_dt'] = pd.to_datetime(df['TradeDate_dt']).dt.date
df['PubDate_dt'] = pd.to_datetime(df['PubDate_dt']).dt.date

for t in df['Politician'].unique():
  print(t)

start_date = df['TradeDate_dt'].min()
end_date = datetime.now().strftime('%Y-%m-%d')  # Current date for the end date

# Function to fetch historical data for a given ticker
def fetch_historical_data(tickers, start_date, end_date):
    tickers_str = ' '.join(tickers)
    tickers_str = tickers_str.replace('$ETH', 'ETH-USD')
    tickers_str = tickers_str.replace('$BTC', 'BTC-USD')
    tickers_str = tickers_str.replace('$LTC', 'LTC-USD')
    tickers_str = tickers_str.replace('BRK/B', '')
    tickers_str = tickers_str.replace('BF/A', '')
    data = yf.download(tickers_str,
                       start=start_date,
                       end=end_date,
                       group_by='ticker',
                       ignore_tz=True)
    return data

# Filter out rows with NaN in 'Ticker' column and prepare a list of unique tickers
df = df.dropna(subset=['Ticker'])
unique_tickers = df['Ticker'].unique()
unique_insiders = df['Politician'].unique()

# Fetch historical data for the ticker
tickers = df['Ticker'].unique().tolist()
historical_data = fetch_historical_data(tickers, start_date, end_date)

# Define your backtesting strategy
class CongressTradesStrategy1(Strategy):
    def init(self):
        # Your initialization logic here
        super().init()
        self.mysize = .99

    def next(self):
        # Implement your strategy that uses trades from the CSV

        if self.data.Direction == 'buy':
            self.buy(size=self.mysize)
        elif self.data.Direction == 'sell':
            self.sell(size=self.mysize)

bts = [] # for visualizing later
res_df = pd.DataFrame()

bts2 = [] # for visualizing later
res_df2 = pd.DataFrame()

for i in unique_insiders:
  # print(i)
  sub_df = df.loc[df['Politician']==i]
  insiders_tickers = sub_df['Ticker'].unique()

  for t in insiders_tickers:
    # print(t)
    t = t.replace('$ETH', 'ETH-USD')
    t = t.replace('$BTC', 'BTC-USD')
    t = t.replace('$LTC', 'LTC-USD')
    sub_df2 = sub_df.loc[sub_df['Ticker']==t]
    try:
      prices = historical_data[t]
    except KeyError:
      print(f'cannot find {t} ticker.')
      continue
    prices['index'] = prices.index
    prices['index'] = pd.to_datetime(prices['index']).dt.date

    # create dataset based on trade date
    data_with_sig = prices.merge(sub_df2,
                                  right_on=['TradeDate_dt'],
                                  left_on=['index'],
                                  how='outer')
    data_with_sig = data_with_sig.set_index('index')
    data_with_sig['TradeDate_dt'] = data_with_sig['TradeDate_dt'].fillna(datetime.today())
    data_with_sig = data_with_sig.loc[data_with_sig['Open'].notna()]

    # create dataset based on published date
    data_with_sig2 = prices.merge(sub_df2,
                                  right_on=['PubDate_dt'],
                                  left_on=['index'],
                                  how='outer')
    data_with_sig2 = data_with_sig2.set_index('index')
    data_with_sig2['PubDate_dt'] = data_with_sig2['PubDate_dt'].fillna(datetime.today())
    data_with_sig2 = data_with_sig2.loc[data_with_sig2['Open'].notna()]

    # Run backtests
    try:
      bt = Backtest(data_with_sig, CongressTradesStrategy1, cash=10000, commission=.002)
      bt2 = Backtest(data_with_sig2, CongressTradesStrategy1, cash=10000, commission=.002)
    except ValueError as ve:
      print(f'value error: {ve}')
      continue
    results = bt.run()
    results2 = bt2.run()

    bts.append([bt, i, t])
    bts2.append([bt2, i, t])

    res = pd.DataFrame(results).T
    res['Politician'] = i
    res['Ticker'] = t
    res_df = pd.concat([res_df,res])

    res2 = pd.DataFrame(results2).T
    res2['Politician'] = i
    res2['Ticker'] = t
    res_df2 = pd.concat([res_df2,res2])

"""## Results Table 1"""

group_df = res_df.groupby(['Politician']).agg({
    'Equity Final [$]': 'sum',
    '# Trades': 'sum',
    'Win Rate [%]': 'mean',
    'Ticker': pd.Series.nunique
})
group_df['Start Amount'] = group_df['Ticker'] * 10*1000
return_num = (group_df['Equity Final [$]'] - group_df['Start Amount'])
group_df['Return'] = return_num / group_df['Start Amount']
group_df = group_df.sort_values('Return', ascending=False)
group_df.to_csv(f'{end_date}_trade_dt_stats.csv')

"""## Results Table 2"""

group_df2 = res_df2.groupby(['Politician']).agg({
    'Equity Final [$]': 'sum',
    '# Trades': 'sum',
    'Win Rate [%]': 'mean',
    'Ticker': pd.Series.nunique
})
group_df2['Start Amount'] = group_df2['Ticker'] * 10*1000
return_num = (group_df2['Equity Final [$]'] - group_df2['Start Amount'])
group_df2['Return'] = return_num / group_df2['Start Amount']
group_df2 = group_df2.sort_values('Return', ascending=False)
group_df2.to_csv(f'{end_date}_pub_dt_stats.csv')

"""# Visualize Backtest Results"""

# save backtest plots as html
for bt1, bt2 in zip(bts,bts2):
  print(bt1[1] + " : " + bt1[2])
  print('=====')
  try:
    bt1[0].plot(filename=f'html/{bt1[1]} {bt1[2]}_trade_dates.html', 
               open_browser=False)
    bt2[0].plot(filename=f'html/{bt2[1]} {bt2[2]}_pub_dates.html', 
               open_browser=False)
  except ValueError as ve:
    print(f'value error: {ve}')
  print('=====')

end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

print('start_time: ',start_time)
print('end_time: ',end_time)