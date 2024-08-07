import logging
import cloudscraper
from abc import ABC, abstractmethod
from lib.hostname_ignoring_adapter import HostNameIgnoringAdapter
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import yaml
import certifi
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
from dotenv import load_dotenv


# configuration    
with open("configuration.yml", 'r') as ymlfile:
    print('loading config')
    cfg = yaml.safe_load(ymlfile)

disable_ssl = False
load_dotenv()

logging.getLogger('WDM').setLevel(logging.WARNING)

if 'disable_ssl' in cfg:
    disable_ssl = cfg['disable_ssl']

class BaseProvider(ABC):
    def __init__(self, provider_name, provider_data):
        self.provider_name = provider_name
        self.provider_data = provider_data

        self.__scraper = cloudscraper.create_scraper()
        if disable_ssl:
            self.__scraper.mount('https://', self.get_adapter_from_strategy())

        # Set path to ChromeDriver
        chrome_service = ChromeService(executable_path="/opt/chromedriver/chromedriver-linux64/chromedriver")

        # Set up driver
        self.driver = webdriver.Chrome(service=chrome_service, options=self.set_chrome_options())
        
    
    def set_chrome_options(self) -> Options:
        """Sets chrome options for Selenium.
        Chrome options for headless browser is enabled.
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")  # This is important for some versions of Chrome
        chrome_options.add_argument("--remote-debugging-port=9222")  # This is recommended

        # Set path to Chrome binary
        chrome_options.binary_location = "/opt/chrome/chrome-linux64/chrome"
        return chrome_options


    @abstractmethod
    def props_in_source(self, source):
        pass

    def request(self, url):
        return self.__scraper.get(url, verify=certifi.where())

    def next_prop(self):
        for source in self.provider_data:
            yield from self.props_in_source(source)
    
    def get_adapter_from_strategy():
        
        retry_strategy = Retry(
            total=5,  
            status_forcelist=[429, 500, 502, 503, 504],  
            method_whitelist=["HEAD", "GET", "OPTIONS"],  
            backoff_factor=1 
        )

        return HTTPAdapter(max_retries=retry_strategy)