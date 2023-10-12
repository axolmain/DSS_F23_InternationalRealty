# basics
# other
import os
import re
import time
from datetime import date
from time import sleep

import geckodriver_autoinstaller
from fpdf import FPDF
from selenium import webdriver
# search tools
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

WAIT_TIME = 5  # seconds

SCREENSHOTS_DIR = 'screenshots/'

# find downloads folder
if os.name == "nt":
    DOWNLOADS_DIR = f"{os.getenv('USERPROFILE')}\\Downloads"
else:
    DOWNLOADS_DIR = f"{os.getenv('HOME')}/Downloads"

IMAGE_HEIGHT = 5
IMAGE_WIDTH = 7.5


class Scraper:

    def __init__(self, street, city, state, zip_code, country, price):

        self.driver = None
        self.street = street.strip().upper()
        self.city = city.strip().upper()
        self.state = state.strip().upper()
        self.zip_code = str(zip_code).strip().upper()
        self.country = country.strip().upper()
        self.address = self.get_full_address()
        self.price = price
        self.urls = {}

    def get_full_address(self):

        return f"{self.street} {self.city}, {self.state}, {self.zip_code} {self.country}"

    def start_webdriver(self):

        # Configure options (if any)
        options = FirefoxOptions()
        options.profile = webdriver.FirefoxProfile()
        # options.add_argument('--headless')  # Uncomment if you want to run Firefox headlessly

        # Ensure GeckoDriver is installed and get the path
        gecko_driver_path = GeckoDriverManager().install()

        # Configure WebDriver service
        # service = FirefoxService(executable_path=gecko_driver_path)
        # service.log_path = "geckodriver.log"  # Specify the log path

        # Start WebDriver
        self.driver = webdriver.Firefox(
            options=options
        )

    def get_urls(self):

        url_methods = [method for method in dir(Scraper) if re.search(r"get_.+_urls", method)]
        for method in url_methods:
            # get platform name
            platform = method[len('get_'):-len('_urls')] \
                .title() \
                .replace('_', ' ')

            # call method
            try:
                self.__getattribute__(method)()
                print(f"✓ - {platform}")
            except:
                print(f"X - {platform}")

    def get_screenshots(self):

        # create screenshots folder
        if not os.path.exists(SCREENSHOTS_DIR):
            os.mkdir(SCREENSHOTS_DIR)

        # create save folder
        base_path = SCREENSHOTS_DIR + self.address
        if not os.path.exists(base_path):
            os.mkdir(base_path)

        # resize window
        self.driver.set_window_size(1200, 800)

        # loop through available urls
        for site_name, url in self.urls.items():
            self.driver.get(url)
            sleep(3)
            self.driver.save_screenshot(f"{base_path}/{site_name}.png")

    def create_report(self):

        # create blank PDF
        pdf = FPDF(
            orientation='Landscape',
            unit='in',
            format='Letter'
        )

        # add screenshots to PDF
        for file_name in os.listdir(SCREENSHOTS_DIR + self.address):
            # new page
            pdf.add_page()
            pdf.set_margins(0, 0, 0)

            # header
            pdf.set_x(11 / 2)
            pdf.set_y(1.25)
            pdf.set_font('Helvetica', '', 40)
            pdf.cell(
                txt=file_name[:-len('.png')],
                w=11,
                align='C',  # center
            )

            # date
            pdf.set_x(11 / 2)
            pdf.set_y(1.75)
            pdf.set_font('Helvetica', '', 25)
            pdf.cell(
                txt=date.today().strftime("%B %d, %Y"),
                w=11,
                align='C',  # center
            )

            # screenshot
            pdf.image(
                f"{SCREENSHOTS_DIR}{self.address}/{file_name}",
                h=IMAGE_HEIGHT,
                w=IMAGE_WIDTH,
                x=(11 - IMAGE_WIDTH) / 2,
                y=(8.5 - IMAGE_HEIGHT) / 2 + 0.75
            )

        # save PDF report
        pdf.output(f"{DOWNLOADS_DIR}/{self.address}.pdf")

    def get_sothebys_urls(self):

        # load page
        url = 'https://www.sothebysrealty.com/eng'
        self.driver.get(url)

        # search address
        search_bar_xpath = "/html/body/div/div/div/main/section[1]/div/div/div[2]/div/div/div[2]/div[2]/div[1]/input"
        search_bar = WebDriverWait(self.driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.XPATH, search_bar_xpath))
        )
        search_bar.send_keys(self.address + Keys.ENTER)

        # get property ID
        id_xpath = "/html/body/div[1]/div/div/main/div[1]/section[4]/div/div[1]/ul/li[1]/ul/li[1]/div[2]"
        id = WebDriverWait(self.driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.XPATH, id_xpath))
        ).text

        # save listing urls
        self.urls.update({
            'Sotheby\'s International Realty': f"https://www.sothebysrealty.com/id/{id}",
            'Golden Gate\nSotheby\'s International Realty': f"https://www.goldengatesir.com/id/{id}",
            'James Edition': f"https://www.jamesedition.com/ref/{id}",
            'Juwai': f"https://www.juwai.com/find-listing-by-source?source=Sothebys&source_id={id}",
            # 'Real-Buzz': f"http://www.real-buzz.com/RealEstate-detail-SIR/{id}", # Website no longer exists
            'Country Life': f"http://www.countrylife.co.uk/international-property/{id}"
        })

    def get_mansion_global_urls(self):

        # load page
        url = f'https://www.mansionglobal.com/'
        self.driver.get(url)

        # search address
        search_bar_css = "input.MGTheme--whitney--3m76N7fd.typography--sans-serif--2NTOffNS"
        search_bar = WebDriverWait(self.driver, WAIT_TIME).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, search_bar_css))
        )
        search_bar.send_keys(self.address)

        # click top result
        result_xpath = "/html/body/div[1]/div/div/div/header/div[2]/div[2]/div/form/div/div/div/div[1]/div/div[3]/div/div/div/div/div/div/div/button"
        WebDriverWait(self.driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.XPATH, result_xpath))
        ).click()

        # load listing
        WebDriverWait(self.driver, WAIT_TIME).until(
            EC.url_changes(url)
        )

        # extract id from listing url
        listing_url = self.driver.current_url
        id = listing_url.split('/')[-1]

        # save listing urls
        self.urls.update({
            "Mansion Global": f"https://www.mansionglobal.com/listings/{id}",
            "Wall Street Journal": f"https://realestate.wsj.com/listings/{id}",
            "Market Watch": f"https://www.marketwatch.com/personal-finance/real-estate/listings/{id}",
            "Barrons": f"https://www.barrons.com/real-estate/listings/{id}"
        })

    def get_properstar_urls(self):

        # load page
        url = 'https://www.properstar.com/buy'
        self.driver.get(url)


        # press search button
        search_button_xpath = "/html/body/main/div[1]/div[2]/div[1]/section[1]/div[2]/section/button"
        search_button_class_name = "autocomplete-cta-button autocomplete-hero-cta btn btn-secondary btn-white btn-lg"
        search_button = WebDriverWait(self.driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.XPATH, search_button_xpath))
        )
        search_button.click()

        time.sleep(2)

        # search address
        search_input_xpath = "/html/body/div[5]/div/div/div/div/div[2]/div[2]/input"
        search_bar = WebDriverWait(self.driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.XPATH, search_input_xpath))
        )
        search_bar.send_keys(self.address)

        # get first item
        first_item_id = "downshift-0-item-0"
        first_item_xpath = "/html/body/div[5]/div/div/div/div/div[2]/div[3]/div/ul/li[1]"

        first_item_btn = WebDriverWait(self.driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.XPATH, first_item_xpath))
        )
        first_item_btn.click()

        time.sleep(2)

        # # Find listing from search results
        # listing = re.findall("[^,]*", self.address)
        # find_listing = WebDriverWait(self.driver, 10).until(
        #     EC.presence_of_element_located((By.XPATH, f"//a[contains(text(), '{listing[0]}')]"))
        # )
        # find_listing.click()

        # click first listing
        listing_xpath = "/html/body/main/div[1]/div[3]/div/div[2]/div/div[1]/div/div[2]/article[1]/div/div[1]/div[1]/div/div/div/div/div[1]/a"
        listing_url = WebDriverWait(self.driver, WAIT_TIME * 3).until(
            EC.presence_of_element_located((By.XPATH, listing_xpath))
        ).get_attribute('href')

        # extract id from listing url
        id = listing_url.split('/')[-1]

        # save listing urls
        self.urls.update({
            "Proper Star": f"https://www.properstar.com/listing/{id}",
            "99 Acres": f"https://international.99acres.com/listing/{id}"
        })

    # def get_landwatch_urls(self):

    #     url = "https://www.landwatch.com/"
    #     self.driver.get(url)

    #     search_bar_xpath = "/html/body/div/div[2]/div/section[1]/section/div/div/div/div/div/div/div/div[1]/div/div/input"
    #     search_bar = WebDriverWait(self.driver, WAIT_TIME).until(
    #         EC.presence_of_element_located((By.XPATH, search_bar_xpath))
    #     )
    #     search_bar.send_keys(f"{self.city}, {self.state}" + Keys.ENTER)

    #     # grabs listings
    #     linkaddy = WebDriverWait(self.driver, WAIT_TIME).until(
    #         EC.presence_of_all_elements_located((By.CLASS_NAME, '_61961'))
    #     )

    #     # main loop for searching a page for an address
    #     for element in linkaddy:

    #         # grabs and manipulates listing to be compared to the search value
    #         addy = element.find_element(By.CLASS_NAME, 'df867').text
    #         addy = addy.splitlines()
    #         new_ad = ''
    #         for i in range(len(addy)):
    #             new_ad += addy[i]

    #         # if address is found grab the link to the page
    #         if new_ad == self.address:
    #             link = element.find_element(By.TAG_NAME, 'a').get_attribute('href')
    #             print(link)
    #             element_found = True
    #             return

    #     # begins recurssion loop if address is not found on page
    #     if element_found == False:

    #         # how to grab the next url if its the first page
    #         if iterator == 1:
    #             iterator+=1
    #             element = self.driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div[3]/div/div[2]/div[4]/a')
    #             link = element.get_attribute('href')
    #             page_scraper(search_ad, link, iterator)

    #         # how to grab the next page if its not the first page
    #         else:
    #             element = self.driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div[3]/div/div[2]/div[3]/a[2]')
    #             link = element.get_attribute('href')
    #             page_scraper(search_ad, link, iterator)
