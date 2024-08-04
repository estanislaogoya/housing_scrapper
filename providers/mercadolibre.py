from bs4 import BeautifulSoup
import logging
import re
from providers.base_provider import BaseProvider

class Mercadolibre(BaseProvider):
    def props_in_source(self, source):
        page_link = self.provider_data['base_url'] + source + '_NoIndex_True'
        from_ = 1
        regex = r"(MLA-\d*)"

        while(True):
            logging.info(f"Requesting {page_link}")
            page_response = self.request(page_link)

            if page_response.status_code != 200:
                break
            
            page_content = BeautifulSoup(page_response.content, 'lxml')
            properties = page_content.find_all('li', class_='ui-search-layout__item')

            if len(properties) == 0:
                break

            logging.info(f"Properties: {len(properties)}")

            for prop in properties:
                # section = prop.find('a', class_='ui-search-result__link')

                section = prop.find('div', class_='ui-search-result__content')

                if section is None:
                    logging.warning("Section not found in property.")
                    continue

                content = section.find('a', class_='ui-search-link__title-card')

                if content and 'href' in content.attrs:
                    link = content['href']
                    logging.info(f"Extracted link")
                else:
                    logging.info("Link not found")
                    continue

                matches = re.search(regex, link)
                internal_id = matches.group(1).replace('-', '')

                price_section_currency = section.find('span', class_='andes-money-amount__currency-symbol')
                price_section_value = section.find('span', class_='andes-money-amount__fraction')

                if price_section_currency and price_section_value:
                    price = price_section_currency.get_text().strip() + ' ' + price_section_value.get_text().strip()
                else:
                    price = ''

                # title_section = section.find('div', class_='ui-search-item__group--title')
                
                title = section.find('h2', class_='ui-search-item__title')
                
                if title is not None:
                    title = title.get_text().strip() + ' ' + price
                else:
                    logging.warning("Title not found.")
                    title = 'No title'

                yield {
                    'title': title, 
                    'url': link,
                    'internal_id': internal_id,
                    'provider': self.provider_name
                    }

            from_ += 50
            page_link = self.provider_data['base_url'] + source + f"_Desde_{from_}_NoIndex_True"
    