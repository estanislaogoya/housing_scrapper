import telegram
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables (if needed)
load_dotenv()

# Create a bot instance with the token
bot = telegram.Bot(token='6997354603:AAFwdF7fWeKlxNioezzVMTYfpnPQZ24coQk')

async def get_updates():
    # Get updates using the bot instance
    updates = await bot.get_updates()
    return updates

async def main():
    updates = await get_updates()
    # Process updates and print chat IDs
    print([u.message.chat.id for u in updates if u.message])

# Run the main function using asyncio
if __name__ == "__main__":
    asyncio.run(main())
