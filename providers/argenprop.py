from bs4 import BeautifulSoup
import logging
import re
from providers.base_provider import BaseProvider

class Argenprop(BaseProvider):
    def props_in_source(self, source):
        page_link = self.provider_data['base_url'] + source
        page = 1
        processed_ids = []

        while(True):
            logging.info(f"Requesting {page_link}")
            page_response = self.request(page_link)

            if page_response.status_code != 200:
                break
            
            page_content = BeautifulSoup(page_response.content, 'lxml')

            properties = page_content.find_all('div', class_='listing__item')

            if len(properties) == 0:
                break

            for prop in properties:
                # if data-id was already processed we exit
                internal_id = prop.get('id')

                if internal_id in processed_ids:
                    return
                else:
                    processed_ids.append(internal_id)
                
                title = prop.find('h2', class_='card__title').get_text().strip()
                price_section = prop.find('p', class_='card__price')
                if price_section is not None:
                    title = title + ' ' + price_section.get_text().strip()
                href = prop.find('a', class_='card')['href']
                    
                yield {
                    'title': title, 
                    'url': self.provider_data['base_url'] + href,
                    'internal_id': internal_id,
                    'provider': self.provider_name
                    }

            page += 1
            page_link = self.provider_data['base_url'] + source + f"-pagina-{page}"
