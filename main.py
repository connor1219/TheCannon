import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import keyboard
import os
import time
import sqlite3
def main():
    options = ['Run Monitor','Exit']
    current_selection = 0
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
    conn.close()

    def clear_screen():
        # Clear the terminal screen
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_menu():
        clear_screen()
        print("Use arrow keys to navigate and Enter to select.\n")
        for index, option in enumerate(options):
            if index == current_selection:
                print(f"> {option}")  # hover option
            else:
                print(f"  {option}")

    def on_arrow_key(event):
        nonlocal current_selection
        if event.name == 'up':
            # Selection up
            current_selection = (current_selection - 1) % len(options)
        elif event.name == 'down':
            # Selection down
            current_selection = (current_selection + 1) % len(options)
        print_menu()

    def on_enter(event):
        clear_screen()
        print(f'\nYou selected "{options[current_selection]}".')
        if options[current_selection] == 'Exit':
            # this doesn't even print cause it just clears screen right after
            print("Work in progress")
        elif options[current_selection] == 'Run Monitor':
            monitor()
        clear_screen()
        print_menu()

    def setup_webhook(item):
        webhook_url = 'https://discord.com/api/webhooks/1235970598992216167/PiAaHRpjxGuu0RmY9XCBh9xGCgbKjy4s9plF5CaFQvZoaXn34PqmPtUTMl58BzC0a5lb'
        footer_icon_url = 'https://cdn.discordapp.com/attachments/1235970581720072202/1235980692689653872/corndog_white_bg.jpg?ex=66365838&is=663506b8&hm=e9a3b25dd133617cfbf512d46e92991b56bbaa8e06e8743c794fd2fe3eba5618&'

        image_url = item.find('img')['src']
        address = item.find('h2').find('a').text.strip()
        description = item.find('div', class_='description').text.strip()
        date_price_combo = item.find_all('dd')
        date = date_price_combo[0].text.strip()
        price = date_price_combo[2].text.strip()
        listing_url = item.find('h2').find('a')['href']
        check_and_insert_url(item)

        # Create the payload for the Discord message
        data = {
            "embeds": [
                {
                    "fields": [
                        {
                            "name": "Address",
                            "value": address,
                        },
                        {
                            "name": "Description",
                            "value": description
                        },
                        {
                            "name": "Price",
                            "value": price
                        },
                        {
                            "name": "Date Posted",
                            "value": date
                        }
                    ],
                    "title": "New Listing Uploaded!",
                    "description": f"[View Listing]({listing_url})",
                    "image": {
                        "url": image_url
                    },
                    "footer": {
                        "text": "Corndog Dev",
                        "icon_url": footer_icon_url
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
        }

        headers = {
            "Content-Type": "application/json"
        }

        # Sends webhook
        response = requests.post(webhook_url, headers=headers, data=json.dumps(data))

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
        # Fills database with all current listings
        # to avoid discord webhook spam on startup
        conn = sqlite3.connect('listings.db')
        cursor = conn.cursor()
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
        i = 0

        # Infinitely monitor for listings
        while True:
            print(f"Monitoring... ({i})")
            i+=1
            response = requests.get('https://thecannon.ca/housing/')
            soup = BeautifulSoup(response.text, 'html.parser')
            house_listing = soup.find_all('li', class_='housing-item')
            check_and_insert_url(house_listing)
            # Delay to stop ip bans or flags
            # Speed isn't a major concern given the nature of the scraped site
            time.sleep(30)

    # Create listeners
    keyboard.on_press_key("up", on_arrow_key)
    keyboard.on_press_key("down", on_arrow_key)
    keyboard.on_press_key("enter", on_enter, suppress=True)

    print_menu()

    # Start the event loop
    while True:
        keyboard.wait()

    # Close listeners
    keyboard.unhook_all()

main()
