# TheCannon Web Scraper

A Python web scraper that monitors TheCannon rental marketplace for new housing listings and sends real-time Discord notifications.

## Features

- **Real-time monitoring** of TheCannon.ca housing listings
- **Discord webhook integration** for instant notifications
- **SQLite database** to track processed listings and prevent duplicates
- **Rich embed notifications** with listing details, images, and direct links
- **Automatic rate limiting** to prevent IP bans

## How It Works

The scraper continuously monitors the TheCannon housing page, parsing new listings and storing them in a local SQLite database. When a new listing is detected, it automatically sends a formatted Discord embed with:

- Property address and description
- Rental price and posting date
- Property image
- Direct link to the full listing

## Installation

1. Ensure Python 3.x is installed on your system
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `webhookurl.txt` file in the project root containing your Discord webhook URL

## Usage

Simply run the main script:

```bash
python main.py
```

The scraper will:
1. Initialize the database with current listings (to prevent spam on startup)
2. Begin monitoring for new listings every 30 seconds
3. Send Discord notifications for any new properties found

## Configuration

- **Webhook URL**: Place your Discord webhook URL in `webhookurl.txt`
- **Monitoring interval**: Currently set to 30 seconds (configurable in code)
- **Database**: SQLite database (`listings.db`) is created automatically

## Database Schema

The scraper maintains a simple SQLite database with the following structure:

```sql
CREATE TABLE listings (
    url TEXT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

## Dependencies

- `requests` - HTTP requests to TheCannon website
- `beautifulsoup4` - HTML parsing and data extraction
- `discord.py` - Discord webhook integration
- `sqlite3` - Database operations (built-in)
