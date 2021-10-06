"""
  Author: Saimon
  Date: 06 October, 2021

"""

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


class CarCrawler:

    output_file_name = "output/vehicle_data.xlsx"
    car_name_selector = "div.vdp-group section.vin-overview h1"
    car_price_selector = "div.price-summary span[data-test='vdp-price-row']"
    car_vin_selector = "div.vdp-group section.vin-overview span.mr-1"
    car_summary_selector = "section.vehicle-summary div"
    car_features_selector = "section.features-and-specs div li"
    zip_code_selector = "input[name='zip']"
    radius_selector = "input[id='search-radius-range-min']"

    def __init__(self, zip_code, radius):
        self.zip_code = zip_code
        self.radius = radius
        self.all_cars_list = []
        self.driver = self.start_driver()

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






