#!/usr/bin/env python
import asyncio
import logging
import yaml
import sys
from lib.notifier import Notifier
from providers.processor import process_properties
from router import Router

# logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def run():
    # configuration
    with open("configuration.yml", 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    disable_ssl = False
    if 'disable_ssl' in cfg:
        disable_ssl = cfg['disable_ssl']

    errors, new_properties, notifier_params = Router().run()

    logging.info(f"{notifier_params=}")

    notifier = Notifier.get_instance(cfg['notifier'], notifier_params, disable_ssl)

    if len(new_properties) > 0:
        asyncio.run(notifier.notify(new_properties))
    else:
        logging.info(f"No new properties to notify")
    
    if len(errors) > 0:
        logging.error(f"Following errors happened: {errors}")


if __name__ == "__main__":
    run()