import datetime
import glob, os
import pandas as pd 

files = glob.glob('*.csv')
files = [f for f in files if 'combined_table' in f]
files = sorted(files, key=os.path.getctime, reverse=True)

df = pd.read_csv(files[0])

# remove trailing spaces from column data
for c in df.columns:
    try:
        df[c] = df[c].apply(lambda x: x.strip())
    except:
        pass

df['TradeDate_dt'] = pd.to_datetime(df['TradeDate'])

# if there isn't a report gap, it will cause an error later.
# TODO: handle this better
df = df.loc[df['ReportGap'].notna()]
df['PubDate'] = df['TradeDate_dt'] + pd.to_timedelta(df['ReportGap'], unit='d')

df['PubDate_dt'] = pd.to_datetime(df['PubDate'])

df['day_diff_report'] = df['PubDate_dt'] - df['TradeDate_dt']
df['day_diff_today'] = df['PubDate_dt'] - datetime.datetime.today()
df['30days_report'] = 'f'
df['30days_today'] = 'f'
filt = df['day_diff_report']<=pd.to_timedelta(30, unit='d')
df['30days_report'] = df['30days_report'].mask(filt, 't')
filt2 = df['day_diff_today']<=pd.to_timedelta(30, unit='d')
df['30days_today'] = df['30days_today'].mask(filt2, 't')

df['Ticker'] = df['Ticker'].fillna('')
df['Ticker'] = df['Ticker'].str.replace('N/A', '')
df['Ticker'] = df['Ticker'].str.replace(':US', '')
df['Ticker - Info'] = df['Ticker'] + ' - ' + df['Issuer']
df['Ticker - Info'] = df['Ticker - Info'].apply(lambda x: x[:45])

df3 = df.loc[df['30days_report']=='t'] # trades that were reported within 30 days of the trade occurring
# df3 = df3.loc[df3['30days_today']=='t'] # of those trades, trades that have been reported within 30 days of today
df3 = df3.drop_duplicates()

today_str = datetime.datetime.today().strftime('%Y-%m-%d')
df3.to_csv(f'{today_str}_potential_trades.csv', index=False)