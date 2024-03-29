from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time

# Setup ChromeDriver (make sure it's installed and in PATH)
chrome_options = Options()
chrome_options.add_argument("--headless")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

base_url = ('https://www.capitoltrades.com/trades?per_page=96'
            + '&assetType=crypto&assetType=etf&assetType=etn&'
            + 'assetType=futures&assetType=hedge-pvt-eq-funds-non-eif'
            + '&assetType=mutual-fund&assetType=non-public-stock'
            + '&assetType=indices&assetType=other-investment-fund'
            + '&assetType=other-securities&assetType=ownership-interest'
            + '&assetType=preferred-shares&assetType=private-equity-fund'
            + '&assetType=stock&assetType=stock-options')

html = ''
for x in range(1, 41):
    # Navigate to the URL
    if x == 1:
        driver.get(f'{base_url}')
    else:
        driver.get(f'{base_url}&page={x}')
    
    # Optional: Wait for dynamic content to load
    time.sleep(5)
    
    # Get page source
    html += driver.page_source
    
    # Print progress
    print(f'Page {x} processed.')

# Close the browser
driver.quit()

# Save the HTML content to a file
today_str = datetime.today().strftime('%Y-%m-%d')
with open(f'{today_str}_html.txt', 'w') as outfile:
    outfile.write(html)
