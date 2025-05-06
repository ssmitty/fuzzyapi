import pandas as pd
from fuzzywuzzy import process, fuzz
import logging

def preprocess_name(name):
    """Remove common company suffixes, punctuation, and non-alphanumeric chars for better matching."""
    if not isinstance(name, str):
        return name
    import re
    name = name.lower()
    name = re.sub(r'[^a-z0-9 ]', '', name)  # Remove all non-alphanumeric except space
    suffixes = [
        ' inc', ' corporation', ' corp', ' ltd', ' llc', ' co',
        ' - common stock', '- common stock', ' common stock',
        ' incorporated', ' plc', ' group', ' holdings', ' company', ' companies', ' lp', ' ag', ' sa', ' nv', ' spa', ' srl', ' limited', ' the', ' and', ' of', ' dba', ' llp', ' pty', ' s p a', ' s a', ' inc', ' inc', ' inc', ' inc'
    ]
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    name = re.sub(r'\s+', ' ', name)  # Normalize whitespace
    return name.strip()

def load_data(filepath):
    """Load a CSV file into a DataFrame."""
    try:
        return pd.read_csv(filepath)
    except Exception as e:
        logging.error(f"Error loading data from {filepath}: {e}")
        raise

def load_public_companies(csv_path):
    """Load public companies from a CSV file."""
    try:
        return pd.read_csv(csv_path)
    except Exception as e:
        logging.error(f"Error loading public companies from {csv_path}: {e}")
        raise

def load_combined_dataset(csv_path):
    """Load the combined dataset for name matching."""
    try:
        return pd.read_csv(csv_path)
    except Exception as e:
        logging.error(f"Error loading combined dataset from {csv_path}: {e}")
        raise

def best_match(name, combined_df, tickers_df):
    """Fuzzy match name in combined dataset, then get ticker from tickers dataset."""
    try:
        if not isinstance(name, str):
            logging.warning(f"Input name is not a string: {name}")
            return None, None, None, None, None, 0, None
        # If not a string it returns none
        companies_list = combined_df['Name'].tolist()
        logging.info(f"Searching for: {name}")
        output = process.extractOne(name, companies_list)
        # Output holds the best match and the score
        if output and len(output) == 2:
            matched_name, score = output
            logging.info(f"Best match: {matched_name} with score: {score}")
            # If the score is below 90 it returns none
            if score <= 89:
                logging.info(f"Score {score} is below threshold of 90")
                return None, None, None, None, None, score, None

            matched_row = combined_df[combined_df['Name'] == matched_name]
            if matched_row.empty:
                logging.warning(f"Matched name {matched_name} not found in dataset")
                return matched_name, None, None, None, None, score, None
            # If the matched name is not found in the dataset it returns none
            matched_row = matched_row.iloc[0]
            state = matched_row['State']
            country = matched_row['Country']
            logging.info(f"Found state: {state}, country: {country}")
            # Preprocess matched_name and ticker_titles for better matching
            pre_matched_name = preprocess_name(matched_name)
            ticker_titles = tickers_df['title'].tolist()
            pre_ticker_titles = [preprocess_name(t) for t in ticker_titles]

            # Fuzzy match: get all tickers with a perfect score (100)
            ticker_matches = process.extract(pre_matched_name, pre_ticker_titles, scorer=fuzz.token_set_ratio)
            top_matches = [match for match, s in ticker_matches if s == 100]
            tickers = []
            if top_matches:
                for match in top_matches:
                    idxs = [i for i, t in enumerate(pre_ticker_titles) if t == match]
                    for idx in idxs:
                        ticker_row = tickers_df.iloc[[idx]]
                        ticker = ticker_row['ticker'].values[0] if not ticker_row.empty else None
                        if ticker:
                            tickers.append(ticker)
                # Remove duplicates, preserve order
                seen = set()
                tickers = [x for x in tickers if not (x in seen or seen.add(x))]
                predicted_ticker = tickers[0] if tickers else None
                logging.info(f"Perfect match tickers: {tickers}")
                return matched_name, predicted_ticker, tickers, state, country, score, 100
            else:
                # Fallback to previous logic: get the best match >= 90
                ticker_output = process.extractOne(pre_matched_name, pre_ticker_titles, scorer=fuzz.token_set_ratio)
                logging.info(f"Ticker output: {ticker_output}")
                if ticker_output and len(ticker_output) == 2:
                    ticker_match, ticker_score = ticker_output
                    logging.info(f"Found ticker match: {ticker_match} with score: {ticker_score}")
                    if ticker_score >= 90:
                        idx = pre_ticker_titles.index(ticker_match)
                        ticker_row = tickers_df.iloc[[idx]]
                        ticker = ticker_row['ticker'].values[0] if not ticker_row.empty else None
                        logging.info(f"Ticker found: {ticker}")
                        return matched_name, ticker, [ticker] if ticker else [], state, country, score, ticker_score
                    else:
                        logging.info(f"Ticker score {ticker_score} is below threshold of 90")
                        return matched_name, None, [], state, country, score, None
                else:
                    logging.warning(f"No ticker match found for {matched_name}")
                    return matched_name, None, [], state, country, score, None
        else:
            logging.warning(f"No match found for {name}")
            return None, None, None, None, None, 0, None
    except Exception as e:
        logging.error(f"Error in best_match for name '{name}': {e}")
        return None, None, None, None, None, 0, None
