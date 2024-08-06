import logging
import sqlite3
from providers.zonaprop import Zonaprop
from providers.argenprop import Argenprop
from providers.mercadolibre import Mercadolibre
from providers.properati import Properati
from providers.inmobusqueda import Inmobusqueda
from providers.dixon import Dixon
from termcolor import colored
from utils.db_client import PostgresDbClient
from models.properties import Property
from sqlalchemy import text
from sqlalchemy.orm import Session
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

def register_property(ses, prop, notifier_params):
    
    try:
        new_prop = Property(
                internal_id = prop['internal_id'],
                provider = prop['provider'],
                url = prop['url'],
                captured_date = datetime.datetime.now(),
                client_id = notifier_params.client_id,
                )
        
        ses.add(new_prop)

        ses.commit()
        # logging.info(
        #             f"Successfully inserted query"
        #         )
    except Exception as e:
        ses.rollback()
        logging.error(
            f"Failed query execution..{e}"
        )
    


def process_properties(provider_name, provider_data, ses, db, notifier_params):
    provider = get_instance(provider_name, provider_data)

    new_properties = []
    properties = {}

    with ses:
        for prop in provider.next_prop():

            provider_key = prop['provider']

            if provider_key not in properties:
                properties[provider_key] = {'processed': [], 'new': []}

            properties[provider_key]['processed'].append(prop['internal_id'])

                # Check to see if we know it
            stmt = f"SELECT * FROM properties WHERE internal_id='{prop['internal_id']}' AND provider='{provider_key}' AND client_id = {notifier_params.client_id}"

            results = db.execute(stmt)

            if results.rowcount == 0 or results.rowcount is None:
                properties[provider_key]['new'].append(prop['internal_id'])
                register_property(ses, prop, notifier_params)
                new_properties.append(prop)
            
    logging.info(f"{provider_name} | New: {colored(len(properties[provider_key]['new']), 'green')} | Processed: {len(properties[provider_key]['processed'])}")
                    
    return new_properties

def get_instance(provider_name, provider_data):
    if provider_name == 'zonaprop':
        return Zonaprop(provider_name, provider_data)
    elif provider_name == 'argenprop':
        return Argenprop(provider_name, provider_data)
    elif provider_name == 'mercadolibre':
        return Mercadolibre(provider_name, provider_data)
    elif provider_name == 'properati':
        return Properati(provider_name, provider_data)
    elif provider_name == 'inmobusqueda':
        return Inmobusqueda(provider_name, provider_data)
    elif provider_name == 'dixon':
        return Dixon(provider_name, provider_data)
    else:
        raise Exception('Unrecognized provider')
