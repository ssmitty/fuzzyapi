import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

import pandas as pd
import requests
import os

# URL for NASDAQ listed companies
NASDAQ_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
OTHER_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
OUTPUT_DIR = "supplemental_data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "company_tickers.csv")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


def download_and_clean(url, symbol_col, name_col):
    logging.info(f"Downloading {url}...")
    response = requests.get(url)
    response.raise_for_status()
    lines = response.text.splitlines()
    # Remove the last line if it's not data (footer)
    if lines[-1].startswith("File Creation Time"):  # NASDAQ puts a footer
        lines = lines[:-1]
    # Save to a temporary file for pandas
    temp_file = os.path.join(OUTPUT_DIR, "temp.txt")
    with open(temp_file, "w") as f:
        f.write("\n".join(lines))
    # Read with pandas
    df = pd.read_csv(temp_file, sep="|")
    # Keep only relevant columns
    df = df[[symbol_col, name_col]]
    df.columns = ["ticker", "title"]
    os.remove(temp_file)
    logging.info(f"Saved {len(df)} tickers to temp file")
    return df


def main():
    logging.info("Downloading NASDAQ...")
    nasdaq_df = download_and_clean(NASDAQ_URL, "Symbol", "Security Name")
    logging.info("Downloading NYSE/AMEX/others...")
    other_df = download_and_clean(OTHER_URL, "ACT Symbol", "Security Name")
    combined = pd.concat([nasdaq_df, other_df], ignore_index=True)
    combined = combined.drop_duplicates(subset=["ticker"])
    combined.to_csv(OUTPUT_FILE, index=False)
    logging.info(f"Saved {len(combined)} tickers to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
