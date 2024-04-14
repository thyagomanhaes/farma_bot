# farma_bot
Web scraping project using asynchronous way to collect data from two pharmacy-related websites

# Set up

- Create a virtual envirement with python -m venv env
- execute the command pip install -r requirements to install the libs needed to run the project

To use the mecofarma bot, just run the "scraper_mecofarma.py" in mecofarma folder.

To use the AppySaude bot, just run the "scraper_appysaude.py" in appysaude folder.

# Telegram bot

To use the telegram bot, you need to create a ".env" file in the root directory.

- FARMABOT_STRING_SESSION_BOT=
- FARMABOT_TELEGRAM_API_ID=
- FARMABOT_TELEGRAM_API_HASH=
- FARMABOT_BOT_TOKEN=

In mecofarma , you can choose to scrap between the entire website or send a excel file with the items you want.


If you want to create a Telegram Bot string session, use this:

````
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
````

> with TelegramClient(StringSession(), FARMABOT_TELEGRAM_API_ID, FARMABOT_TELEGRAM_API_HASH) as client:
    print(client.session.save())

The files will be stored in the folder called "files" and you can schedule the execution of scrapers using crontab for Linux for example.

