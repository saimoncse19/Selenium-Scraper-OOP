"""
  Author: Saimon
  Date: 06 October, 2021

"""
import time
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import pandas as pd
import logging

# basic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
logger.setLevel(logging.INFO)


class CarCrawler:

    # output destination and css-selectors for required fields
    output_file_name = "output/vehicle_data.xlsx"
    car_name_selector = "div.vdp-group section.vin-overview h1"
    car_price_selector = "div.price-summary span[data-test='vdp-price-row']"
    car_vin_selector = "div.vdp-group section.vin-overview span.mr-1"
    car_summary_selector = "section.vehicle-summary div"
    car_features_selector = "section.features-and-specs div li"
    zip_code_selector = "input[name='zip']"
    radius_selector = "input[id='search-radius-range-min']"

    def __init__(self, _zip, _radius, _start_url):
        self.zip_code = _zip
        self.radius = _radius
        self.all_cars_list = []
        self.driver = self.start_driver()
        self.start_url = _start_url

    # this is initialize the driver
    @staticmethod
    def start_driver():
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        return driver

    # Close the browser/driver
    def quit_driver(self):
        self.driver.quit()

    # this will wait to mimic human behavior
    def wait(self, element, wait):
        try:
            wait = WebDriverWait(self.driver, wait)
            wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, element)))
        except:
            logger.info(f'{element} not found')

    # Start from this URL
    def get_url(self, url):
        self.driver.get(url)

    def start_crawler(self):
        logger.info(f'Crawler Started.....')
        self.get_url(self.start_url)
        # Explicit wait until DOM is ready
        WebDriverWait(self.driver, 30).until(lambda driver:
                                             self.driver.execute_script('return document.readyState') == 'complete')
        time.sleep(2)

        try:
            zip_code_input_field = self.driver.find_element_by_css_selector(self.zip_code_selector)
            radius_input_field = self.driver.find_element_by_css_selector(self.radius_selector)

            # clear the zip code input field
            for count in range(0, 5):
                self.wait(zip_code_input_field, 30)
                zip_code_input_field.send_keys(Keys.BACKSPACE)

            # fill the input field
            zip_code_input_field.send_keys(self.zip_code)

            radius_input_field.click()

            # wait until page is reloaded
            time.sleep(2)
            self.wait(radius_input_field, 30)

            # add radius to the url and reload
            self.get_url(self.driver.current_url.replace("radius=75", f"radius={self.radius}"))

            # get all car details
            self.get_car_listings()
            # Export
            self.to_xlsx()
        except Exception as err:
            logger.info(err)

    # get all the necessary car details
    def get_car_details(self):
        car_name_element = self.driver.find_element_by_css_selector(self.car_name_selector)
        car_name = car_name_element.text if car_name_element else ''
        car_price_element = self.driver.find_element_by_css_selector(self.car_price_selector)
        car_price = car_price_element.text if car_price_element else ''
        car_vin_element = self.driver.find_element_by_css_selector(self.car_vin_selector)
        car_vin = car_vin_element.text if car_vin_element else ''
        car_summary_element = self.driver.find_elements_by_css_selector(self.car_summary_selector)
        car_summary = [sum_div.text for sum_div in car_summary_element]
        car_features_element = self.driver.find_elements_by_css_selector(self.car_features_selector)
        car_features = [spec_div.text for spec_div in car_features_element]
        car_details = {
            'NAME': car_name,
            'PRICE': car_price,
            'VIN': car_vin,
            'Vehicle Summary': car_summary,
            'Top Features & Specs': car_features

        }
        self.all_cars_list.append(car_details)

    # Recursively traverse all pages and car pages

    def get_car_listings(self):
        car_page_selector = "div.visible-vehicle-info a.usurp-inventory-card-vdp-link"
        self.wait(car_page_selector, 10)
        next_page_selector = "div.srp-pagination a[data-tracking-value='next']"
        next_page_element = self.driver.find_element_by_css_selector(next_page_selector)
        next_page_url = None
        if next_page_element:
            next_page_url = next_page_element.get_attribute('href')

        # get and iterate over all cars (pages) on the current page
        car_pages = self.driver.find_elements_by_css_selector(car_page_selector)
        all_cars_url = [car.get_attribute('href') for car in car_pages]

        # Access individual car page
        for car_url in all_cars_url:
            car_detail_page_url = urljoin(self.driver.current_url, car_url)

            # open the car page and get details
            self.get_url(car_detail_page_url)
            self.get_car_details()

        # terminate recursive call
        if not next_page_url:
            return
        next_page_url = urljoin(self.driver.current_url, next_page_url)

        # call to next page recursively. Please comment the next two lines to only scrape first page
        self.get_url(next_page_url)
        self.get_car_listings()

    # data to XLSX
    def to_xlsx(self):
        df = pd.DataFrame(self.all_cars_list)
        df.to_excel(self.output_file_name)


def ask_radius_slider_option(options):
    print("Please choose Radius:")
    for idx, element in enumerate(options):
        print(f"{idx + 1}) {element}")
    user_input = input("Enter number: ")
    try:
        if int(user_input) in options:
            return int(user_input)
    except Exception as E:
        pass
    ask_radius_slider_option(options)


if __name__ == "__main__":
    zip_code = int(input("Enter Zip Code (must be valid): "))
    radius = ask_radius_slider_option([10, 25, 50, 75, 100, 200, 500])
    crawler_obj = CarCrawler(zip_code, radius, _start_url="https://www.edmunds.com/cars-for-sale-by-owner/")
    crawler_obj.start_crawler()
    crawler_obj.quit_driver()





