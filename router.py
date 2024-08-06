import logging
from utils.db_client import PostgresDbClient
from providers.processor import process_properties
import os
from dotenv import load_dotenv
from sqlalchemy import text
from collections import defaultdict

load_dotenv()

logger = logging.getLogger()

class Router():

    def __init__(self):
        try:
            self.db = PostgresDbClient()
            self.ses = self.db.Session()
            logger.info("DB Client instanced Successfully")
        except Exception as e:
            logger.exception(e)
            logger.error(str(e))
            logger.error("Error. Could not instance DB Client Session")

    def _get_search_for_user(self):

        errors = []
        results = ''
        user_name = os.environ['USER_NAME_SEARCH']

        stmt = f"""
            SELECT 
                a.provider_name as "provider_name",
                a.url as "url",
                c.base_url as "base_url"
            FROM search_queries a 
                JOIN clients b ON a.client_id = b.client_id
                LEFT JOIN providers c ON a.provider_name = c.provider_name
            WHERE 
                b.name = :user_name
                AND a.enabled = true
                ORDER BY 1 asc  
            """

        results = self.ses.execute(text(stmt), {'user_name': user_name})

        if results.rowcount == 0 :
            errors.append(f"No search found for user: {user_name}")
            logger.error("No search found for user")
        
        return errors, results

    def _get_notifier_params_for_user(self):
        
        errors = []
        results = ''
        user_name = os.environ['USER_NAME_SEARCH']
        notifier_settings = {}

        stmt = f"""
            SELECT 
                a.chat_id,
                a.client_id,
                bot_token
            FROM clients a
                JOIN bots b ON a.bot_id = b.id
            WHERE a.name = :user_name
            """

        results = self.ses.execute(text(stmt), {'user_name': user_name})

        if results.rowcount == 0 :
            logger.error("No search found for user")

        results = results.fetchone()
        
        return results

    def run(self):
        
        provider = defaultdict(list)
        new_properties = []
        self.error = []

        errors, results = self._get_search_for_user()

        notifier_params = self._get_notifier_params_for_user()

        if errors:
            return self.error, new_properties

        if results:
            for row in results:
                tmpobj = {}

                tmpobj['base_url'] = row.base_url
                tmpobj['url'] = row.url
                
                provider[row.provider_name].append(tmpobj)

            for provider_name, provider_data in provider.items():
                
                try:
                    logging.info(f"Processing provider {provider_name}")
                    new_properties += process_properties(provider_name, provider_data, self.ses, self.db, notifier_params)
                except Exception as e:
                    logging.error(f"Error processing provider {provider_name}.\n{str(e)}")
                    self.error.append(f"Error processing provider {provider_name}.\n{str(e)}")
    
        return self.error, new_properties, notifier_params

