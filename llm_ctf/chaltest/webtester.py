import argparse
import os
from selenium import webdriver
import logging
from pathlib import Path

def get_webdriver(log_output : str = None):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    # Ignore certificate errors
    # Disabled by BDG; we want to catch these!
    # options.add_argument('--ignore-certificate-errors')
    # Set screen size
    options.add_argument('window-size=1280,1024')
    logging.info(f"Using Chrome options: {options.arguments}")
    # Enable logging
    if log_output:
        service_args = ['--verbose']
        service = webdriver.chrome.service.Service(service_args=service_args, log_output=log_output)
        logging.info(f'Logging to with {service_args} to {log_output.name}')
        driver = webdriver.Chrome(options=options, service=service)
    else:
        driver = webdriver.Chrome(options=options)
    return driver

def take_screenshot(url, filename, log_filename):
    with open(log_filename, 'w+b') as logf:
        try:
            driver = get_webdriver(logf)
            # 30 second timeout
            driver.set_page_load_timeout(30)
            driver.get(url)
            ret = True
        except Exception as e:
            logging.info(f"Error occurred: {e}")
            ret = False
        finally:
            # Try to save a screenshot anyway, just in case the page just has
            # dynamic content that takes a while to load
            try:
                driver.save_screenshot(filename)
                driver.quit()
            except Exception as e:
                logging.info(f"Error occurred: {e}")
                ret = False
    return ret

def main():
    parser = argparse.ArgumentParser(description='Take a screenshot of a webpage')
    parser.add_argument('url', help='URL to take a screenshot of')
    parser.add_argument('name_prefix', help='Prefix for the screenshot and logs')
    args = parser.parse_args()
    output_dir = Path('output').resolve()
    output_dir.mkdir(exist_ok=True)
    filename = str(output_dir/f"{args.name_prefix}.png")
    chrome_log = str(output_dir/f"{args.name_prefix}.chrome.log")
    logfile = str(output_dir/f"{args.name_prefix}.screenshot.log")
    print(output_dir)

    # Configure logging
    logging.basicConfig(filename=logfile, level=logging.INFO, format='%(asctime)s | %(message)s')

    if take_screenshot(args.url, filename, chrome_log):
        logging.info(f"Screenshot and logs saved to saved to {output_dir}")
        # print(f"Screenshot and logs saved to saved to {output_dir}")
        return 0
    else:
        logging.info(f"Error occurred, see {chrome_log} for details")
        # print(f"Error occurred, see {chrome_log} for details")
        return 1

if __name__ == '__main__':
    exit(main())
