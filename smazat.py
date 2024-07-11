import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class BaseScraper:
    def __init__(self, driver_path=None):
        self.driver = None
        try:
            if driver_path:
                self.driver = webdriver.Chrome(service=Service(driver_path))
            else:
                self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        except Exception as e:
            logging.error(f"Error initializing WebDriver: {e}")
            self.driver = None

    def get_driver(self):
        return self.driver

class AdminScraper(BaseScraper):
    def __init__(self, driver_path=None):
        super().__init__(driver_path)
        # Další inicializace specifická pro AdminScraper

    def some_admin_function(self, url):
        driver = self.get_driver()
        if driver:
            driver.get(url)
            # Další logika
        else:
            print("WebDriver nebyl správně inicializován.")

class FrontScraper(BaseScraper):
    def __init__(self, driver_path=None):
        super().__init__(driver_path)
        # Další inicializace specifická pro FrontScraper

    def scrap_description(self, url, selector):
        driver = self.get_driver()
        if driver:
            driver.get(url)
            # Další logika pro scrapování podle selectoru
            # Například:
            try:
                element = driver.find_element_by_css_selector(selector)
                return element.text
            except Exception as e:
                logging.error(f"Error scraping description: {e}")
                return None
        else:
            print("WebDriver nebyl správně inicializován.")

# Příklad použití ve skriptu jednorazovy.py
if __name__ == "__main__":
    url_fragment_1 = "https://www.travelasap.cz/a/354"
    scraper = FrontScraper()

    try:
        description = scraper.scrap_description(url_fragment_1+"#tab-recenze-hotelu", "#tab-recenze-hotelu > div > div.local-rating")
        if description:
            print(description)
        else:
            print("Scraping description failed.")
    except Exception as e:
        print(f"Error: {e}")
