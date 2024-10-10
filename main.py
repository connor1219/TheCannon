import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import sqlite3
from discord import Embed, SyncWebhook


def main():
    f = open("webhookurl.txt", "r")
    webhook_url = f.read()

    def setup_webhook(item):
        footer_icon_url = ('https://cdn.discordapp.com/attachments/1235970581720072202/1235980692689653872'
                           '/corndog_white_bg.jpg?ex=66365838&is=663506b8&hm'
                           '=e9a3b25dd133617cfbf512d46e92991b56bbaa8e06e8743c794fd2fe3eba5618&')
        image_url = item.find('img')['src']
        address = item.find('h2').find('a').text.strip()
        description = item.find('div', class_='description').text.strip()
        date_price_combo = item.find_all('dd')
        date = date_price_combo[0].text.strip()
        price = date_price_combo[2].text.strip()
        listing_url = item.find('h2').find('a')['href']

        # Create an Embed
        embed = Embed(
            title="New Listing Uploaded!",
            description=f"[View Listing]({listing_url})",
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Address", value=address, inline=False)
        embed.add_field(name="Description", value=description, inline=False)
        embed.add_field(name="Price", value=price, inline=False)
        embed.add_field(name="Date Posted", value=date, inline=False)

        # Set the image and footer
        embed.set_image(url=image_url)
        embed.set_footer(text="Corndog Dev", icon_url=footer_icon_url)

        # Initialize the webhook
        webhook = SyncWebhook.from_url(webhook_url)

        # Send the embed via the webhook
        webhook.send(embed=embed)

    def check_and_insert_url(house_listing):
        conn = sqlite3.connect('listings.db')
        cursor = conn.cursor()

        # Iterate through all listings checking if any are not in the database already
        for item in house_listing:
            listing_url = item.find('h2').find('a')['href']
            # Check if the URL already exists in the database
            cursor.execute('SELECT url FROM listings WHERE url = ?', (listing_url,))
            exists = cursor.fetchone()

            if not exists:
                # Adds new URL into the database
                cursor.execute('INSERT INTO listings (url) VALUES (?)', (listing_url,))
                conn.commit()
                # Setup and Send Webhook
                setup_webhook(item)
        conn.close()

    def init_database(house_listing):
        # Creates / Purges and then Fills database with all current listings
        # to avoid discord webhook spam on startup
        conn = sqlite3.connect('listings.db')
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS listings')
        cursor.execute('''
            CREATE TABLE listings (
                url TEXT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''')
        conn.commit()
        for item in house_listing:
            listing_url = item.find('h2').find('a')['href']
            cursor.execute('INSERT INTO listings (url) VALUES (?)', (listing_url,))
            conn.commit()
        conn.close()

    def monitor():
        # Send request to get html
        response = requests.get('https://thecannon.ca/housing/')
        # Parse html
        soup = BeautifulSoup(response.text, 'html.parser')
        # Grabs all the individual listings
        house_listing = soup.find_all('li', class_='housing-item')
        # Set up DB
        init_database(house_listing)
        counter = 0

        # Infinitely monitor for listings
        while True:
            print(f"Monitoring... ({counter})")
            counter += 1
            response = requests.get('https://thecannon.ca/housing/')
            soup = BeautifulSoup(response.text, 'html.parser')
            house_listing = soup.find_all('li', class_='housing-item')
            check_and_insert_url(house_listing)
            # Delay to stop ip bans or flags
            # Speed isn't a major concern given the nature of the scraped site
            time.sleep(30)

    # def set_webhook():
    #    # fixes bug where enter from selecting carries over to the input
    #    input("")
    #    main.webhookurl = input("Enter your desired discord webhook URL: ")
    #    f = open("webhookurl.txt", "w")
    #    f.write(main.webhookurl)

    monitor()


main()
