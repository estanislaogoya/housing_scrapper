#import requests
from bs4 import BeautifulSoup
import logging
from providers.base_provider import BaseProvider

class Zonaprop(BaseProvider):
    
    def __init__(self, provider_data, provider_name):
        super().__init__(provider_data, provider_name)
        self.logger = logging.getLogger(__name__)

    def props_in_source(self, source):
        page_link = source['base_url'] + source['url']
        page = 1
        processed_ids = []

        while(True):
            #self.logger.info(f"Requesting {page_link}")
            page_response = self.request(page_link)
            
            if page_response.status_code != 200:
                break
            
            page_content = BeautifulSoup(page_response.content, 'lxml')
            properties = page_content.find_all('div', {'data-posting-type': 'PROPERTY'})

            for prop in properties:
                # if data-id was already processed we exit
                if prop['data-id'] in processed_ids:
                    return
                
                processed_ids.append(prop['data-id'])

                description_h3 = prop.find('h3', {'data-qa': 'POSTING_CARD_DESCRIPTION'})
                
                if description_h3:
                    a_tag = description_h3.find('a')
                    if a_tag:
                        title = a_tag.text.strip()
                    else:
                        title = "NOT FOUND"

                price_section = prop.find('div', {'data-qa': 'POSTING_CARD_PRICE'})

                if price_section is not None:
                    title = title + ' ' + price_section.text.strip()
                    
                yield {
                    'title': source['base_url'] + prop['data-to-posting'], #title, 
                    'url': source['base_url'] + prop['data-to-posting'],
                    'internal_id': prop['data-id'],
                    'provider': self.provider_name
                    }
                
                # print({
                #     'title': title, 
                #     'url': self.provider_data['base_url'] + prop['data-to-posting'],
                #     'internal_id': prop['data-id'],
                #     'provider': self.provider_name
                #     })
                
            if page > 3:
                break
            page += 1
            page_link = source['base_url'] + source['url'].replace(".html", f"-pagina-{page}.html")
        
        self.driver.quit()
    