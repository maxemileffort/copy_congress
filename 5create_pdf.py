import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import glob, os, time, sys
from fpdf import FPDF
from datetime import datetime
from PIL import Image

def load_and_convert_image(image_path):
    """Load an image and convert it to RGB."""
    img = Image.open(image_path)
    return img.convert('RGB')

def setup_driver():
    """Sets up headless Chrome WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to process each image
def process_image(image_path):
    trade = 'trade_date' in image_path
    pub = 'pub_date' in image_path
    return image_path, trade, pub

def convert_html_to_png(html_file, output_file):
    """Converts a single HTML file to PNG."""
    driver = setup_driver()
    try:
        driver.get(f"file:///{html_file}")
        time.sleep(5)  # Adjust as needed for page load times
        driver.save_screenshot(output_file)
    except:
        pass
    os.remove(html_file)
    driver.quit()

def main(html_files):
    """Converts a list of HTML files to PNG images using concurrent processing."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for html_file in html_files:
            html_file = os.path.join(os.getcwd(), html_file)
            
            output_file = html_file.replace('.html', '.png')
            output_file = output_file.replace('html', 'imgs')
            print(output_file)
            if os.path.isfile(output_file):
                continue
            futures.append(executor.submit(convert_html_to_png, html_file, output_file))
        
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error during conversion: {e}")

def create_page(pdf, image_path):
    fn_without_extension = os.path.splitext(os.path.basename(image_path))[0]
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)  # Set font: Arial, bold, 12pt
    pdf.cell(0, 10, fn_without_extension, 0, 1, 'C')  # Label the chart
    pdf.image(image_path, w=190, y=30)

if __name__ == "__main__":

    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    html_files = sorted(glob.glob(f'html/*.html'))
    main(html_files)

    today_str = datetime.today().strftime('%Y-%m-%d')

    imagelist = sorted(glob.glob(f'imgs/*.png'))

    pdf1 = FPDF()
    pdf2 = FPDF()
    # Use ThreadPoolExecutor to process images in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_image, image_path) for image_path in imagelist]
        
        for future in concurrent.futures.as_completed(futures):
            try:
                image_path, is_trade_date, is_pub_date = future.result()
                fn_without_extension = os.path.splitext(os.path.basename(image_path))[0]
                if is_trade_date:
                    pdf1.add_page()
                    pdf1.set_font('Arial', 'B', 12)  # Set font: Arial, bold, 12pt
                    pdf1.cell(0, 10, fn_without_extension, 0, 1, 'C')  # Label the chart
                    pdf1.image(image_path, w=190, y=30)
                elif is_pub_date:
                    pdf2.add_page()
                    pdf2.set_font('Arial', 'B', 12)  # Set font: Arial, bold, 12pt
                    pdf2.cell(0, 10, fn_without_extension, 0, 1, 'C')  # Label the chart
                    pdf2.image(image_path, w=190, y=30)
                os.remove(image_path)  # Remove the processed image
            except Exception as e:
                print(f"Error processing image: {e}")

    file_name = f"{today_str}_insider_trading_copying (trade dates).pdf"
    file_name2 = f"{today_str}_insider_trading_copying (publish dates).pdf"
    
    pdf1.output(file_name, "F")
    pdf2.output(file_name2, "F")

    old_html_files = glob.glob('hmtl/*.html')
    for f in old_html_files:
        os.remove(f)

    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print('start_time: ',start_time)
    print('end_time: ',end_time)