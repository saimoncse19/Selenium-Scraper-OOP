"""
  Author: Saimon
  Date: 06 October, 2021

"""
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By


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

    def __init__(self, zip_code, radius, start_url):
        self.zip_code = zip_code
        self.radius = radius
        self.all_cars_list = []
        self.driver = self.start_driver()
        self.start_url = start_url

    # this is initialize the driver
    @staticmethod
    def start_driver():
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
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
            print(f'The desired element: {element} not found.')

    # Start from this URL
    def get_url(self, url):
        self.driver.get(url)

    def start_crawler(self):
        self.get_url(self.start_url)
        # Explicit wait until DOM is ready
        WebDriverWait(self.driver, 30).until(lambda _:
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
            radius_input_field = self.driver.find_element_by_css_selector(self.radius_selector)
            self.wait(radius_input_field, 30)

            # add radius to the url and reload
            self.get_url(self.driver.current_url.replace("radius=75", f"radius={self.radius}"))
        except Exception as err:
            print(f" Error: {err}")






