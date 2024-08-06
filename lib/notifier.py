import telegram
import logging
import random
import os

class NullNotifier:
    def notify(self, properties):
        pass

class Notifier(NullNotifier):
    def __init__(self, config, notifier_params, disable_ssl):

        self.telegram_token = notifier_params.bot_token
        self.telegram_chat_id = notifier_params.chat_id

        logging.info(f"Setting up bot with token {self.telegram_token}")
        self.config = config
        if disable_ssl:
            self.bot = telegram.Bot(token=self.telegram_token)
        else:
            self.bot = telegram.Bot(token=self.telegram_token)

    def escape_markdown_v2(self, text):
        escape_chars = r'_*[]()~>`#+-=|{}.!'
        return ''.join(f'\\{char}' if char in escape_chars else char for char in text)


    async def notify(self, properties):
        logging.info(f'Notifying about {len(properties)} properties')
        text = random.choice(self.config['messages'])
        await self.bot.send_message(chat_id=self.telegram_chat_id, text=text)

        for prop in properties:
            logging.info(f"Notifying about {prop['url']}")
            escaped_title = self.escape_markdown_v2(prop['title'])
            escaped_url = self.escape_markdown_v2(prop['url'])
            await self.bot.send_message(chat_id=self.telegram_chat_id, 
                    text=f"[{escaped_title}]({escaped_url})",
                    parse_mode='MarkdownV2')

    async def test(self, message):
        await self.bot.send_message(chat_id=self.telegram_chat_id, text=message)

    @staticmethod
    def get_instance(config, notifier_params, disable_ssl=False):
        if config['enabled']:
            return Notifier(config, notifier_params, disable_ssl)
        else:
            return NullNotifier()