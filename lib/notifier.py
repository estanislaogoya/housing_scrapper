import telegram
import logging
import random
import os

load_dotenv()

class NullNotifier:
    def notify(self, properties):
        pass

class Notifier(NullNotifier):
    def __init__(self, config, disable_ssl):
        logging.info(f"Setting up bot with token {config['token']}")
        self.config = config
        if disable_ssl:
            self.bot = telegram.Bot(token=os.environ['TELEGRAM_TOKEN'])
        else:
            self.bot = telegram.Bot(token=os.environ['TELEGRAM_TOKEN'])

    def escape_markdown_v2(self, text):
        escape_chars = r'_*[]()~>`#+-=|{}.!'
        return ''.join(f'\\{char}' if char in escape_chars else char for char in text)


    async def notify(self, properties):
        logging.info(f'Notifying about {len(properties)} properties')
        text = random.choice(self.config['messages'])
        await self.bot.send_message(chat_id=os.environ['TELEGRAM_CHAT_ID'], text=text)

        for prop in properties:
            logging.info(f"Notifying about {prop['url']}")
            escaped_title = self.escape_markdown_v2(prop['title'])
            escaped_url = self.escape_markdown_v2(prop['url'])
            await self.bot.send_message(chat_id=os.environ['TELEGRAM_CHAT_ID'], 
                    text=f"[{escaped_title}]({escaped_url})",
                    parse_mode='MarkdownV2')

    async def test(self, message):
        await self.bot.send_message(chat_id=os.environ['TELEGRAM_CHAT_ID'], text=message)

    @staticmethod
    def get_instance(config, disable_ssl=False):
        if config['enabled']:
            return Notifier(config, disable_ssl)
        else:
            return NullNotifier()
