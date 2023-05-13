# farma_bot
Project using telegram BOT with telethon library for scraping data from various websites

To use the envirement variables create ".env" file in the root directory.

You can scrap whatever you want and the bot will manage and send a excel file with the data as result.

If you want to create a Telegram Bot string session, use this:

````
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
````

> with TelegramClient(StringSession(), FARMABOT_TELEGRAM_API_ID, FARMABOT_TELEGRAM_API_HASH) as client:
    print(client.session.save())