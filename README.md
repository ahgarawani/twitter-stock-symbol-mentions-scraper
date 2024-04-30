# Twitter Stock Symbol Mentions Scraper

This script allows you to scrape Twitter accounts for the number of occurrences of a specific stock symbol within a given time interval.

## Installation

1. Clone the repository.
2. Install the required dependencies by running `pip install -r requirements.txt`.

## Usage

1. Make sure you have the necessary Chrome browser and ChromeDriver installed.
2. Modify the `COOKIES` list in the script with your desired cookies for Twitter.
3. Prepare a text file containing the URLs of the Twitter accounts you want to scrape, with each URL on a separate line.
4. Run the script with the following command:

   ```bash
   python script.py --accounts_file <path_to_accounts_file> --ticker <stock_symbol> --interval <scraping_interval>
   ```

   Replace <path_to_accounts_file> with the path to your text file containing Twitter account URLs, <stock_symbol> with the specific stock symbol you want to count mentions for, and <scraping_interval> with the time interval for the scraping session in minutes.

   The script will print the total count of mentions of the specified stock symbol in the last scraping interval and will continue to scrape periodically according to the specified interval.

## Example

```bash
python script.py --accounts_file 'accounts.txt' --ticker '$AAPL' --interval '15'
```

This command will scrape the Twitter accounts listed in accounts.txt for mentions of the stock symbol "AAPL" every 15 minutes.
