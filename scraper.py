import argparse
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
import re
import schedule
from datetime import datetime, timedelta
import time
from typing import List, Dict


# Global constant for cookies
COOKIES: List[Dict[str, str]] = [
    {"name": "guest_id_marketing", "value": "v1%3A171450094067160934"},
    {"name": "guest_id_ads", "value": "v1%3A171450094067160934"},
    {"name": "guest_id", "value": "v1%3A171450094067160934"},
    {"name": "gt", "value": "1785372464010195183"},
    {"name": "_ga", "value": "GA1.2.892000168.1714500942"},
    {"name": "_gid", "value": "GA1.2.17130126.1714500942"},
    {"name": "_twitter_sess", "value": "BAh7CSIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCBI6ODCPAToMY3NyZl9p%250AZCIlYjI0MzBlOTI5MDg2NGEzZDY5YzU4N2M4MTZiMGVhYzE6B2lkIiVmZjk2%250AMjRhMzhmNmJjYmEyZWU3Y2ZmZjZhOTg1YWNkOA%253D%253D--557249aeb8cbbb5a3c3178b5bd812a0378d3a398"},
    {"name": "kdt", "value": "DSRs8PsvrOSWz2EFS2MAXsSHyt8gNEdHxd7D9Myz"},
    {"name": "auth_token", "value": "48b5f6160821c0d94bdbe69a2b252f70a665d705"},
    {"name": "ct0", "value": "8619b3da96fcf3238af9584f0c48b21b3fb5c62f17997444ee6467670a09a1c4a1d064348bdaa1aef0a93891f30fff2b35ca7e7cede664540db70ed1c40b5a84af781c61ef521c6b39d396013d4ffb02"},
    {"name": "twid", "value": "u%3D1785368119290003456"},
    {"name": "att", "value": "1-6bqx3USx08n1upken3fzUGuKjkKSA5SfAERNc4bK"},
    {"name": "personalization_id", "value": '"v1_/x50LhWZxyQ667sFp/NCFA=="'},
]


def is_within_scraping_interval(time_str: str, scraping_interval_minutes: int) -> bool:
    """
    Check if the given time string is within the past X minutes.

    Args:
        time_str: A string representing the time in ISO format.
        scraping_interval_minutes: An integer representing the interval in minutes.

    Returns:
        A boolean value indicating whether the time difference is within the specified interval.
    """
    # Convert the time string to a datetime object
    input_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))

    # Get the current time
    current_time = datetime.now(input_time.tzinfo)

    # Calculate the time difference
    time_difference = current_time - input_time

    # Check if the time difference is within the past X minutes
    return time_difference <= timedelta(minutes=scraping_interval_minutes)


def get_driver_ready_for_twitter(cookies: List[Dict[str, str]]) -> webdriver.Chrome:
    """
    Initialize a Chrome WebDriver instance with specified cookies for Twitter scraping.

    Args:
        cookies: A list of dictionaries representing cookies to be added to the WebDriver.

    Returns:
        A Chrome WebDriver instance ready for Twitter scraping.
    """
    # Define Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    # Add more options here if needed

    # Define paths
    user_home_dir = os.path.expanduser("~")
    chrome_binary_path = os.path.join(user_home_dir, "chrome-linux64", "chrome")
    chromedriver_path = os.path.join(user_home_dir, "chromedriver-linux64", "chromedriver")

    # Set binary location and service
    chrome_options.binary_location = chrome_binary_path
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get('https://twitter.com/')
    time.sleep(1)

    # Add cookies to the WebDriver
    for cookie in cookies:
        driver.add_cookie(cookie)

    return driver


def get_ocurr_count_from_twitter_account(driver: WebDriver, account_url: str, ticker: str, scraping_interval: int) -> int:
    """
    Scrape the specified Twitter account for the number of occurrences of a stock symbol.

    Args:
        driver: WebDriver instance for interacting with the web page.
        account_url: URL of the Twitter account to scrape.
        ticker: The specific stock symbol to be counted.
        scraping_interval: The time interval for the scraping session.

    Returns:
        The count of occurrences of the specified stock symbol in the tweets.
    """
    # Fetch the Twitter page
    driver.get(account_url)
    time.sleep(5)

    # Extract tweet texts
    tweets = driver.find_elements(By.XPATH, "//article[contains(@data-testid, 'tweet')]")
    
    # Initialize count
    count = 0
    
    # Loop through tweets and count mentions of stock symbol
    for tweet in tweets:
        tweet_publish_time = tweet.find_element(By.TAG_NAME, "time").get_attribute('datetime')
        if is_within_scraping_interval(tweet_publish_time, scraping_interval):
            tweet_text = tweet.find_element(By.XPATH, "//div[contains(@data-testid, 'tweetText')]").text
            # Use regular expression to find stock symbol mentions
            mentions = re.findall(r'\$[A-Za-z]{3,4}', tweet_text)
            for mention in mentions:
                if mention.lower() == ticker.lower():
                    count += 1
    
    return count

    
def scrape_all_accounts(twitter_accounts: List[str], ticker: str, scraping_interval: int) -> None:
    """
    Scrape multiple Twitter accounts for the number of occurrences of a stock symbol and print the total count.

    Args:
        twitter_accounts: List of URLs of the Twitter accounts to scrape.
        ticker: The specific stock symbol to be counted.
        scraping_interval: The time interval for the scraping session.

    Returns:
        None
    """
    driver = get_driver_ready_for_twitter(COOKIES)
    final_count = 0
    for url in twitter_accounts:
        final_count += get_ocurr_count_from_twitter_account(driver, url, ticker, scraping_interval)
    
    driver.quit()

    print(f"'{ticker}' was mentioned '{final_count}' times in the last '{scraping_interval}' minutes.")


def main() -> None:
    """
    Main function to scrape Twitter accounts for the number of occurrences of a stock symbol.

    Args:
        None

    Returns:
        None
    """
    parser = argparse.ArgumentParser(description='Scrapes the Twitter accounts for the number of occurrences of a stock symbol.')
    parser.add_argument('--accounts_file', help='Path to a .txt file that includes the list of accounts to be scraped each in a separate line.')
    parser.add_argument('--ticker', help='The specific stock symbol to be counted by the script.')
    parser.add_argument('--interval', help='The time interval for another scraping session.')
    args = parser.parse_args()

    with open(args.accounts_file, 'r') as file:
        twitter_accounts = file.readlines()

    ticker = args.ticker.upper()
    scraping_interval = int(args.interval)

    scrape_all_accounts(twitter_accounts, ticker, scraping_interval)

    # Schedule scraping function to run every X minutes
    schedule.every(scraping_interval).minutes.do(scrape_all_accounts, twitter_accounts=twitter_accounts, ticker=ticker, scraping_interval=scraping_interval)
    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
