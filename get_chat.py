import telegram
from dotenv import load_dotenv
import os

load_dotenv()

bot = telegram.Bot(token=os.environ['TELEGRAM_TOKEN'])
print([u.message.chat.id for u in bot.getUpdates()])