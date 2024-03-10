import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import glob, os, time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def load_and_convert_image(image_path):
    """Load an image, convert it to RGB, and add a watermark in the bottom right corner."""
    watermark = os.path.splitext(os.path.basename(image_path))[0]
    with Image.open(image_path) as img:

        # Get the width and height of the image
        img_width, img_height = img.size

        # Preparing the text watermark (Change the color in the last parameter below)
        txt = Image.new("RGBA", img.size, (100, 100, 100, 0))
    
        # Create a drawing context
        draw = ImageDraw.Draw(txt)

        # Specify the font and size for the watermark
        # You might need to adjust the path to a font file and font size depending on your setup
        font = ImageFont.truetype("arial.ttf", 14)
        
        # Get the width and height of the text
        _, _, w, h = draw.textbbox((0, 0), watermark, font=font)

        # Position for the watermark (bottom right corner with a small margin)
        x = img_width - w - 10
        y = img_height - h - 10
        
        # Make the text written into center
        draw.text((x, y), 
                  watermark, 
                  font=font, 
                  fill=(100, 100, 100, 255))
    
        # Combine the image with text watermark
        out = Image.alpha_composite(img, txt)
        
    return out

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
        time.sleep(1)  # Adjust as needed for page load times
        driver.save_screenshot(output_file)
    except:
        pass
    os.remove(html_file)
    driver.quit()

def handle_html_files(html_files):
    """Converts a list of HTML files to PNG images using concurrent processing."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for html_file in html_files:
            html_file = os.path.join(os.getcwd(), html_file)
            
            output_file = html_file.replace('.html', '.png')
            output_file = output_file.replace('html', 'imgs')
            if os.path.isfile(output_file):
                continue
            futures.append(executor.submit(convert_html_to_png, html_file, output_file))
        
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error during conversion: {e}")

def handle_png_files(image_dir, output_pdf, flag):
    # Get the list of image paths
    image_paths = [os.path.join(image_dir, img) for img in os.listdir(image_dir) if img.endswith(('png', 'jpg', 'jpeg'))]
    specific_paths = [f for f in image_paths if flag in f]

    with ThreadPoolExecutor() as executor:
        images_converted = list(executor.map(load_and_convert_image, specific_paths))

    # Save the first image, appending the rest
    images_converted[0].save(output_pdf, save_all=True, append_images=images_converted[1:])

if __name__ == "__main__":

    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    html_files = sorted(glob.glob(f'html/*.html'))
    handle_html_files(html_files)

    today_str = datetime.today().strftime('%Y-%m-%d')

    file_name = f"{today_str}_insider_trading_copying (trade dates).pdf"
    file_name2 = f"{today_str}_insider_trading_copying (publish dates).pdf"

    img_dir = os.path.join(os.getcwd(), 'imgs')
    handle_png_files(img_dir, file_name, 'trade_dates')
    handle_png_files(img_dir, file_name2, 'pub_dates')

    old_html_files = glob.glob('html/*.html')
    for f in old_html_files:
        os.remove(f)

    old_png_files = glob.glob('imgs/*.png')
    for f in old_png_files:
        os.remove(f)

    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print('start_time: ',start_time)
    print('end_time: ',end_time)