import time
import json
from pathlib import Path
from selenium import webdriver
from key_words import KeywordManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TwitterScraper:
    def __init__(self, credentials_file):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("window-size=1200,10000")  # Set the default width and height
        self.driver = webdriver.Chrome(options=chrome_options)
        self.tweets = []
        self.trends = []
        self.credentials_file = credentials_file
        self.keyword_manager = KeywordManager()
        self.logged_in = False

    def login(self):
        if not self.logged_in:
            with open(self.credentials_file) as f:
                credentials = json.load(f)

            self.driver.get("https://x.com/login")
            time.sleep(3)

            email_field = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.NAME, "text"))
            )
            email_field.send_keys(credentials["email"])

            # Cliquer sur le bouton "Next"
            next_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Next']]"))
            )
            next_button.click()

            # Vérifier quel champ est présent après le premier clic
            try:
                username_field = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_element_located((By.NAME, "text"))  # Vérifie si le champ d'utilisateur est présent
                )
                username_field.send_keys(credentials["username"])

                # Cliquer à nouveau sur le bouton "Next"
                next_button_again = WebDriverWait(self.driver, 7).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Next']]"))
                )
                next_button_again.click()

                # Maintenant, chercher le champ de mot de passe
                password_field = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.NAME, "password"))
                )
                password_field.send_keys(credentials["password"])

                # Cliquer sur le bouton "Log in"
                login_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Log in']]"))
                )
                login_button.click()

            except Exception as e:
                # Si le champ d'utilisateur n'est pas présent, essayer le champ de mot de passe
                try:
                    password_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.NAME, "password"))
                    )
                    password_field.send_keys(credentials["password"])

                    # Cliquer sur le bouton "Log in"
                    login_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Log in']]"))
                    )
                    login_button.click()

                except Exception as e:
                    print("Erreur lors de l'authentification :", e)

            WebDriverWait(self.driver, 5).until(
                EC.url_contains("home")
            )
            # Navigate to the Explore section
            self.driver.get("https://x.com/explore")
            self.logged_in = True
        time.sleep(10)  # Wait for the results to load


    def perform_search(self, keyword):
        # free the previous search data
        self.tweets = []
        # Locate the search input field using XPath
        search_input = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@data-testid='SearchBox_Search_Input']"))
        )
        search_input.click()
        # Clear the input using Ctrl + A and Delete
        search_input.send_keys(Keys.CONTROL, 'a')  # Select all text
        search_input.send_keys(Keys.DELETE)  # Delete the selected text
        search_input.send_keys(keyword)
        search_input.send_keys(Keys.ENTER)

        # Notification
        print("Notification: search performed!\n")

        time.sleep(10)  # Wait for the results to load

    def get_trends(self):
        self.trends = []

        # Navigate to the Explore section
        self.driver.get("https://x.com/explore")

        # Cliquer sur l'onglet "Trending"
        trending_tab = WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//a[contains(@href, '/explore/tabs/trending')]"))
        )
        trending_tab.click()
        self.scroll_and_collect_trends()

        # Cliquer sur l'onglet "News"
        news_tab = WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//a[contains(@href, '/explore/tabs/news')]"))
        )
        news_tab.click()
        self.scroll_and_collect_trends()

        # Cliquer sur l'onglet "Sports"
        sports_tab = WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//a[contains(@href, '/explore/tabs/sports')]"))
        )
        sports_tab.click()
        self.scroll_and_collect_trends()

        # Cliquer sur l'onglet "Entertainment"
        entertainment_tab = WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//a[contains(@href, '/explore/tabs/entertainment')]"))
        )
        entertainment_tab.click()
        self.scroll_and_collect_trends()

    def scroll_and_collect_trends(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Collect visible trends using a more specific selector
            time.sleep(10)
            trend_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='trend']")
            for trend in trend_elements:
                trend_text = trend.text
                if trend_text and trend_text not in self.trends:
                    self.trends.append(trend_text)  # Collect only the text of the trend

            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for new content to load

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:  # Check if we reached the bottom
                break
            last_height = new_height


    def scroll_and_collect_tweets(self, scroll_pause_time=5, max_scrolls=20):
        # Scroll and collect tweets after the search
        for _ in range(max_scrolls):
            time.sleep(scroll_pause_time)
            tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, "article")
            for tweet in tweet_elements:
                tweet_text = tweet.text
                if tweet_text not in self.tweets:
                    self.tweets.append(tweet_text)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def close(self):
        self.driver.quit()

    def save_tweets(self, filename="tweets.json"):
        # Create the data_set directory if it doesn't exist
        data_set_path = Path("data_set")
        data_set_path.mkdir(exist_ok=True)

        # Save tweets to a temporary file in the data_set folder
        file_path = data_set_path / filename
        with file_path.open('w', encoding='utf-8') as f:
            json.dump(self.tweets, f, ensure_ascii=False, indent=4)


    def save_trends(self, filename="trends.json"):
        # Create the data_set directory if it doesn't exist
        data_set_path = Path("data_set")
        data_set_path.mkdir(exist_ok=True)

        # Save tweets to a temporary file in the data_set folder
        file_path = data_set_path / filename
        with file_path.open('w', encoding='utf-8') as f:
            json.dump(self.trends, f, ensure_ascii=False, indent=4)