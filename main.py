import sys
import time
import signal
from scraper import TwitterScraper
from tweet_to_json import structure_tweets

def signal_handler(sig, frame):
    print("\nExiting gracefully...")
    scraper.close()
    sys.exit(0)

if __name__ == "__main__":
    scraper = TwitterScraper('credentials.json')

    try:
        scraper.login()
    except Exception as e:
        print(e)

    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C

    while True:
        # keyword = scraper.keyword_manager.get_keyword()  # Get the keyword from the user
        # scraper.keyword_manager.store_keyword(keyword)  # Store the keyword in the JSON file

        # scraper.perform_search(keyword)  # Perform the search with the keyword
        # scraper.scroll_and_collect_tweets()  # Scroll and collect tweets based on the search

        # scraper.save_tweets("tweets.json")  # Changed filename for consistency

        scraper.get_trends()

        scraper.save_trends("trends.json")

        time.sleep(10)  # Wait for the results to load

        # structure_tweets(keyword)
