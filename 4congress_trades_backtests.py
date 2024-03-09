# -*- coding: utf-8 -*-
"""Congress Trades - Backtests.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1M6-niDqPAgMFJylcWAiuWQVKjvGt7bIp

# Imports
"""

#ignoring warnings
import warnings
warnings.simplefilter('ignore')

#importing neccesary modules
from datetime import datetime
import sys
import pandas as pd
import pandas_ta as ta
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')
import seaborn as sns

from backtesting import Backtest, Strategy

import yfinance as yf

"""# Download Data"""

import glob

files = glob.glob('*.csv')
df = pd.read_csv(files[0])
df['Ticker'] = df['Ticker'].str.replace(':US', '')
df = df.dropna(subset=['Ticker'])
df['TradeDate_dt'] = pd.to_datetime(df['TradeDate_dt'])
df['PubDate_dt'] = pd.to_datetime(df['PubDate_dt'])

df.head(3)

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
                       group_by='ticker')
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
for i in unique_insiders:
  print(i)
  sub_df = df.loc[df['Politician']==i]
  insiders_tickers = sub_df['Ticker'].unique()

  for t in insiders_tickers:
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
    data_with_sig = prices.merge(sub_df2,
                                  right_on=['TradeDate_dt'],
                                  left_on=['index'],
                                  how='outer')
    data_with_sig = data_with_sig.set_index('index')
    data_with_sig['TradeDate_dt'] = data_with_sig['TradeDate_dt'].fillna(datetime.today())
    data_with_sig = data_with_sig.loc[data_with_sig['Open'].notna()]
    # print(data_with_sig)
    # Run backtest
    try:
      bt = Backtest(data_with_sig, CongressTradesStrategy1, cash=10000, commission=.002)
    except ValueError as ve:
      print(f'value error: {ve}')
      continue
    results = bt.run()
    bts.append([bt, i, t])
    res = pd.DataFrame(results).T
    res['Politician'] = i
    res['Ticker'] = t
    res_df = pd.concat([res_df,res])

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
group_df

# Define your backtesting strategy
class CongressTradesStrategy2(Strategy):
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

bts2 = [] # for visualizing later
res_df2 = pd.DataFrame()
for i in unique_insiders:
  print(i)
  sub_df = df.loc[df['Politician']==i]
  insiders_tickers = sub_df['Ticker'].unique()

  for t in insiders_tickers:
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
    data_with_sig = prices.merge(sub_df2,
                                  right_on=['PubDate_dt'],
                                  left_on=['index'],
                                  how='outer')
    data_with_sig = data_with_sig.set_index('index')
    data_with_sig['PubDate_dt'] = data_with_sig['PubDate_dt'].fillna(datetime.today())
    data_with_sig = data_with_sig.loc[data_with_sig['Open'].notna()]
    # print(data_with_sig)
    # Run backtest
    try:
      bt = Backtest(data_with_sig, CongressTradesStrategy1, cash=10000, commission=.002)
    except ValueError as ve:
      print(f'value error: {ve}')
      continue
    results = bt.run()
    bts2.append([bt, i, t])
    res2 = pd.DataFrame(results).T
    res2['Politician'] = i
    res2['Ticker'] = t
    res_df2 = pd.concat([res_df2,res2])

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
group_df2

"""# Visualize Backtest Results"""

for bt in bts:
  print(bt[1] + " : " + bt[2])
  print('=====')
  try:
    bt[0].plot()
  except ValueError as ve:
    print(f'value error: {ve}')
  print('=====')

for bt in bts2:
  print(bt[1] + " : " + bt[2])
  print('=====')
  try:
    fig = bt[0].plot()
    fig.savefing(f'{bt[1]} {bt[2]}.png')
  except ValueError as ve:
    print(f'value error: {ve}')
  print('=====')

from datetime import datetime

today_str = datetime.today().strftime('%Y-%m-%d')

from fpdf import FPDF #

imagelist = sorted(glob.glob(f'*.png'))

pdf = FPDF()
for i in range(0, len(imagelist)):
  pdf.add_page()
  pdf.image(imagelist[i], w=170)
file_name = f"{today_str}_insider_trading_copying.pdf"
pdf.output(file_name, "F")

from google.colab import files
files.download(file_name)