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
        
        chromedriver_path = os.environ['CHROMEDRIVER']
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), 
            options=chrome_options
        )
    
    @abstractmethod
    def props_in_source(self, source):
        pass

    def request(self, url):
        return self.__scraper.get(url, verify=certifi.where())

    def next_prop(self):
        for source in self.provider_data['sources']:
        
            yield from self.props_in_source(source)
    
    def get_adapter_from_strategy():
        
        retry_strategy = Retry(
            total=5,  
            status_forcelist=[429, 500, 502, 503, 504],  
            method_whitelist=["HEAD", "GET", "OPTIONS"],  
            backoff_factor=1 
        )

        return HTTPAdapter(max_retries=retry_strategy)