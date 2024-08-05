from bs4 import BeautifulSoup
import logging
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from providers.base_provider import BaseProvider

class Mercadolibre(BaseProvider):

    def __init__(self, provider_data, provider_name):
        super().__init__(provider_data, provider_name)

        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        
        # Initialize Selenium WebDriver with the options
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), 
            options=chrome_options
        )

    def extract_total_pages(self, page_content):
        pages = 1

        results_section = page_content.find('div', class_='ui-search-search-result')

        if results_section:
            span_element = results_section.find('span', class_='ui-search-search-result__quantity-results')

            if span_element:
                span_text = span_element.get_text()

                match = re.search(r'\d+', span_text)

                if match:
                    number_of_properties = int(match.group())
                    pages = -(-number_of_properties // 50)  # Ceiling division
                    logging.info(f"Number of pages: {pages}")
                else:
                    logging.info("No match found for the pattern.")
            else:
                logging.error("No span with class 'ui-search-search-result__quantity-results' found.")
        else:
            logging.error("No div with class 'ui-search-search-result' found.")
        return pages

    def props_in_source(self, source):
        page_link = self.provider_data['base_url'] + source + '_NoIndex_True'
        from_ = 1
        regex = r"(MLA-\d*)"
        page = 1

        while True:
            logging.info(f"Requesting {page_link}")
            self.driver.get(page_link)

            try:
                # Wait for the results section to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'ui-search-search-result'))
                )
            except TimeoutException:
                logging.error("Timeout waiting for the results section to load.")
                break

            page_content = BeautifulSoup(self.driver.page_source, 'lxml')

            properties = page_content.find_all('li', class_='ui-search-layout__item')

            total_pages = self.extract_total_pages(page_content)

            if len(properties) == 0:
                break

            for prop in properties:
                
                section = prop

                if section is None:
                    logging.warning("Section not found in property.")
                    continue

                title_content1 = section.find('a', class_='poly-component__title')
                title_content2 = section.find('a', class_='ui-search-link__title-card')

                if title_content1 and 'href' in title_content1.attrs:
                    link = title_content1['href']
                elif title_content2 and 'href' in title_content2.attrs:
                    link = title_content2['href']
                else:
                    logging.warning("No Link Found")

                matches = re.search(regex, link)
                internal_id = matches.group(1).replace('-', '')

                price_section_currency = section.find('span', class_='andes-money-amount__currency-symbol')
                price_section_value = section.find('span', class_='andes-money-amount__fraction')

                if price_section_currency and price_section_value:
                    price = price_section_currency.get_text().strip() + ' ' + price_section_value.get_text().strip()
                else:
                    price = ''

                title1 = section.find('h2', class_='poly-box')
                title2 = section.find('h2', class_='ui-search-item__title')

                if title1 is not None:
                    title = title1.get_text().strip() + ' ' + price
                elif title2 is not None:
                    title = title2.get_text().strip() + ' ' + price
                else:
                    logging.warning("Title not found.")
                    title = 'No title'

                yield {
                    'title': title,
                    'url': link,
                    'internal_id': internal_id,
                    'provider': self.provider_name
                }

            if page < total_pages:
                page += 1
                from_ += len(properties)
                page_link = self.provider_data['base_url'] + source + f"_Desde_{from_}_NoIndex_True"
            else:
                break

        # Close the Selenium WebDriver
        self.driver.quit()
