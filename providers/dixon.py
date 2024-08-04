from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import logging
import re
from providers.base_provider import BaseProvider
import time
import hashlib
from dotenv import load_dotenv
import os

load_dotenv()


# Set the path to your chromedriver
chromedriver_path = os.environ['CHROMEDRIVER']

# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize ChromeDriver with headless mode
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

class Dixon(BaseProvider):

    def extract_total_pages(self, result_text_div):
        pages = 1

        if result_text_div:
            result_text = result_text_div.get_text(strip=True)
            
            # Use a regular expression to find the number in the text
            match = re.search(r"Se encontraron (\d+) inmuebles", result_text)
            if match:
                number_of_properties = int(match.group(1))
                pages = -(- number_of_properties // 6)
                logging.info(f"Number of properties found: {number_of_properties}")
            else:
                logging.info(f"No match found for the pattern.")
        else:
            logging.error(f"No div with class 'result-text' found.")
        return pages
    
    def get_string_from_url(self, url):
        
        match = re.search(r'prop\.php\?([^\s]+)', url)
        if match:
            return match.group(1)
        else:
            raise ValueError('String not found in the URL response.')
        
    def string_to_numeric_value(self, s):

        # Create a SHA-256 hash of the input string
        sha256_hash = hashlib.sha256(s.encode()).hexdigest()
        
        # Convert the hexadecimal hash to an integer
        numeric_value = int(sha256_hash, 16)
        
        return numeric_value

    def scale_to_range(self, value, min_range, max_range):
        # Scale the value to the desired range
        return min_range + (value % (max_range - min_range + 1))
    
    def calculate_internal_id(self, property_link):
        # Extract the string from the URL
        extracted_string = self.get_string_from_url(property_link)

        # Convert the extracted string to a numeric value
        numeric_value = self.string_to_numeric_value(extracted_string)

        return self.scale_to_range(numeric_value, 1, 99999999)
    
    def scrape_page(self):

        title = ''
        href = ''
        processed_props = []
        content = BeautifulSoup(driver.page_source, 'html.parser')

        if self.current_page == 1:
            # Find the div element with class 'result-text'
            result_text_div = content.find('div', class_='result-text')
            self.total_pages = self.extract_total_pages(result_text_div)
        
        logging.info(f"Current Page: {self.current_page}. Total Pages: {self.total_pages}") 

        # Locate the form element by its ID
        form_element = content.find('form', id='frmSearch')

        # Find all divs with class 'row' within the form
        properties = form_element.find_all('div', class_='row')

        # Iterate and print each row
        for prop in properties:
            row_photo_div = prop.find('div', class_='row-photo')
            
            if row_photo_div is not None:
                # Find all <a> elements within the row_photo_div
                a_elements = row_photo_div.find_all('a')
                if a_elements:
                    # Extract and print the href attribute for each <a> element
                    property_link = a_elements[0].get('href')
                    if property_link:
                        pass
                    else:
                        logging.info(f"No href attribute found for this <a> element.")

            internal_id = self.calculate_internal_id(property_link)
            

            if internal_id in self.processed_ids:
                return
            else:
                self.processed_ids.append(internal_id)

            row_tit1_elements = prop.find_all(class_='row-tit1')

            if row_tit1_elements is not None:
                # Extract and print the text for each element with class 'row-tit1'
                for element in row_tit1_elements:
                    title = element.get_text(strip=True)
            else:
                logging.info(f"No elements with class 'row-tit1' found.")

            processed_props.append({
                'title': title, #title, 
                'url': property_link,
                'internal_id': internal_id,
                'provider': self.provider_name
            })
        
        return processed_props

        # Perform your scraping logic here
        # print(soup.prettify())  # Example print, replace with actual scraping code
    
    def props_in_source(self, source):
        page_link = self.provider_data['base_url'] + source
        self.current_page = 1
        self.total_pages = 1
        page = 1
        self.processed_ids = []

        driver.get(page_link)

        while self.current_page <= self.total_pages:
            try:
                # Capture the initial page source
                initial_page_source = driver.page_source

                # Wait for the div with class result-text to be present and visible
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div.result-text"))
                )
                
                # Scrape the current page
                processed_props = self.scrape_page()
                
                # Yield each property found on the current page
                for obj in processed_props:
                    yield obj
                
                # Wait for the next page button to be clickable
                next_page = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'javascript:chgPage') and contains(text(), '>')]"))
                )
                
                # Click the next page button
                next_page.click()
                
                # Wait for the page to be fully loaded after clicking
                WebDriverWait(driver, 10).until(
                    EC.staleness_of(next_page)
                )
                
                # Capture the new page source and compare it
                new_page_source = driver.page_source

                if initial_page_source == new_page_source:
                    logging.info("Page source has not changed. Stopping scraping.")
                    break
                
                # Increment the page count
                self.current_page += 1

            except Exception as e:
                logging.error(f"Exception happened: {e}")
                break
