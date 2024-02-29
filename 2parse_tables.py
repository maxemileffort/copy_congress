from datetime import datetime
import glob, os, re

from bs4 import BeautifulSoup
import pandas as pd

txt_files = glob.glob('*.txt')
txt_files = sorted(txt_files, key=os.path.getctime, reverse=True)
target_file = txt_files[0]

with open(target_file, 'r') as infile:
    html = infile.read()

soup = BeautifulSoup(html, 'html.parser')

# Find all tables in the HTML
tables = soup.find_all('table')

# Process each table in a list comprehension and concatenate the results
df = pd.concat([
    pd.DataFrame([{
        'Politician': row.find('h3', class_='politician-name').text if row.find('h3', class_='politician-name') else None,
        'Issuer': row.find('h3', class_='issuer-name').text if row.find('h3', class_='issuer-name') else None,
        'Ticker': row.find('span', class_='q-field issuer-ticker').text if row.find('span', class_='q-field issuer-ticker') else None,
        'ReportGap': row.find('span', class_="reporting-gap-tier--2").text if row.find('span', class_="reporting-gap-tier--2") else None,
        'TradeDate': row.find('div', class_='q-cell cell--tx-date').text if row.find('div', class_='q-cell cell--tx-date') else None,
        'Size': row.find('div', class_='q-range-icon-wrapper').text if row.find('div', class_='q-range-icon-wrapper') else None,
        'Direction': row.find('div', class_='q-cell cell--tx-type').text if row.find('div', class_='q-cell cell--tx-type') else None,
        'Price': row.find('div', class_="q-cell cell--trade-price").text if row.find('div', class_="q-cell cell--trade-price") else None,
    } for row in table.find_all('tr') if row.find('td', class_='q-column--issuer')])
    for table in tables
], ignore_index=True)

today_str = datetime.today().strftime('%Y-%m-%d')

# Save the combined dataframe to a new CSV file
df.to_csv(f'{today_str}_combined_table.csv', index=False)
